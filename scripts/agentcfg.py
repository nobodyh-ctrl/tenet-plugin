#!/usr/bin/env python3
"""Install, uninstall, restore and inspect the forge complementary configuration.

What it manages (all tracked in an ownership manifest):
  * methodology rules  -> <config>/rules/forge/*.md
  * private profile    -> <config>/rules/forge/profile.md (created once, never overwritten)
  * --with-permissions -> forge ask/deny rules merged into <config>/settings.json
  * --with-plugin      -> `claude plugin marketplace add` + `claude plugin install` (user scope)
  * --with-engram      -> `claude mcp add --scope user engram -- <engram> mcp --tools=agent`

<config> is --config-dir, else $CLAUDE_CONFIG_DIR, else ~/.claude. Stdlib only.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

TOOL = "forge"
MARKETPLACE = "forge"
PLUGIN_ID = "forge@forge"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_SRC = os.path.join(REPO_ROOT, "global-config", "rules")
PROFILE_TEMPLATE = os.path.join(REPO_ROOT, "global-config", "templates", "profile.md")
RULES_REL = os.path.join("rules", TOOL)
PROFILE_REL = os.path.join(RULES_REL, "profile.md")
STATE_REL = TOOL
MANIFEST_REL = os.path.join(STATE_REL, "manifest.json")
BACKUPS_REL = os.path.join("backups", TOOL)
SETTINGS_REL = "settings.json"
# Second-layer rules; the forge guard hook is the primary control (docs/security.md).
PERMISSIONS = {
    "ask": [
        "Bash(git push *)",
        "Bash(terraform apply *)",
        "Bash(terraform destroy *)",
        "Bash(tofu apply *)",
        "Bash(tofu destroy *)",
        "Bash(kubectl delete *)",
        "Bash(npm install -g *)",
        "PowerShell(git push *)",
    ],
    "deny": [
        "Read(~/.ssh/**)",
        "Read(~/.aws/credentials)",
        "Edit(~/.ssh/**)",
    ],
}
OPENSPEC_INSTALL = "npm install -g @fission-ai/openspec@latest  (https://openspec.dev/docs/installation)"
ENGRAM_INSTALL = "https://github.com/Gentleman-Programming/engram/releases/latest"
CLAUDE_INSTALL = "https://code.claude.com/docs/en/setup"


class InstallError(Exception):
    """A condition that must abort before anything is written."""


# --- helpers ---------------------------------------------------------------------------------

def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_link(path):
    if os.path.islink(path):
        return True
    isjunction = getattr(os.path, "isjunction", None)
    return bool(isjunction and isjunction(path))


def atomic_write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp-" + TOOL
    with open(tmp, "wb") as handle:
        handle.write(data)
    os.replace(tmp, path)


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except ValueError as exc:
            raise InstallError("%s is not valid JSON (%s); fix or restore it first" % (path, exc))


def dump_json(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def resolve_config_dir(explicit):
    path = explicit or os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    path = os.path.abspath(os.path.expanduser(path))
    if os.path.lexists(path):
        if is_link(path):
            raise InstallError("config dir %s is a symlink or junction; refusing to write through it" % path)
        if not os.path.isdir(path):
            raise InstallError("config dir %s is not a directory" % path)
    elif not os.path.isdir(os.path.dirname(path)):
        raise InstallError("config dir %s does not exist and its parent is missing" % path)
    return path


def check_paths_safe(config, rels):
    for rel in rels:
        current = config
        for part in rel.split(os.sep):
            current = os.path.join(current, part)
            if os.path.lexists(current) and is_link(current):
                raise InstallError("%s is a symlink or junction; refusing to write through it" % current)


def which_first(candidates):
    for candidate in candidates:
        if not candidate:
            continue
        found = shutil.which(candidate) if os.sep not in candidate and "/" not in candidate else (candidate if os.path.isfile(candidate) else None)
        if found:
            return found
    return None


def find_claude(explicit=None):
    # "none" disables detection (used by tests to simulate a missing CLI).
    if "none" in (explicit, os.environ.get("FORGE_CLAUDE_BIN")):
        return None
    home = os.path.expanduser("~")
    return which_first([explicit, os.environ.get("FORGE_CLAUDE_BIN"), "claude",
                        os.path.join(home, ".local", "bin", "claude.exe"), os.path.join(home, ".local", "bin", "claude")])


def find_engram():
    if os.environ.get("FORGE_ENGRAM_BIN") == "none":
        return None
    home = os.path.expanduser("~")
    return which_first([os.environ.get("FORGE_ENGRAM_BIN"), "engram",
                        os.path.join(home, "AppData", "Local", "engram", "bin", "engram.exe"),
                        os.path.join(home, ".local", "bin", "engram"), os.path.join(home, "go", "bin", "engram")])


def command_for(binary):
    """Python scripts (used by tests as fake CLIs) run through the current interpreter."""
    return [sys.executable, binary] if binary.endswith(".py") else [binary]


def is_default_config(config):
    default = os.path.join(os.path.expanduser("~"), ".claude")
    return not os.environ.get("CLAUDE_CONFIG_DIR") and os.path.normcase(config) == os.path.normcase(default)


def run_cli(binary, args, config, check=True):
    # Setting CLAUDE_CONFIG_DIR, even to the default path, moves where the CLI keeps .claude.json,
    # so it is exported only for non-default config dirs.
    env = dict(os.environ)
    if not is_default_config(config):
        env["CLAUDE_CONFIG_DIR"] = config
    result = subprocess.run(command_for(binary) + args, capture_output=True, text=True, env=env, timeout=300)
    if check and result.returncode != 0:
        raise InstallError("`%s` failed: %s" % (" ".join(["claude"] + args[:3]), (result.stderr or result.stdout).strip()[:300]))
    return result


def tool_version(binary, args=("--version",)):
    try:
        out = subprocess.run(command_for(binary) + list(args), capture_output=True, text=True, timeout=30)
        return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr).strip() else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# --- plan model ------------------------------------------------------------------------------

class Plan:
    def __init__(self, config):
        self.config = config
        self.ops = []        # (action, rel_path, payload)
        self.cli = []        # (description, args)
        self.notes = []

    def add(self, action, rel, payload=None):
        self.ops.append((action, rel, payload))

    def changes(self):
        return [op for op in self.ops if op[0] not in ("keep",)]

    def show(self, title):
        print("%s (config: %s)" % (title, self.config))
        if not self.ops and not self.cli:
            print("  nothing to do")
        for action, rel, _ in self.ops:
            print("  %-8s %s" % (action, rel.replace(os.sep, "/")))
        for description, _ in self.cli:
            print("  %-8s %s" % ("run", description))
        for note in self.notes:
            print("  note     %s" % note)


class Backup:
    """Lazily created snapshot of every path touched in one run, restorable byte for byte."""

    def __init__(self, config, stamp):
        self.config = config
        self.stamp = stamp
        self.dir = os.path.join(config, BACKUPS_REL, stamp)
        self.index = []

    def save(self, rel):
        if any(entry["path"] == rel for entry in self.index):
            return
        source = os.path.join(self.config, rel)
        entry = {"path": rel.replace(os.sep, "/"), "existed": os.path.isfile(source)}
        if entry["existed"]:
            target = os.path.join(self.dir, "files", rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
        self.index.append(entry)
        atomic_write(os.path.join(self.dir, "index.json"), dump_json({"tool": TOOL, "created": self.stamp, "entries": self.index}))


def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")


# --- install ---------------------------------------------------------------------------------

def plan_install(config, manifest, args, claude):
    plan = Plan(config)
    owned = manifest.get("files", {})
    new_files = {}
    for name in sorted(os.listdir(RULES_SRC)):
        if not name.endswith(".md"):
            continue
        source = os.path.join(RULES_SRC, name)
        rel = os.path.join(RULES_REL, name)
        dest = os.path.join(config, rel)
        source_hash = sha256(source)
        new_files[rel.replace(os.sep, "/")] = source_hash
        if not os.path.exists(dest):
            plan.add("create", rel, source)
        elif sha256(dest) == source_hash:
            plan.add("keep", rel)
        elif rel.replace(os.sep, "/") in owned:
            plan.add("update", rel, source)
        else:
            raise InstallError("%s exists and is not owned by %s; move it away or remove it first" % (dest, TOOL))
    profile = os.path.join(config, PROFILE_REL)
    plan.add("keep" if os.path.exists(profile) else "create", PROFILE_REL, None if os.path.exists(profile) else PROFILE_TEMPLATE)

    added = {"ask": [], "deny": []}
    if args.with_permissions:
        settings = read_json(os.path.join(config, SETTINGS_REL), {})
        if not isinstance(settings, dict):
            raise InstallError("settings.json must contain a JSON object")
        existing = settings.get("permissions") or {}
        for kind in ("ask", "deny"):
            current = existing.get(kind) or []
            added[kind] = [rule for rule in PERMISSIONS[kind] if rule not in current]
        if added["ask"] or added["deny"]:
            plan.add("merge", SETTINGS_REL, added)
    previous = manifest.get("permissions", {"ask": [], "deny": []})
    owned_permissions = {k: sorted(set(previous.get(k, [])) | set(added[k])) for k in ("ask", "deny")}

    plugin_owned = manifest.get("plugin", False)
    if args.with_plugin:
        if not claude:
            plan.notes.append("claude CLI not found; run manually: claude plugin marketplace add %s && claude plugin install %s --scope user" % (REPO_ROOT, PLUGIN_ID))
        elif args.dry_run:
            # Even read-only CLI queries can create files in a fresh config dir, so dry runs skip them.
            plan.cli.append(("claude plugin marketplace add <repo>", None))
            plan.cli.append(("claude plugin install %s --scope user" % PLUGIN_ID, None))
            plan.notes.append("dry run: plugin detection skipped; the real run skips both commands if %s is already installed" % PLUGIN_ID)
        elif plugin_installed(claude, config):
            plan.notes.append("plugin %s already installed; left as is" % PLUGIN_ID)
        else:
            plan.cli.append(("claude plugin marketplace add <repo>", ["plugin", "marketplace", "add", REPO_ROOT]))
            plan.cli.append(("claude plugin install %s --scope user" % PLUGIN_ID, ["plugin", "install", PLUGIN_ID, "--scope", "user"]))
            plugin_owned = True

    engram_owned = manifest.get("engram_mcp", False)
    if args.with_engram:
        engram = find_engram()
        existing = mcp_entry(config, "engram")
        if not engram:
            plan.notes.append("engram binary not found; install it first: %s" % ENGRAM_INSTALL)
        elif existing is not None:
            if engram_owned:
                plan.notes.append("engram MCP entry already registered by %s" % TOOL)
            elif same_engram(existing, engram):
                plan.notes.append("engram MCP entry already present (not owned by %s); left as is" % TOOL)
            else:
                plan.notes.append("CONFLICT: an engram MCP entry with a different command exists; left untouched")
        elif not claude:
            plan.notes.append("claude CLI not found; run manually: claude mcp add --scope user engram -- \"%s\" mcp --tools=agent" % engram)
        else:
            plan.cli.append(("claude mcp add --scope user engram -- <engram> mcp --tools=agent",
                             ["mcp", "add", "--scope", "user", "engram", "--", engram, "mcp", "--tools=agent"]))
            engram_owned = True

    new_manifest = {
        "tool": TOOL,
        "version": plugin_version(),
        "files": new_files,
        "profile": PROFILE_REL.replace(os.sep, "/"),
        "permissions": owned_permissions,
        "plugin": plugin_owned,
        "engram_mcp": engram_owned,
    }
    return plan, new_manifest


def apply_install(plan, manifest_before, manifest_after, claude):
    config = plan.config
    manifest_changed = {k: v for k, v in manifest_after.items()} != {k: v for k, v in manifest_before.items() if k != "installed_at"}
    if not plan.changes() and not plan.cli and not manifest_changed:
        print("install: already up to date; nothing written")
        return None
    backup = Backup(config, timestamp())
    for action, rel, payload in plan.ops:
        dest = os.path.join(config, rel)
        if action in ("create", "update"):
            backup.save(rel)
            with open(payload, "rb") as handle:
                atomic_write(dest, handle.read())
        elif action == "merge":
            backup.save(rel)
            settings = read_json(dest, {})
            permissions = settings.setdefault("permissions", {})
            for kind in ("ask", "deny"):
                if payload[kind]:
                    permissions.setdefault(kind, []).extend(payload[kind])
            atomic_write(dest, dump_json(settings))
    backup.save(MANIFEST_REL)
    manifest_after["installed_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    atomic_write(os.path.join(config, MANIFEST_REL), dump_json(manifest_after))
    for description, args in plan.cli:
        print("running: %s" % description)
        run_cli(claude, args, config)
    print("install: done. backup id: %s" % backup.stamp)
    return backup.stamp


# --- uninstall -------------------------------------------------------------------------------

def plan_uninstall(config, manifest, args, claude):
    plan = Plan(config)
    if not manifest:
        plan.notes.append("no %s manifest found; nothing owned to remove" % TOOL)
        return plan
    for rel in sorted(manifest.get("files", {})):
        dest = os.path.join(config, rel)
        if os.path.isfile(dest):
            plan.add("delete" if sha256(dest) == manifest["files"][rel] else "delete*", rel)
    profile = os.path.join(config, manifest.get("profile", PROFILE_REL))
    if os.path.isfile(profile):
        if args.purge:
            plan.add("delete", manifest.get("profile", PROFILE_REL))
        else:
            plan.notes.append("profile kept: %s (use --purge to remove)" % profile)
    owned = manifest.get("permissions", {})
    if owned.get("ask") or owned.get("deny"):
        settings = read_json(os.path.join(config, SETTINGS_REL), {})
        present = {k: [r for r in owned.get(k, []) if r in ((settings.get("permissions") or {}).get(k) or [])] for k in ("ask", "deny")}
        if present["ask"] or present["deny"]:
            plan.add("unmerge", SETTINGS_REL, present)
    if manifest.get("plugin"):
        if claude:
            plan.cli.append(("claude plugin uninstall %s --scope user" % PLUGIN_ID, ["plugin", "uninstall", PLUGIN_ID, "--scope", "user"]))
            plan.cli.append(("claude plugin marketplace remove %s" % MARKETPLACE, ["plugin", "marketplace", "remove", MARKETPLACE]))
        else:
            plan.notes.append("claude CLI not found; run: claude plugin uninstall %s --scope user && claude plugin marketplace remove %s" % (PLUGIN_ID, MARKETPLACE))
    if manifest.get("engram_mcp"):
        if claude:
            plan.cli.append(("claude mcp remove engram --scope user", ["mcp", "remove", "engram", "--scope", "user"]))
        else:
            plan.notes.append("claude CLI not found; run: claude mcp remove engram --scope user")
    plan.add("delete", MANIFEST_REL)
    return plan


def apply_uninstall(plan, claude):
    config = plan.config
    backup = Backup(config, timestamp())
    for action, rel, payload in plan.ops:
        dest = os.path.join(config, rel)
        backup.save(rel)
        if action.startswith("delete") and os.path.isfile(dest):
            os.remove(dest)
        elif action == "unmerge":
            settings = read_json(dest, {})
            permissions = settings.get("permissions") or {}
            for kind in ("ask", "deny"):
                if kind in permissions:
                    permissions[kind] = [r for r in permissions[kind] if r not in payload[kind]]
                    if not permissions[kind]:
                        del permissions[kind]
            if "permissions" in settings and not settings["permissions"]:
                del settings["permissions"]
            atomic_write(dest, dump_json(settings))
    for folder in (os.path.join(config, RULES_REL), os.path.join(config, STATE_REL)):
        if os.path.isdir(folder) and not os.listdir(folder):
            os.rmdir(folder)
    for description, args in plan.cli:
        print("running: %s" % description)
        result = run_cli(claude, args, config, check=False)
        if result.returncode != 0:
            print("  warning: command failed; run it manually if needed")
    print("uninstall: done. backup id: %s" % backup.stamp)


# --- restore ---------------------------------------------------------------------------------

def restore(config, stamp, dry_run):
    folder = os.path.join(config, BACKUPS_REL, stamp)
    index_path = os.path.join(folder, "index.json")
    if os.path.basename(stamp) != stamp or not os.path.isfile(index_path):
        raise InstallError("backup %s not found under %s" % (stamp, os.path.join(config, BACKUPS_REL)))
    index = read_json(index_path, {})
    for entry in index.get("entries", []):
        rel = entry["path"].replace("/", os.sep)
        if ".." in rel.split(os.sep) or os.path.isabs(rel):
            raise InstallError("unsafe path in backup index: %s" % entry["path"])
    check_paths_safe(config, [e["path"].replace("/", os.sep) for e in index.get("entries", [])])
    # Snapshot the current state first so a restore can itself be undone (it may delete edited files).
    undo = None if dry_run else Backup(config, timestamp())
    for entry in index.get("entries", []):
        if undo:
            undo.save(entry["path"].replace("/", os.sep))
    for entry in index.get("entries", []):
        rel = entry["path"].replace("/", os.sep)
        dest = os.path.join(config, rel)
        if entry["existed"]:
            print("  %-8s %s" % ("restore", entry["path"]))
            if not dry_run:
                with open(os.path.join(folder, "files", rel), "rb") as handle:
                    atomic_write(dest, handle.read())
        elif os.path.exists(dest):
            print("  %-8s %s" % ("delete", entry["path"]))
            if not dry_run:
                os.remove(dest)
    print("restore: %s%s. Plugin and MCP registrations are not file backups; use uninstall or the claude CLI for those."
          % (stamp, " (dry run)" if dry_run else " done"))
    if undo:
        print("restore: previous state saved as backup id %s" % undo.stamp)


# --- detection -------------------------------------------------------------------------------

def plugin_installed(claude, config):
    result = run_cli(claude, ["plugin", "list", "--json"], config, check=False)
    try:
        items = json.loads(result.stdout or "[]")
    except ValueError:
        return False
    return any(PLUGIN_ID in json.dumps(item) or (item.get("name") == "forge" and MARKETPLACE in json.dumps(item))
               for item in items if isinstance(item, dict))


def claude_json_path(config):
    # The CLI keeps user-scope MCP servers in $CLAUDE_CONFIG_DIR/.claude.json, or ~/.claude.json by default.
    if is_default_config(config):
        return os.path.join(os.path.expanduser("~"), ".claude.json")
    return os.path.join(config, ".claude.json")


def mcp_entry(config, name):
    try:
        data = read_json(claude_json_path(config), {})
    except InstallError:
        return None
    return (data.get("mcpServers") or {}).get(name) if isinstance(data, dict) else None


def same_engram(entry, engram):
    command = os.path.normcase(os.path.abspath(entry.get("command", ""))) if entry.get("command") else ""
    return command == os.path.normcase(os.path.abspath(engram)) and entry.get("args") == ["mcp", "--tools=agent"]


def plugin_version():
    manifest = os.path.join(REPO_ROOT, "plugins", "forge", ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as handle:
            return json.load(handle).get("version", "unknown")
    except (OSError, ValueError):
        return "unknown"


def prerequisites(claude, dry_run=False):
    print("prerequisites:")
    print("  python    %s" % sys.version.split()[0])
    if not claude:
        print("  claude    NOT FOUND - install: %s" % CLAUDE_INSTALL)
    else:
        # Dry runs never invoke the claude CLI, not even for --version.
        print("  claude    %s" % ("found at %s" % claude if dry_run else tool_version(claude)))
    engram = find_engram()
    print("  engram    %s" % (tool_version(engram, ("version",)) if engram else "not found (optional) - %s" % ENGRAM_INSTALL))
    openspec = shutil.which("openspec")
    print("  openspec  %s" % (tool_version(openspec) if openspec else "not found (optional) - %s" % OPENSPEC_INSTALL))
    git = shutil.which("git")
    print("  git       %s" % (tool_version(git) if git else "not found (recommended)"))


# --- CLI -------------------------------------------------------------------------------------

def status(config):
    manifest = read_json(os.path.join(config, MANIFEST_REL), None)
    print("config dir: %s" % config)
    if not manifest:
        print("not installed")
        return
    print("installed version %s at %s" % (manifest.get("version"), manifest.get("installed_at")))
    for rel, digest in sorted(manifest.get("files", {}).items()):
        dest = os.path.join(config, rel)
        state = "missing" if not os.path.isfile(dest) else ("ok" if sha256(dest) == digest else "modified")
        print("  %-9s %s" % (state, rel))
    print("  permissions: %d ask, %d deny" % (len(manifest["permissions"].get("ask", [])), len(manifest["permissions"].get("deny", []))))
    print("  plugin registered by installer: %s" % manifest.get("plugin"))
    print("  engram MCP registered by installer: %s" % manifest.get("engram_mcp"))
    backups = os.path.join(config, BACKUPS_REL)
    if os.path.isdir(backups):
        print("  backups: %s" % ", ".join(sorted(os.listdir(backups))[-5:]))


def build_parser():
    parser = argparse.ArgumentParser(prog="agentcfg", description="forge complementary installer")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "uninstall", "restore", "status"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--config-dir", help="Claude config dir (default: $CLAUDE_CONFIG_DIR or ~/.claude)")
        if name != "status":
            cmd.add_argument("--dry-run", action="store_true", help="show planned operations without changing anything")
        if name in ("install", "uninstall"):
            cmd.add_argument("--claude-bin", help="path to the claude CLI (default: auto-detect)")
        if name == "install":
            cmd.add_argument("--with-permissions", action="store_true", help="merge forge ask/deny rules into settings.json")
            cmd.add_argument("--with-plugin", action="store_true", help="register the marketplace and install the forge plugin")
            cmd.add_argument("--with-engram", action="store_true", help="register the Engram MCP server at user scope")
        if name == "uninstall":
            cmd.add_argument("--purge", action="store_true", help="also remove the private profile")
        if name == "restore":
            cmd.add_argument("backup_id", help="backup id printed by install/uninstall")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        config = resolve_config_dir(args.config_dir)
        if args.command == "status":
            status(config)
            return 0
        if args.command == "restore":
            restore(config, args.backup_id, args.dry_run)
            return 0
        check_paths_safe(config, [RULES_REL, STATE_REL, BACKUPS_REL, SETTINGS_REL])
        claude = find_claude(args.claude_bin)
        manifest = read_json(os.path.join(config, MANIFEST_REL), {})
        if args.command == "install":
            prerequisites(claude, args.dry_run)
            plan, new_manifest = plan_install(config, manifest, args, claude)
            check_paths_safe(config, [rel for _, rel, _ in plan.ops])
            plan.show("install plan" + (" (dry run)" if args.dry_run else ""))
            if not args.dry_run:
                apply_install(plan, manifest, new_manifest, claude)
        else:
            plan = plan_uninstall(config, manifest, args, claude)
            check_paths_safe(config, [rel for _, rel, _ in plan.ops])
            plan.show("uninstall plan" + (" (dry run)" if args.dry_run else ""))
            if not args.dry_run and (plan.ops or plan.cli):
                apply_uninstall(plan, claude)
        return 0
    except InstallError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
