# Design

## Context

See proposal.md for motivation. Facts verified on 2026-10-14 (installed versions and official docs):

- **Claude Code 2.1.296:**
  - Plugins ship skills, agents, hooks, MCP/LSP and limited `settings`. They cannot ship permission rules or always-loaded context.
  - A plugin-root `CLAUDE.md` is ignored.
  - Plugin agents ignore `permissionMode`, `hooks` and `mcpServers`.
  - Hooks receive `agent_type` inside subagents.
  - `~/.claude/rules/**/*.md` is loaded recursively in every session.
  - `CLAUDE_CONFIG_DIR` isolates config for tests.
- **OpenSpec 1.14.1:** core profile installed in this repo. Its six `/opsx:*` commands and skills live in `.claude/`.
- **Engram 2.1.0:** has an existing DB at `~/.engram`. It is not wired to Claude Code (no MCP servers registered). It provides `mem_search`, `mem_context`, `mem_save`, `mem_session_summary`, `mem_current_project` and related tools. Project scope resolves through `.engram/config.json` or cwd.
- **Gentle AI 3.7.0:** installed, but `state.json` shows no agents. Its earlier Claude Code files were removed, leaving empty directories in `~/.claude`. Current docs (4.x):
  - SDD is retired in favor of ODD guidance.
  - Components are `engram`, `skills`, `context7`, `persona`, `permissions`, `gga` and `theme`.
  - `install` takes `--agent`, `--preset custom`, `--components`, `--persona custom` and `--dry-run`.
  - `uninstall` is selective by component.
  - Backups are taken before every write.
- **Gentle AI 4.1.1, isolated install (task 2.2):** with only `--components engram --persona custom`, it still wrote:
  - an 80 KB always-loaded `CLAUDE.md` with a mandatory ODD orchestrator (`odd/tasks/` documents and automatic per-task commits);
  - nine review agents;
  - review and telemetry hooks;
  - a `UserPromptSubmit` refresh.

  Its `--dry-run` lists no files and still writes `state.json`. Evidence is in `manual/catalog/tools.md`.
- **GGA 2.10.1:** a pre-commit reviewer of staged files. It sends file content to the configured provider.
- **Gentle Shell:** requires the Pi runtime. It is not a Claude Code component.

## Goals / Non-Goals

**Goals:**
- One owner per configuration surface, and one source of truth per instruction.
- Smallest always-loaded context. Everything else loads on demand.
- Technical enforcement where the platform allows it.
- Every global change is reversible and traceable.

**Non-Goals:**
- OS-level sandboxing.
- Resistance to an agent deliberately obfuscating commands.
- Adopting optional tools (code graph, GGA hooks, Context7) in this change.

## Decisions

### D1. Ownership map
| Surface | Owner |
|---|---|
| Engram binary and database | Engram (official release install) |
| Engram user-scope MCP entry (`~/.claude.json`) | Claude Code CLI, invoked by the forge installer `--with-engram`, recorded in the manifest |
| Specs, changes and `/opsx:*` | OpenSpec (per project) |
| Skills, agents and guard hook | `forge` plugin (Claude Code plugin cache) |
| `~/.claude/rules/facundo-agent-config/` and optional permission rules | forge installer (manifest) |
| Persona and preferences | forge private `profile.md` rule |

No two systems write the same file. Forge never edits `~/.claude.json` directly; only `claude mcp add` and `claude mcp remove` do.

### D2. No Gentle AI; Engram wired directly
Decision taken by the user after the isolated footprint test, on 2026-10-14.
- The installer flag `--with-engram` runs `claude mcp add --scope user engram -- <engram> mcp --tools=agent`. This is the same entry Gentle AI writes, minus its other assets.
- If an `engram` entry already exists with a different command, the installer reports a conflict and does not touch it.
- Uninstall runs `claude mcp remove engram --scope user`, and only when the manifest says forge added the entry.
- The Engram upgrade to 3.4.0 is a separate, approved step. `~/.engram` is backed up first.

Two ideas from ODD are kept as forge rules:
- **Task sizing:** a task is small if it can be resumed from the request plus `git diff`. Small tasks take the lightweight path.
- **Evidence-based delegation:** delegate only when the needed evidence exceeds one inline batch, there are disjoint writers, or a high-risk change needs an independent check.

