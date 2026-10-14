#!/usr/bin/env python3
"""tenet guard: PreToolUse hook that denies clearly destructive actions and asks on risky ones.

Reads the hook JSON from stdin and prints a `hookSpecificOutput` decision, or nothing.
It never blocks on its own failures (fail-open): a broken guard must not brick every tool.
Messages cite rule ids only, never the command or file contents, so secrets are not echoed.
"""
import json
import os
import re
import shlex
import sys

POLICY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "policy.json")
COMMAND_TOOLS = {"Bash", "PowerShell"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
FILE_TOOLS = WRITE_TOOLS | {"Read"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")
ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
WRAPPERS = {"sudo", "doas", "command", "builtin", "exec", "nohup", "time", "env"}


def warn(message):
    sys.stderr.write("tenet guard: %s\n" % message)


def load_policy(path=POLICY_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def tokens_of(segment):
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def strip_prefix(tokens):
    """Drop env assignments and wrappers (sudo, env, ...) to find the real program."""
    index = 0
    while index < len(tokens) and (ENV_ASSIGN.match(tokens[index]) or tokens[index] in WRAPPERS):
        index += 1
    return tokens[index:]


def program_name(token):
    name = re.split(r"[\\/]", token)[-1]
    return re.sub(r"\.exe$", "", name, flags=re.IGNORECASE)


def segments(command):
    return [part.strip() for part in SEGMENT_SPLIT.split(command) if part.strip()]


def normalize_target(target):
    value = target.replace("\\", "/")
    if len(value) > 1 and value.endswith("/") and not value.endswith(":/"):
        value = value.rstrip("/") or "/"
    return value


def is_dangerous_rm(command, policy):
    targets = {normalize_target(t).lower() for t in policy["dangerous_rm_targets"]}
    targets |= {t + "/" for t in targets if not t.endswith("/")}
    for segment in segments(command):
        tokens = strip_prefix(tokens_of(segment))
        if not tokens or program_name(tokens[0]) != "rm":
            continue
        flags = [t for t in tokens[1:] if t.startswith("-")]
        recursive = any(f in ("--recursive", "-r", "-R") or (not f.startswith("--") and re.search("[rR]", f)) for f in flags)
        if not recursive:
            continue
        for operand in (t for t in tokens[1:] if not t.startswith("-")):
            if normalize_target(operand).lower() in targets:
                return True
    return False


def match_command_rules(command, policy, decision):
    for rule in policy["command_rules"]:
        if rule["decision"] == decision and re.search(rule["pattern"], command, re.IGNORECASE):
            return rule
    return None


def agent_role(payload):
    agent = payload.get("agent_type") or ""
    return agent.split(":")[-1].strip().lower()


def readonly_violation(command, policy):
    """Return True when a reviewer command is not provably read-only."""
    for pattern in policy["readonly_forbidden_patterns"]:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    allowed = {c.lower() for c in policy["readonly_commands"]}
    git_ok = set(policy["readonly_git_subcommands"])
    git_list_only = policy["readonly_git_list_only"]
    for segment in segments(command):
        tokens = strip_prefix(tokens_of(segment))
        if not tokens:
            continue
        program = program_name(tokens[0]).lower()
        if program == "git":
            args = tokens[1:]
            while args and args[0] in ("-C", "-c", "--no-pager", "-P"):
                args = args[2:] if args[0] in ("-C", "-c") else args[1:]
            if not args:
                return True
            sub, rest = args[0], args[1:]
            if sub in git_ok:
                continue
            if sub in git_list_only and (not rest or rest[0] in git_list_only[sub]):
                continue
            return True
        if program not in allowed:
            return True
    return False


def check_command(payload, policy):
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return None
    if is_dangerous_rm(command, policy):
        return ("deny", "deny-rm-root", "Recursive deletion of root, home or a drive.")
    rule = match_command_rules(command, policy, "deny")
    if rule:
        return ("deny", rule["id"], rule["reason"])
    if agent_role(payload) in policy["readonly_agents"] and readonly_violation(command, policy):
        return ("deny", "deny-reviewer-write", "Reviewer agents may only run read-only commands.")
    rule = match_command_rules(command, policy, "ask")
    if rule:
        return ("ask", rule["id"], rule["reason"])
    return None


def check_file(payload, policy):
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        return None
    norm = path.replace("\\", "/")
    name = norm.rsplit("/", 1)[-1]
    secrets = policy["secret_files"]
    is_write = payload.get("tool_name") in WRITE_TOOLS

    def any_match(patterns, value):
        return any(re.search(p, value, re.IGNORECASE) for p in patterns)

    excepted = any_match(secrets["name_exceptions"], name)
    if is_write and not excepted and (any_match(secrets["private_key_patterns"], name) or any_match(secrets["private_key_patterns"], norm)):
        return ("deny", "deny-private-key-write", "Writing private key material is blocked.")
    if not excepted and (any_match(secrets["name_patterns"], name) or any_match(secrets["path_patterns"], norm)):
        return ("ask", "ask-secret-file", "This file may contain secrets.")
    if is_write and any_match(policy["global_config_files"], norm):
        return ("ask", "ask-global-config-file", "Editing user-level configuration needs explicit approval.")
    return None


def evaluate(payload, policy):
    tool = payload.get("tool_name")
    if tool in COMMAND_TOOLS:
        return check_command(payload, policy)
    if tool in FILE_TOOLS:
        return check_file(payload, policy)
    return None


def render(decision):
    kind, rule_id, reason = decision
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": kind,
            "permissionDecisionReason": "tenet guard [%s]: %s" % (rule_id, reason),
        }
    })


def main():
    try:
        payload = json.loads(sys.stdin.read())
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
    except ValueError:
        warn("invalid hook input; no decision")
        return 0
    try:
        policy = load_policy()
        decision = evaluate(payload, policy)
    except Exception as error:  # fail-open by design, see docs/security.md
        warn("internal error (%s); no decision" % type(error).__name__)
        return 0
    if decision:
        sys.stdout.write(render(decision) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
