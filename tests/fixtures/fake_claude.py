"""Fake `claude` CLI for installer tests (forge:synthetic-fixture).

Keeps its state under $CLAUDE_CONFIG_DIR and logs every invocation to calls.log there.
Mimics the real CLI's storage of user-scope MCP servers in $CLAUDE_CONFIG_DIR/.claude.json.
"""
import json
import os
import sys

config = os.environ["CLAUDE_CONFIG_DIR"]
state_path = os.path.join(config, "fake-claude-state.json")
mcp_path = os.path.join(config, ".claude.json")
args = sys.argv[1:]

with open(os.path.join(config, "calls.log"), "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\n")


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


state = load(state_path, {"plugins": [], "marketplaces": []})
if args[:2] == ["plugin", "list"]:
    print(json.dumps([{"id": p, "scope": "user", "enabled": True} for p in state["plugins"]]))
elif args[:3] == ["plugin", "marketplace", "add"]:
    state["marketplaces"].append("facundo-agent-config")
elif args[:3] == ["plugin", "marketplace", "remove"]:
    state["marketplaces"] = [m for m in state["marketplaces"] if m != args[3]]
elif args[:2] == ["plugin", "install"]:
    state["plugins"].append(args[2])
elif args[:2] == ["plugin", "uninstall"]:
    state["plugins"] = [p for p in state["plugins"] if p != args[2]]
elif args[:2] == ["mcp", "add"]:
    name = args[args.index("--scope") + 2]
    rest = args[args.index("--") + 1:]
    data = load(mcp_path, {})
    data.setdefault("mcpServers", {})[name] = {"type": "stdio", "command": rest[0], "args": rest[1:], "env": {}}
    save(mcp_path, data)
elif args[:2] == ["mcp", "remove"]:
    data = load(mcp_path, {})
    data.get("mcpServers", {}).pop(args[2], None)
    save(mcp_path, data)
elif args[:1] == ["--version"]:
    print("0.0.0 (fake claude)")
else:
    sys.stderr.write("fake claude: unsupported %s\n" % args)
    sys.exit(2)
save(state_path, state)
