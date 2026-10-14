# Tool catalog

Evidence-based evaluations of agent and engineering tools. Evaluation criteria, classification levels and the installation policy are defined in [the catalog index](README.md).

## Agent configuration

### Gentle AI

- **Category:** agent-configuration
- **Classification:** Deferred
- **Purpose:** Configures coding agents (Claude Code and 16 others) with memory wiring, skills, review agents, persona and permissions.
- **Evidence (2026-10-14):**
  - Installed binary is 3.7.0. The latest release is v4.1.1 (2026-10-12).
  - The v4.0.0 release notes state that ODD is the only development workflow and that SDD and OpenSpec are retired. Source: <https://github.com/Gentleman-Programming/gentle-ai/releases/tag/v4.0.0>.
  - An isolated install of v4.1.1 used a temp `HOME`, `CLAUDE_CONFIG_DIR` and `GENTLE_AI_HOME`, with `install --agent claude-code --preset custom --components engram --persona custom`. With only the `engram` component selected, it still wrote:
    - `~/.claude/CLAUDE.md`: 534 lines, about 80 KB, always loaded. It contains managed blocks `engram-protocol`, `orchestrator` and `agent-routing`. The orchestrator makes ODD mandatory, creates `odd/tasks/*.md` feature documents and commits each task automatically on a feature branch.
    - Nine review agents in `~/.claude/agents/` (`review-*`, `jd-*`).
    - `settings.json` hooks:
      - a `SessionStart` and `Stop` review stop-hook;
      - async telemetry on `Stop` and `SubagentStop`;
      - a `UserPromptSubmit` skill-registry refresh on every prompt.
    - `~/.claude.json` with `mcpServers.engram`, set to `engram.exe mcp --tools=agent`.
  - `install --dry-run` listed no files and still wrote `state.json` under `GENTLE_AI_HOME`.
- **Conflicts with this system:**
  - ODD replaces OpenSpec SDD.
  - Automatic commits contradict the approval policy.
  - About 80 KB of always-loaded context contradicts the token budget.
  - A second set of review agents overlaps with `tenet`.
- **Alternatives:** wire Engram directly through the Claude Code CLI (same MCP entry), or use Engram's own Claude Code plugin.
- **Installation state:** 3.7.0 binary present, no agents configured (`state.json` reports none).
- **Lifecycle:** not adopted. If adopted later, remove it with `gentle-ai uninstall --agent claude-code`. Gentle AI takes snapshots under `~/.gentle-ai/backups/`.

## Persistent memory

### Engram

- **Category:** persistent-memory
- **Classification:** Required
- **Purpose:** Local SQLite memory for agents, exposed over MCP. It provides `mem_current_project`, `mem_context`, `mem_search`, `mem_get_observation`, `mem_save`, `mem_session_start`, `mem_session_summary` and related tools.
- **Evidence (2026-10-14):**
  - Installed version is 2.1.0. The latest is v3.4.0.
  - v3.0.0 requires `expected_project` for updates and deletes and moves the module path to `/v3`. Source: <https://github.com/Gentleman-Programming/engram/releases/tag/v3.0.0>.
  - The Claude Code setup options are:
    - The official plugin, `engram setup claude-code`. It needs `jq` and `curl` and adds session hooks.
    - A bare MCP server, `claude mcp add --scope user engram -- <engram> mcp --tools=agent`. It needs no hooks.

    Source: <https://github.com/Gentleman-Programming/engram/blob/main/docs/AGENT-SETUP.md>.
  - Projects resolve from `.engram/config.json` (nearest wins) or from the cwd. When the project is ambiguous, writes return `ambiguous_project`.
- **Alternatives:** Graphiti (rejected: needs a graph database plus LLM APIs). Claude Code auto memory is per-repository and has no search tools.
- **Installation state:** 2.1.0 binary at the user's local app data. The database exists. It is not wired to Claude Code.
- **Lifecycle:** check with `engram doctor` and `claude mcp list`; update by reinstalling the release binary; remove with `claude mcp remove engram --scope user`.

## Agent runtimes and specification

### Claude Code

- **Category:** agent-runtime
- **Classification:** Required
- **Purpose:** Primary coding agent (CLI and VS Code extension). Hosts the plugins, skills, subagents, hooks and MCP servers.
- **Evidence (2026-10-14):** CLI 2.1.296 and VS Code extension 2.1.299 are installed. Docs: <https://code.claude.com/docs/en/plugins-reference>, <https://code.claude.com/docs/en/sub-agents>, <https://code.claude.com/docs/en/hooks>.
- **Alternatives:** other agents (Codex, OpenCode, Cursor). Out of scope.
- **Installation state:** installed natively under the user's local bin directory, which is not on `PATH` in every shell.
- **Lifecycle:** check with `claude --version` and `claude plugin validate`; update with `claude update`.

### OpenSpec

- **Category:** specification
- **Classification:** Required
- **Purpose:** Spec-driven change lifecycle (proposal, specs, design, tasks, archive) and `/opsx:*` commands for Claude Code.
- **Evidence (2026-10-14):** 1.14.1 installed via npm. Docs: <https://openspec.dev/docs/installation>, <https://openspec.dev/docs/cli>. Sends anonymous usage telemetry by default; opt out with `OPENSPEC_TELEMETRY=0` or `openspec config set telemetry.enabled false`.
- **Alternatives:** Gentle AI ODD documents (rejected with Gentle AI); plain ADRs and issues.
- **Installation state:** installed globally; initialized per project only on request.
- **Lifecycle:** check with `openspec --version` and `openspec validate --all --strict`; update with `npm install -g @fission-ai/openspec@latest`, then `openspec update` per project; remove with `npm uninstall -g @fission-ai/openspec`.

