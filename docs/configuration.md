# Configuration layers

forge spreads its behavior over several Claude Code mechanisms. Each surface has exactly one owner, so tools never overwrite each other.

| Layer | Location | Loaded | Owner | Contains |
|---|---|---|---|---|
| Plugin `forge` | Claude Code plugin cache (installed from the `facundo-agent-config` marketplace) | Skills and agents on demand. The guard hook runs on every matching tool call | Claude Code CLI (`claude plugin install`) | Skills, agents, guard hook, Engineering Manual |
| User rules | `~/.claude/rules/facundo-agent-config/*.md` | Every session, every project | forge installer (manifest) | Methodology: core, SDD, memory, delegation, tokens, autonomy |
| Private profile | `~/.claude/rules/facundo-agent-config/profile.md` | Every session | You (created once from a template, never overwritten) | Language, experience, learning goals, preferred defaults |
| Optional permissions | `~/.claude/settings.json` → `permissions.ask` / `permissions.deny` | Every session | forge installer, only with `--with-permissions` (manifest) | Second-layer `ask`/`deny` rules |
| Engram MCP entry | `~/.claude.json` → `mcpServers.engram` (user scope) | Every session | Claude Code CLI, called by the installer with `--with-engram` | `engram mcp --tools=agent` |
| Engram data | `~/.engram/` | Through `mem_*` tools | Engram | Memories. forge never edits it directly |
| Project instructions | `<repo>/AGENTS.md`, `<repo>/CLAUDE.md`, `<repo>/.claude/` | Sessions in that repo | The project | Project constraints, stack, commands |
| Project specs | `<repo>/openspec/` | Through `/opsx:*` and `openspec` | OpenSpec (per project, opt-in) | Specs, changes, archive |
| Project memory key | `<repo>/.engram/config.json` | Through Engram | The project | Fixed Engram project name |

## Why not a CLAUDE.md in the plugin?

Claude Code does not load a `CLAUDE.md` placed at a plugin root. The plugin format cannot ship always-loaded context or permission rules. That is why the methodology lives in user-level rules, which `~/.claude/rules/` loads recursively.

## Why not a section in `~/.claude/CLAUDE.md`?

That file is yours, and other tools also write to it (Gentle AI and the Engram plugin, for example). Two writers on one file make uninstalls unsafe. forge only writes inside its own folder.

## Global vs project

- **Global (forge):** how agents work, meaning methodology, safety and memory protocol. It contains nothing about a specific product.
- **Project:** what this product is. Requirements, stack, architecture, deployment and decisions live in the repository. Use `/forge:project-init` to create them.

## Reference-only material

The Engineering Manual (`plugins/forge/manual/`) and the files under `docs/` are not always loaded. Skills read specific manual sections when a task needs them.
