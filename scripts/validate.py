#!/usr/bin/env python3
"""Structural, content and secret validation for forge.

Stdlib only. Usage: python scripts/validate.py [--root PATH]
Exits 1 on any error. `claude plugin validate` remains the authoritative manifest check;
this script adds offline checks for everything the specs require.
"""
import argparse
import json
import os
import re
import subprocess
import sys

PLUGIN_REL = os.path.join("plugins", "forge")
SKILLS = [
    "plan-work", "implement", "review-code", "verify-changes", "documentation", "devops-iac",
    "feature", "bugfix", "release", "project-init",
    "learn-concept", "hands-on-lab", "research-technology", "aws-security", "networking-lab", "study-topic",
]
OPENSPEC_SKILLS = ["plan-work", "implement", "verify-changes", "review-code", "documentation"]
AGENT_TOOLS = {
    "architect": {"Read", "Grep", "Glob", "WebFetch", "WebSearch"},
    "explorer": {"Read", "Grep", "Glob"},
    "implementer": {"Read", "Grep", "Glob", "Edit", "Write", "Bash"},
    "reviewer": {"Read", "Grep", "Glob", "Bash"},
    "security-reviewer": {"Read", "Grep", "Glob", "Bash"},
    "tutor": {"Read", "Grep", "Glob", "WebFetch", "WebSearch"},
}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
IGNORED_AGENT_FIELDS = {"permissionMode", "hooks", "mcpServers"}
# Verified against `engram mcp --tools=agent` tools/list (Engram 2.1.0 and 3.4.0, 2026-10-14).
ENGRAM_TOOLS = {"mem_current_project", "mem_context", "mem_search", "mem_save", "mem_session_summary",
                "mem_get_observation", "mem_session_start", "mem_session_end", "mem_update"}
RULES_BUDGET = 120
PLUGIN_READ = "Read(${CLAUDE_PLUGIN_ROOT}/**)"
SKILL_MAX_LINES = 300
DESCRIPTION_MAX = 1536
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")
RESERVED_PREFIX = re.compile(r"^(claude|anthropic|anthropics|cc-plugin)-", re.IGNORECASE)
MARKER = re.compile(r"^- \*\*(MUST|SHOULD|EXPERIMENTAL)\*\* ")
PROVIDER_TERMS = re.compile(r"\b(AWS|Lambda|CloudFront|CloudWatch|CloudTrail|EventBridge|DynamoDB|GuardDuty|"
                            r"Secrets Manager|S3|KMS|API Gateway|Azure|GCP|Google Cloud)\b")
TOOL_FIELDS = ["Category", "Classification", "Purpose", "Evidence", "Alternatives", "Installation state", "Lifecycle"]
TOOL_CLASSES = {"Required", "Recommended", "Optional", "Experimental", "Rejected", "Deferred"}
REQUIRED_TOOLS = ["Claude Code", "OpenSpec", "Engram", "Gentle AI", "Gentleman Guardian Angel", "Gentle Shell",
                  "code-graph-mcp (sdsrss)", "codegraph-mcp (denzharkov)", "Graphiti", "Context7"]
TECH_FIELDS = ["Purpose", "Use cases", "Trade-offs", "Security", "Cost", "Operational complexity", "Alternatives", "Status"]
CATALOG_CRITERIA = ["purpose", "compatibility", "windows", "maintenance", "documentation", "security", "data exposure",
                    "installation", "token", "cost", "overlap", "reliability", "license"]
SYNTHETIC_MARKER = "forge:synthetic-fixture"
SECRET_PATTERNS = [
    ("aws-access-key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{40,}")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("windows-user-path", re.compile(r"\b[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}(?!(Public|Default|<)[\\/>])[A-Za-z0-9._-]+")),
    ("unix-home-path", re.compile(r"(?<![\w.~])/(home|Users)/(?!<)[a-z][a-z0-9._-]+/")),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__", "local", ".venv"}
TEXT_EXT = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".txt", ".toml", ".gitignore", ""}