*Rejected:* Gentle AI 4.x. It imposes ODD over OpenSpec, makes commits without approval and loads about 20k tokens of always-on instructions. *Rejected:* the official Engram plugin (`engram setup claude-code`). It needs `jq` and adds third-party session hooks. It stays an option in the catalog if lifecycle hooks prove necessary.

### D2b. Orchestration
The main Claude Code session is the orchestrator. It owns requirements, integration, final verification, memory writes and reporting. Workflow skills (`feature`, `bugfix`, `release`, `project-init`) define when to call which subagent:
- `explorer` for broad discovery;
- `architect` for design alternatives;
- `implementer` for bounded, disjoint edit surfaces;
- `reviewer` and `security-reviewer` for independent checks of high-risk changes.

Parallel subagents run only for independent, read-only or disjoint work. *Rejected:* a dedicated orchestrator agent set as the default main agent (plugin `settings.agent`). It would replace the user's normal session in every project, and it adds no capability the main session lacks.

### D3. Repository layout
```
.claude-plugin/marketplace.json
plugins/forge/
  .claude-plugin/plugin.json
  skills/<16 skills>/SKILL.md (+references/, templates/)
  agents/<6 agents>.md
  hooks/hooks.json, run-guard.sh, guard.py, policy.json
  manual/            # Engineering Manual + technology & tool catalogs
global-config/rules/ # methodology rules (installed by installer)
global-config/templates/profile.md
installers/          # ps1/sh wrappers
scripts/             # agentcfg.py, validate.py, doctor.py, session_metrics.py
tests/ docs/ openspec/ .github/workflows/
AGENTS.md            # repo dev instructions; CLAUDE.md imports it
```
The manual lives inside the plugin so skills can read it in any project via `${CLAUDE_PLUGIN_ROOT}/manual/...`. There are no top-level `workflows/`, `profile/` or `tool-catalog/` folders, because workflows are skills and the catalog is part of the manual.
*Rejected:* the manual as a separate repo-level `engineering-manual/` folder. Skills in other projects could not reach it without absolute local paths.

### D4. Methodology as user rules
The installer copies the following files and creates `profile.md` from a template if it is absent:
- `core.md`: discovery, source of truth, verification, communication.
- `sdd.md`
- `memory.md`
- `delegation.md`: task sizing, delegation triggers, handoff fields, orchestration.
- `tokens.md`
- `autonomy.md`

The total budget is 120 lines.
*Rejected:* a marked block in `~/.claude/CLAUDE.md`. That file belongs to the user, and other tools such as Gentle AI and Engram may also write sections there. Two writers on one file breaks D1.

### D5. Installer: Python core, platform wrappers
The `.ps1` and `.sh` wrappers detect the OS, locate Python and `claude` (PATH or `~/.local/bin`), and delegate to `scripts/agentcfg.py` (`install`, `uninstall`, `restore`, `status`). The core handles the manifest with SHA-256, timestamped backups, atomic writes, and symlink/foreign-file refusal.
*Rejected:* duplicating the logic in PowerShell and Bash. That means two JSON merge implementations (Bash without `jq` is fragile) and double the tests.

### D6. Engineering Manual scope
- **Index:** `manual/README.md` with the normative levels (`MUST` / `SHOULD` / `EXPERIMENTAL`) and the evolution rule.
- **Sections:**
  - `core/`: principles, SDLC, requirements, SDD/OpenSpec, architecture/ADR, coding, testing, docs, onboarding, definition of done.
  - `delivery/`: cloud, IaC (Terraform/OpenTofu/CloudFormation/CDK/Ansible by role), containers, CI/CD with OIDC, release/rollback, environments, secrets/identity, observability, reliability, operations/incidents, cost.
  - `security/`: threat modeling, least privilege, secure defaults, appsec, supply chain, cloud/infra security, secrets, logging/audit, vulnerability management, security testing.
  - `providers/aws.md`
  - `catalog/technologies.md`
  - `catalog/tools.md`
- **Format:** concise. Each domain is a few bullets with a level, plus decision criteria. Depth grows through later OpenSpec changes, not up front.
*Rejected:* exhaustive manuals now. They would cost tokens to maintain and load, and would not yet be validated by real projects.

