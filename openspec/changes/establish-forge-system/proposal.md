# Proposal

## Why

Each new project starts without a shared engineering methodology, persistent memory, or technical guardrails for Claude Code. The tools that could provide parts of this (Engram 2.1.0, Gentle AI 3.7.0, GGA 2.10.1, OpenSpec 1.14.1) are installed but disconnected: Claude Code has no MCP servers and Gentle AI reports no configured agents. An isolated install of Gentle AI 4.1.1 showed that even its minimal configuration imposes its own ODD workflow (replacing OpenSpec), automatic per-task commits and about 80 KB of always-loaded instructions, so it is not adopted. We need the smallest coherent system that connects them without duplicating what each tool already owns, and that adds the methodology, Engineering Manual and project onboarding that none of them provides.

## What Changes

- `forge` plugin in a marketplace owned by this repo, providing the following components:
  - Engineering skills: `plan-work`, `implement`, `review-code`, `verify-changes`, `documentation`, `devops-iac`.
  - Workflow skills: `feature`, `bugfix`, `release`, `project-init` (onboarding a new or existing repo).
  - Learning skills: `learn-concept`, `hands-on-lab`, `research-technology`, `aws-security`, `networking-lab`, `study-topic`.
  - Agents: `architect`, `explorer`, `implementer`, `reviewer`, `security-reviewer`, `tutor`.
  - A `PreToolUse` guard hook that denies clearly destructive commands, asks on risky ones, and enforces read-only Bash for the reviewer agents.
- Global methodology as short user-level rules: context discovery, SDD/OpenSpec policy, task sizing, the Engram memory lifecycle, delegation and orchestration, token efficiency, verification, and autonomy limits. The rules are installed into `~/.claude/rules/forge/`.
- Engineering Manual, versioned and loaded on demand by skills. It covers core engineering, delivery/infrastructure, security, a technology catalog, and a tool catalog. Each item is marked mandatory, recommended, or experimental. AWS is the first cloud reference; the principles stay provider-agnostic.
- Engram integration wired directly through the native `claude mcp add` CLI. This is an opt-in installer flag that detects conflicts with existing entries. Forge owns a compact memory protocol rule and a verification procedure using synthetic data.
- Gentle AI is not used. Two of its ideas are adopted as forge rules: sizing tasks by whether they can be resumed from the request and the diff, and delegating only when there is evidence it helps.
- Usage metrics script that reads real Claude Code transcript usage data to measure tokens, tool calls, repeated reads, and subagent use.
- Complementary installer with PowerShell and Bash entry points over a Python core. It supports dry-run, backups, an ownership manifest, idempotency, selective uninstall, and restore. It never installs third-party tools on its own.
- Validators, a `unittest` suite, a secret scan, and GitHub Actions CI with no credentials.

**Out of scope (deferred to later changes, recorded in the tool catalog):**
- Code-graph MCP adoption. `sdsrss/code-graph-mcp` is the candidate.
- GGA hooks in real repositories.
- Context7.
- Graphiti or other graph memory.
- Gentle Shell / Pi.
- Model routing.
- Publishing to GitHub.
- Any work on the user's existing private products.

## Capabilities

### New Capabilities
- `plugin-distribution`: marketplace and `forge` plugin manifest, component layout, native install.
- `agent-methodology`: global rules for discovery, SDD policy, delegation, token efficiency, verification and autonomy.
- `engineering-workflows`: engineering skills plus `feature`, `bugfix`, `release` and `project-init` workflows.
- `learning-workflows`: staged learning skills with comprehension checks and progress tracking.
- `specialist-agents`: subagent definitions, least-privilege tools, handoff and output contracts.
- `security-guardrails`: guard hook policy, secret-file protection, reviewer read-only enforcement.
- `persistent-memory`: Engram wiring, usage protocol, isolation rules and cross-session verification.
- `engineering-manual`: structure, normative levels, and evolution rules of the manual.
- `tool-catalog`: tool evaluation criteria, classification, and recorded assessments.
- `usage-metrics`: measurement of token and tool usage from real session data.
- `complementary-installer`: install/uninstall/restore of user-level rules, profile and optional permissions.
- `repo-validation`: structural validators, secret scan, tests and CI.

### Modified Capabilities
<!-- None: no existing specs. -->

## Impact

- **New files only in this repository.** OpenSpec's generated `.claude/` files are kept.
- **User configuration, only after explicit approval in the installation phase:**
  - Engram upgrade to 3.4.0 (after backing up `~/.engram`) and its user-scope MCP entry.
  - `~/.claude/rules/forge/`.
  - Plugin and marketplace entries written by the Claude Code CLI.
  - Optional permission rules.
- **Dependencies:** Python 3.9+, Claude Code ≥ 2.1 and Engram ≥ 3.4 (recommended). OpenSpec is optional per project. Gentle AI is not required.