class Report:
    def __init__(self, root):
        self.root = root
        self.errors = []

    def error(self, path, message):
        rel = os.path.relpath(path, self.root) if os.path.isabs(path) else path
        self.errors.append("%s: %s" % (rel.replace("\\", "/"), message))


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def load_json(report, path):
    try:
        return json.loads(read(path))
    except (OSError, ValueError) as exc:
        report.error(path, "invalid JSON (%s)" % exc)
        return None


def frontmatter(text):
    """Parse simple `key: value` YAML frontmatter (single-line values)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    data = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith((" ", "#")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("\"'")
    return data, text[end + 4:]


def section(text, heading):
    """Return the body of a `## heading` section (until the next `## `)."""
    match = re.search(r"^## %s\b.*?$(.*?)(?=^## |\Z)" % re.escape(heading), text, re.M | re.S)
    return match.group(1) if match else None


def check_links(report, path, text, plugin_root):
    base = os.path.dirname(path)
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"^[a-z]+:|^#|^mailto:", target):
            continue
        target = target.split("#")[0]
        if target and not os.path.exists(os.path.normpath(os.path.join(base, target))):
            report.error(path, "broken link: %s" % target)
    for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)\"']+)", text):
        target = target.rstrip(".,;:")
        if not os.path.exists(os.path.join(plugin_root, target)):
            report.error(path, "missing plugin path: ${CLAUDE_PLUGIN_ROOT}/%s" % target)


# --- manifests -------------------------------------------------------------------------------

def check_manifests(report):
    root = report.root
    market_path = os.path.join(root, ".claude-plugin", "marketplace.json")
    market = load_json(report, market_path)
    if market is None:
        return
    for field in ("name", "owner", "plugins"):
        if field not in market:
            report.error(market_path, "missing field '%s'" % field)
    if not KEBAB.match(str(market.get("name", ""))):
        report.error(market_path, "marketplace name must be kebab-case")
    if not (market.get("owner") or {}).get("name"):
        report.error(market_path, "owner.name is required")
    for index, entry in enumerate(market.get("plugins") or []):
        where = "plugins[%d]" % index
        name, source = entry.get("name", ""), entry.get("source")
        if not KEBAB.match(name):
            report.error(market_path, "%s name must be kebab-case" % where)
        if not isinstance(source, str):
            report.error(market_path, "%s source must be a relative path" % where)
            continue
        if ".." in source.replace("\\", "/").split("/"):
            report.error(market_path, "%s source contains '..'" % where)
            continue
        plugin_dir = os.path.normpath(os.path.join(root, source))
        manifest_path = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
        if not os.path.isfile(manifest_path):
            report.error(market_path, "%s source has no .claude-plugin/plugin.json" % where)
            continue
        manifest = load_json(report, manifest_path)
        if manifest is None:
            continue
        if manifest.get("name") != name:
            report.error(manifest_path, "name '%s' differs from marketplace entry '%s'" % (manifest.get("name"), name))
        if entry.get("version") and entry.get("version") != manifest.get("version"):
            report.error(manifest_path, "version differs from marketplace entry")
        check_plugin_manifest(report, manifest_path, manifest)
        if os.path.exists(os.path.join(plugin_dir, "CLAUDE.md")):
            report.error(plugin_dir, "plugin root must not contain CLAUDE.md (it is not loaded)")


def check_plugin_manifest(report, path, manifest):
    name = manifest.get("name", "")
    if not KEBAB.match(name) or RESERVED_PREFIX.match(name):
        report.error(path, "plugin name must be kebab-case and not use a reserved prefix")
    if not SEMVER.match(str(manifest.get("version", ""))):
        report.error(path, "version must be semver")
    for field in ("description", "license"):
        if not manifest.get(field):
            report.error(path, "missing '%s'" % field)
    if not (manifest.get("author") or {}).get("name"):
        report.error(path, "author.name is required")
    if "mcpServers" in manifest:
        report.error(path, "the plugin must not declare MCP servers")


# --- skills ----------------------------------------------------------------------------------

SKILL_CONTENT_CHECKS = {
    "release": [r"\bSTOP\b", r"explicit approval"],
    "plan-work": [r"openspec init", r"unless the user asks"],
    "project-init": [r"AWS, Terraform, Docker and Kubernetes are options", r"not defaults", r"STOP", r"openspec init"],
    "devops-iac": [r"plan", r"[Bb]efore any `apply`", r"explicit approval"],
    "feature": [r"`explorer`", r"`architect`", r"`implementer`", r"`reviewer`", r"`security-reviewer`"],
    "bugfix": [r"`explorer`", r"regression test"],
    "learn-concept": [r"Diagnostic", r"Checkpoint", r"[Ss]kip"],
    "study-topic": [r"[Aa]ssess prior knowledge", r"Checkpoint", r"skip checks", r"scope `personal`",
                    r"learning-progress\.md", r"confirmation"],
    "research-technology": [r"Verified facts", r"Recommendations", r"Hypotheses"],
    "hands-on-lab": [r"[Aa]uthorized scope", r"[Cc]leanup", r"cost"],
    "aws-security": [r"[Rr]ead-only", r"authorized"],
    "networking-lab": [r"[Cc]leanup"],
}
LAB_TEMPLATE_SECTIONS = ["Objective", "Authorized scope", "Prerequisites", "Steps", "Validation", "Cleanup", "Estimated cost"]


def check_skills(report, plugin_root):
    skills_dir = os.path.join(plugin_root, "skills")
    found = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))) if os.path.isdir(skills_dir) else []
    for missing in sorted(set(SKILLS) - set(found)):
        report.error(skills_dir, "missing skill '%s'" % missing)
    for name in found:
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            report.error(os.path.join(skills_dir, name), "missing SKILL.md")
            continue
        text = read(path)
        meta, body = frontmatter(text)
        if meta is None:
            report.error(path, "missing frontmatter")
            continue
        if meta.get("name") != name:
            report.error(path, "frontmatter name must equal directory name")
        description = meta.get("description", "")
        if not description:
            report.error(path, "missing description")
        elif len(description) > DESCRIPTION_MAX:
            report.error(path, "description longer than %d characters" % DESCRIPTION_MAX)
        if text.count("\n") + 1 >= SKILL_MAX_LINES:
            report.error(path, "SKILL.md must be under %d lines" % SKILL_MAX_LINES)
        if section(body, "Verification") is None:
            report.error(path, "missing '## Verification' section")
        allowed = meta.get("allowed-tools", "")
        reads_plugin = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}|\]\((references|templates)/", body)
        if allowed and allowed != PLUGIN_READ:
            report.error(path, "allowed-tools may only be %s" % PLUGIN_READ)
        if reads_plugin and allowed != PLUGIN_READ:
            report.error(path, "reads plugin files but does not pre-approve %s" % PLUGIN_READ)
        if name in OPENSPEC_SKILLS and not re.search(r"/opsx:|openspec validate", body):
            report.error(path, "must delegate to OpenSpec (/opsx: or openspec validate)")
        for pattern in SKILL_CONTENT_CHECKS.get(name, []):
            if not re.search(pattern, body):
                report.error(path, "missing required content: %s" % pattern)
        check_links(report, path, body, plugin_root)
        for ref_dir in ("references", "templates"):
            folder = os.path.join(skills_dir, name, ref_dir)
            for ref in (os.listdir(folder) if os.path.isdir(folder) else []):
                if ref.endswith(".md"):
                    check_links(report, os.path.join(folder, ref), read(os.path.join(folder, ref)), plugin_root)
    template = os.path.join(skills_dir, "hands-on-lab", "references", "lab-template.md")
    if os.path.isfile(template):
        text = read(template)
        for heading in LAB_TEMPLATE_SECTIONS:
            if section(text, heading) is None:
                report.error(template, "missing lab section '%s'" % heading)


# --- agents ----------------------------------------------------------------------------------

def check_agents(report, plugin_root):
    agents_dir = os.path.join(plugin_root, "agents")
    files = sorted(f for f in os.listdir(agents_dir) if f.endswith(".md")) if os.path.isdir(agents_dir) else []
    names = {f[:-3] for f in files}
    for missing in sorted(set(AGENT_TOOLS) - names):
        report.error(agents_dir, "missing agent '%s'" % missing)
    for file_name in files:
        path = os.path.join(agents_dir, file_name)
        meta, body = frontmatter(read(path))
        if meta is None:
            report.error(path, "missing frontmatter")
            continue
        name = meta.get("name", "")
        if name != file_name[:-3]:
            report.error(path, "frontmatter name must equal file name")
        if not meta.get("description"):
            report.error(path, "missing description")
        if "tools" not in meta:
            report.error(path, "tools must be explicit")
        for field in IGNORED_AGENT_FIELDS & set(meta):
            report.error(path, "'%s' is ignored for plugin agents; do not declare it" % field)
        tools = {t.strip() for t in meta.get("tools", "").split(",") if t.strip()}
        if name != "implementer" and tools & WRITE_TOOLS:
            report.error(path, "only implementer may have write tools (found %s)" % ", ".join(sorted(tools & WRITE_TOOLS)))
        if name in AGENT_TOOLS and tools != AGENT_TOOLS[name]:
            report.error(path, "tools %s differ from privilege table %s" % (sorted(tools), sorted(AGENT_TOOLS[name])))
        restrictions = section(body, "Restrictions") or ""
        if "main session" not in restrictions or not re.search(r"push", restrictions):
            report.error(path, "Restrictions must forbid dangerous operations and return them to the main session")
        if name in ("reviewer", "security-reviewer"):
            for heading in ("Confirmed findings", "Potential risks", "Suggestions"):
                if heading not in body:
                    report.error(path, "output must contain '%s'" % heading)
        check_links(report, path, body, plugin_root)


# --- hooks -----------------------------------------------------------------------------------

def check_hooks(report, plugin_root):
    hooks_path = os.path.join(plugin_root, "hooks", "hooks.json")
    data = load_json(report, hooks_path)
    if data is None:
        return
    events = (data.get("hooks") or {})
    if "PreToolUse" not in events:
        report.error(hooks_path, "missing PreToolUse hook")
    for groups in events.values():
        for group in groups:
            for hook in group.get("hooks", []):
                for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)", hook.get("command", "")):
                    if not os.path.isfile(os.path.join(plugin_root, target)):
                        report.error(hooks_path, "hook script not found: %s" % target)
    policy_path = os.path.join(plugin_root, "hooks", "policy.json")
    policy = load_json(report, policy_path)
    if policy is None:
        return
    seen = set()
    for rule in policy.get("command_rules", []):
        if rule.get("id") in seen:
            report.error(policy_path, "duplicate rule id %s" % rule.get("id"))
        seen.add(rule.get("id"))
        if rule.get("decision") not in ("deny", "ask"):
            report.error(policy_path, "rule %s has invalid decision" % rule.get("id"))
        try:
            re.compile(rule.get("pattern", ""))
        except re.error as exc:
            report.error(policy_path, "rule %s has invalid regex (%s)" % (rule.get("id"), exc))


# --- global rules ----------------------------------------------------------------------------

RULE_CHECKS = {
    "core.md": [r"1\) code.*2\) tests.*3\) approved OpenSpec.*4\) ADRs.*5\) Engineering Manual.*6\) project instructions.*7\) Engram",
                r"investigate"],
    "sdd.md": [r"openspec/", r"[Ll]ightweight path", r"Never run `openspec init`", r"not approval",
               r"architecture", r"security", r"infrastructure", r"memory", r"installers"],
    "delegation.md": [r"resumed from the original request plus `git diff`", r"not by file or command count",
                      r"orchestrator", r"requirements", r"conflict resolution", r"integration", r"final verification",
                      r"memory writes", r"Never run two agents", r"objective", r"relevant paths", r"approved scope",
                      r"expected deliverable", r"required verification", r"prohibited actions", r"OpenSpec change"],
    "tokens.md": [r"line ranges", r"[Ee]ngram", r"re-read", r"concise", r"correctness"],
    "autonomy.md": [r"global installs", r"production deploys", r"cost", r"destructive", r"permissions", r"Git hooks",
                    r"publishing", r"memory integrations", r"external service", r"does not authorize"],
    "memory.md": [r"context, not authority", r"only when the tool confirms", r"[Nn]ever save secrets",
                  r"without user approval", r"`personal` scope"],
}


def check_rules(report):
    rules_dir = os.path.join(report.root, "global-config", "rules")
    if not os.path.isdir(rules_dir):
        report.error(rules_dir, "missing rules directory")
        return
    total = 0
    for file_name in sorted(os.listdir(rules_dir)):
        if not file_name.endswith(".md"):
            continue
        path = os.path.join(rules_dir, file_name)
        text = read(path)
        total += text.count("\n") + (0 if text.endswith("\n") else 1)
        for pattern in RULE_CHECKS.get(file_name, []):
            if not re.search(pattern, text, re.S):
                report.error(path, "missing required clause: %s" % pattern)
        if re.search(r"manual/|^@", text, re.M):
            report.error(path, "rules must not import or inline Engineering Manual files")
    for file_name in RULE_CHECKS:
        if not os.path.isfile(os.path.join(rules_dir, file_name)):
            report.error(rules_dir, "missing rule %s" % file_name)
    if total > RULES_BUDGET:
        report.error(rules_dir, "rules total %d lines, budget is %d" % (total, RULES_BUDGET))
    memory = os.path.join(rules_dir, "memory.md")
    if os.path.isfile(memory):
        for tool in set(re.findall(r"`(mem_[a-z_]+)`", read(memory))) - ENGRAM_TOOLS:
            report.error(memory, "unknown Engram tool %s" % tool)
    template = os.path.join(report.root, "global-config", "templates", "profile.md")
    if not os.path.isfile(template):
        report.error(template, "missing profile template")


# --- manual and catalogs ---------------------------------------------------------------------

def entries(text):
    return re.findall(r"^### (.+?)\n(.*?)(?=^### |^## |\Z)", text, re.M | re.S)


def check_manual(report, plugin_root):
    manual = os.path.join(plugin_root, "manual")
    index = os.path.join(manual, "README.md")
    if not os.path.isfile(index):
        report.error(index, "missing manual index")
        return
    index_text = read(index)
    check_links(report, index, index_text, plugin_root)
    if "OpenSpec" not in (section(index_text, "Evolution") or ""):
        report.error(index, "missing evolution rule referencing OpenSpec")
    linked = {os.path.normpath(os.path.join(manual, t)) for t in re.findall(r"\]\(([^)#\s]+\.md)\)", index_text)}
    for folder, _, files in os.walk(manual):
        for file_name in files:
            path = os.path.normpath(os.path.join(folder, file_name))
            if not file_name.endswith(".md") or path == os.path.normpath(index):
                continue
            if path not in linked:
                report.error(path, "not linked from manual/README.md")
            text = read(path)
            check_links(report, path, text, plugin_root)
            top = os.path.relpath(path, manual).replace("\\", "/").split("/")[0]
            if top in ("core", "delivery", "security", "providers"):
                standards = section(text, "Standards")
                if standards is None:
                    report.error(path, "missing '## Standards' section")
                else:
                    for line in standards.splitlines():
                        if line.startswith("- ") and not MARKER.match(line):
                            report.error(path, "standard without MUST/SHOULD/EXPERIMENTAL marker: %s" % line[:60])
            if top in ("core", "delivery", "security"):
                for line_no, line in enumerate(text.splitlines(), 1):
                    if PROVIDER_TERMS.search(line):
                        report.error(path, "line %d: provider-specific term outside providers/" % line_no)
    check_catalogs(report, os.path.join(manual, "catalog"))


def check_catalogs(report, catalog):
    readme = os.path.join(catalog, "README.md")
    if os.path.isfile(readme):
        text = read(readme).lower()
        for criterion in CATALOG_CRITERIA:
            if criterion not in text:
                report.error(readme, "missing evaluation criterion '%s'" % criterion)
        if "installation policy" not in text:
            report.error(readme, "missing installation policy")
    tools_path = os.path.join(catalog, "tools.md")
    if os.path.isfile(tools_path):
        found = {}
        for title, body in entries(read(tools_path)):
            found[title.strip()] = body
            for field in TOOL_FIELDS:
                if not re.search(r"^- \*\*%s\b" % re.escape(field), body, re.M):
                    report.error(tools_path, "tool '%s' missing field '%s'" % (title, field))
            match = re.search(r"^- \*\*Classification:\*\* (\w+)", body, re.M)
            if match and match.group(1) not in TOOL_CLASSES:
                report.error(tools_path, "tool '%s' has unknown classification" % title)
        for tool in REQUIRED_TOOLS:
            if not any(tool in title for title in found):
                report.error(tools_path, "missing required tool entry '%s'" % tool)
        categories = {re.search(r"\*\*Category:\*\* ([\w-]+)", b).group(1) for b in found.values() if "**Category:**" in b}
        if not {"code-graph", "knowledge-graph"} <= categories:
            report.error(tools_path, "code-graph and knowledge-graph categories must both exist and be distinct")
    tech_path = os.path.join(catalog, "technologies.md")
    if os.path.isfile(tech_path):
        for title, body in entries(read(tech_path)):
            for field in TECH_FIELDS:
                if not re.search(r"^- \*\*%s:\*\*" % re.escape(field), body, re.M):
                    report.error(tech_path, "technology '%s' missing field '%s'" % (title, field))


# --- repository-wide -------------------------------------------------------------------------

def repo_files(root):
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root,
                             capture_output=True, check=True, timeout=60).stdout.decode("utf-8")
        files = [f for f in out.split("\0") if f]
        if files:
            return [os.path.join(root, f) for f in files]
    except (OSError, subprocess.SubprocessError):
        pass
    result = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        result.extend(os.path.join(folder, n) for n in names)
    return result


def private_terms(root):
    path = os.path.join(root, "local", "private-terms.txt")
    if not os.path.isfile(path):
        return []
    return [line.strip() for line in read(path).splitlines() if line.strip() and not line.startswith("#")]


def scan_text(text, terms=()):
    """Return a list of (kind, line_number) hits for secrets, user paths and private terms."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for kind, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                hits.append((kind, line_no))
        for term in terms:
            if re.search(r"\b%s\b" % re.escape(term), line, re.IGNORECASE):
                hits.append(("private-term", line_no))
    return hits