### D7. Guard hook
The hook is a shell-form `"${CLAUDE_PLUGIN_ROOT}/hooks/run-guard.sh"`. The launcher tries `python3`, then `python`, then `py -3`, and runs `guard.py` with `policy.json`, which holds the rules as data with ids. Matcher: `Bash|PowerShell|Read|Edit|Write|MultiEdit|NotebookEdit`. Output is `hookSpecificOutput.permissionDecision`, and the reason cites the rule id only. The hook fails open on missing Python or bad input; this is documented and detected by doctor.
*Rejected:* a pure Bash hook, because JSON parsing without `jq` is fragile. *Rejected:* exec form with `python3`, because it can hit the Microsoft Store alias.

### D8. Agents and models
The tool table follows the spec. `explorer` exists because broad, read-heavy discovery is the main context-saving delegation case. All agents use `model: inherit`. Model routing is deferred until billing is verified (master prompt §8.4).

### D9. Usage metrics
The script parses `~/.claude/projects/<project>/*.jsonl` `message.usage` fields and `tool_use` blocks. The baseline is recorded for one real forge development session before and after the methodology is installed. It is aggregate only and never prints content.

### D10. Tool assessments (initial catalog)
| Tool | Classification | Reason |
|---|---|---|
| Claude Code, OpenSpec, Engram | Required | Core runtime, specs and memory |
| Gentle AI 4.x | Deferred | Imposes ODD, automatic commits and ~80 KB of always-on context even in its minimal setup (isolated test) |
| `sdsrss/code-graph-mcp` | Experimental, deferred | Local, plugin-based, incremental (BLAKE3), MIT. Windows not stated. Needs an accuracy/token test in its own change |
| `denzharkov/codegraph-mcp` | Rejected | Its installer sets `ANTHROPIC_BASE_URL` to a local proxy that rewrites conversation content, and adds blocking hooks. Unacceptable data-path change; 1 star |
| Graphiti | Rejected for now | Needs a graph DB plus LLM/embedding APIs. Engram and repo artifacts cover current needs |
| GGA | Optional, deferred | Complements in-session review at commit time. Sends code to a provider. Per-repo opt-in only |
| Context7 | Optional, deferred | Documentation MCP. Adopt only if doc-lookup misses are observed |
| Gentle Shell | Deferred | Requires the Pi runtime, so it would be a second orchestration layer |

### D11. Project-init templates
These live in `skills/project-init/templates/`:
- an `AGENTS.md` project template, plus a `CLAUDE.md` that imports it
- an ADR template
- `.engram/config.json`
- a decision log

`openspec init` is offered, not run, unless the user asks.

### D12. Plugin file reads pre-approved per skill (found in verification, task 7.3)
The headless `project-init` run showed that reads of `${CLAUDE_PLUGIN_ROOT}/manual/...` are outside the project's working directory, so Claude Code denies them (or prompts in interactive sessions). Skills that read plugin files declare `allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)`. A probe confirmed the variable is substituted in frontmatter and the read succeeds. The grant is read-only, limited to the plugin, and lasts only for the invoking turn.
*Rejected:* a user-level `Read` allow rule for the plugin path. It is broader in time, depends on the install location, and contradicts "no allow rules" in the installer.
Subagents (`architect`, `security-reviewer`) cannot pre-approve. In interactive sessions their manual reads may prompt; the parent can pass the relevant excerpt instead.

## Risks / Trade-offs

- [Engram 3.x API differs from the protocol rule] → The rule names only tools verified against the installed version after the upgrade. Validator checks the names.
- [No Engram lifecycle hooks, so the agent may forget to save] → The memory rule plus the workflow skills' handoff step. The official Engram plugin remains the documented fallback.
- [Hook evasion by obfuscation] → Documented. Optional permissions add a second layer.
- [False positives blocking work] → `deny` only for unambiguous cases. Negative tests use legitimate commands.
- [Python missing or Store alias] → Multi-candidate launcher, doctor check, fail-open documented.
- [Manual grows stale or bloated] → Normative levels, OpenSpec for MUST changes, line checks in the validator.
- [Existing Engram DB holds September data from another agent setup] → Not modified. Isolation tests use synthetic `forge-fixture-*` projects only.

## Migration Plan

This is a fresh install. Rollback paths:
- forge `uninstall` or `restore <timestamp>`
- `claude plugin uninstall forge`
- `claude mcp remove engram --scope user`, done by forge uninstall if forge added the entry
- Restore `~/.engram` from its pre-upgrade backup if the Engram 3.4.0 upgrade misbehaves