## Code intelligence (code graphs)

### code-graph-mcp (sdsrss)

- **Category:** code-graph
- **Classification:** Experimental
- **Purpose:** Local AST graph with call graphs, route tracing, impact analysis and optional local embeddings, exposed as MCP tools and as a Claude Code plugin.
- **Evidence (2026-10-14):** <https://github.com/sdsrss/code-graph-mcp>. MIT, 84 stars, about 1.5k commits. Incremental indexing with BLAKE3. Embeddings run locally (about 120 MB model). The README does not state Windows support.
- **Alternatives:** built-in search (Grep/Glob) plus an `explorer` subagent; LSP plugins.
- **Installation state:** not installed.
- **Lifecycle:** evaluate in its own OpenSpec change. Measure accuracy, incremental reindex and tokens saved with `scripts/session_metrics.py` before adopting.

### codegraph-mcp (denzharkov)

- **Category:** code-graph
- **Classification:** Rejected
- **Purpose:** Local code graph MCP server with notes and semantic search.
- **Evidence (2026-10-14):** <https://github.com/denzharkov/codegraph-mcp>. Its installer sets `ANTHROPIC_BASE_URL` to a local proxy that rewrites conversation content before it reaches the API, and adds `PreToolUse` hooks that can block `Read` and `Bash`. 1 star, no releases.
- **Alternatives:** code-graph-mcp (sdsrss).
- **Installation state:** not installed.
- **Lifecycle:** not applicable.

## Knowledge graphs

### Graphiti

- **Category:** knowledge-graph
- **Classification:** Rejected
- **Purpose:** Temporal knowledge graph framework for agent memory, with an MCP server.
- **Evidence (2026-10-14):** <https://github.com/Memory-Agents/graphiti>. Requires a graph database (Neo4j, FalkorDB or Kuzu) plus LLM and embedding APIs for ingestion. Apache-2.0.
- **Alternatives:** Engram plus repository artifacts (adopted).
- **Installation state:** not installed.
- **Lifecycle:** revisit only if a demonstrated cross-entity reasoning need is not served by Engram.

## Review and documentation

### Gentleman Guardian Angel (GGA)

- **Category:** code-review
- **Classification:** Optional
- **Purpose:** AI review of staged files at commit time, through a git pre-commit hook. Its config has `PROVIDER`, file patterns and a rules file.
- **Evidence (2026-10-14):** <https://github.com/Gentleman-Programming/gentleman-guardian-angel>. 2.10.1 installed. It sends file contents to the configured provider (local providers such as Ollama are possible), caches unchanged files, and has CI and PR modes.
- **Alternatives:** the in-session `review-code` skill and `reviewer` agent; CI static analysis.
- **Installation state:** binary installed; no hooks in any repository.
- **Lifecycle:** opt in per repository with `gga install` (the guard asks for approval); remove with `gga uninstall`. Verify that existing hooks are preserved before adopting.

### Context7

- **Category:** documentation
- **Classification:** Deferred
- **Purpose:** MCP server that returns version-specific library documentation.
- **Evidence (2026-10-14):** offered as an optional Gentle AI component. Not evaluated in isolation.
- **Alternatives:** WebFetch of official docs, used by the `research-technology` skill.
- **Installation state:** not installed.
- **Lifecycle:** adopt only if documentation lookups demonstrably miss or cost too many tokens.

### Gentle Shell

- **Category:** agent-runtime
- **Classification:** Deferred
- **Purpose:** Coding-agent shell on the Pi runtime with ODD, subagents and native review.
- **Evidence (2026-10-14):** <https://github.com/Gentleman-Programming/gentle-shell>. Requires the Pi coding agent. Windows installer candidates are not release-qualified (per the Gentle AI v4.1.0 notes).
- **Alternatives:** Claude Code with tenet (adopted).
- **Installation state:** not installed.
- **Lifecycle:** not applicable; adopting it would mean a second orchestration layer.

## Agent runtimes for deployed agents

### Forge (initializ)

- **Category:** agent-runtime
- **Classification:** Optional
- **Purpose:** Open-source Go runtime that compiles a `SKILL.md` into a hardened, deployable agent. It runs in containers, Kubernetes, CI or as an A2A endpoint, with egress allowlists, encrypted secrets, audit logs, channels (Slack, Telegram) and cron.
- **Evidence (2026-10-14):** <https://github.com/initializ/forge>. Apache-2.0, 246 stars, v0.19.0. Releases are built with GoReleaser: 6 OS/arch archives plus `checksums.txt`, a multi-arch GHCR image and a Homebrew tap. Its name collided with this project's first name, which led to the rename to tenet.
- **Alternatives:** Claude Agent SDK; Claude Managed Agents.
- **Installation state:** not installed.
- **Lifecycle:** evaluate per project only when an agent must run as a service outside an interactive Claude Code session. It is a different problem from tenet's.