def check_files(report):
    terms = private_terms(report.root)
    for path in repo_files(report.root):
        rel = os.path.relpath(path, report.root).replace("\\", "/")
        if rel.split("/")[0] in SKIP_DIRS or os.path.splitext(path)[1].lower() not in TEXT_EXT:
            continue
        try:
            text = read(path)
        except (OSError, UnicodeDecodeError):
            continue
        if path.endswith(".json"):
            load_json(report, path)
        if path.endswith((".yaml", ".yml")):
            check_yaml(report, path, text)
        if SYNTHETIC_MARKER in text:
            continue
        for kind, line_no in scan_text(text, terms):
            report.error(path, "line %d: possible %s" % (line_no, kind))
    workflow = os.path.join(report.root, ".github", "workflows", "ci.yml")
    if os.path.isfile(workflow) and "secrets." in read(workflow):
        report.error(workflow, "CI must not reference secrets")


def check_yaml(report, path, text):
    try:
        import yaml  # optional; stdlib-only fallback below
        yaml.safe_load(text)
        return
    except ImportError:
        pass
    except Exception as exc:  # yaml.YAMLError without importing its type
        report.error(path, "invalid YAML (%s)" % exc)
        return
    for line_no, line in enumerate(text.splitlines(), 1):
        if "\t" in line[: len(line) - len(line.lstrip())]:
            report.error(path, "line %d: tab indentation is invalid YAML" % line_no)


def run(root):
    report = Report(os.path.abspath(root))
    plugin_root = os.path.join(report.root, PLUGIN_REL)
    check_manifests(report)
    check_skills(report, plugin_root)
    check_agents(report, plugin_root)
    check_hooks(report, plugin_root)
    check_rules(report)
    check_manual(report, plugin_root)
    check_files(report)
    for name in ("README.md", "SECURITY.md", "CONTRIBUTING.md"):
        path = os.path.join(report.root, name)
        if os.path.isfile(path):
            check_links(report, path, read(path), plugin_root)
    docs = os.path.join(report.root, "docs")
    for name in (sorted(os.listdir(docs)) if os.path.isdir(docs) else []):
        if name.endswith(".md"):
            check_links(report, os.path.join(docs, name), read(os.path.join(docs, name)), plugin_root)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = parser.parse_args(argv)
    report = run(args.root)
    for message in report.errors:
        print("ERROR " + message)
    print("validate: %d error(s)" % len(report.errors))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
