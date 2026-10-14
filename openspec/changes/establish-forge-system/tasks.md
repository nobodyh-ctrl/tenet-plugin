# Tasks

## 1. Repository base and plugin skeleton

- [x] 1.1 Create `.gitignore` (incl. `local/`, `__pycache__/`), `LICENSE` (MIT), `AGENTS.md` (repo dev instructions) and `CLAUDE.md` importing it; verify `git status --ignored` shows `local/` ignored
- [x] 1.2 Create `.claude-plugin/marketplace.json` and `plugins/forge/.claude-plugin/plugin.json`; verify with `claude plugin validate .` and `claude plugin validate plugins/forge`

## 2. Gentle AI footprint and Engram wiring decision (gate)

- [x] 2.1 Fetch Gentle AI 4.x docs/release notes and the Engram DOCS memory protocol; record verified tool names and install footprint in `plugins/forge/manual/catalog/tools.md`; verify entries cite sources and dates
- [x] 2.2 Run Gentle AI `install --dry-run` (custom preset, engram component, persona custom) with HOME/USERPROFILE pointed at a temp dir after upgrading only in a temp location if possible; record which files it would write; verify none overlaps forge-owned surfaces (D1) — if any does, stop and update design
- [x] 2.3 Record the user's decision (no Gentle AI; direct Engram wiring via `claude mcp`; adopt ODD sizing and delegation ideas as forge rules) in proposal, design and specs; verify `openspec validate establish-forge-system --strict`

## 3. Validator and secret scan

- [x] 3.1 Implement `scripts/validate.py` (JSON/YAML, manifests, frontmatter, hooks.json, links, agent privilege table, rule budget, manual/catalog structure, plugin-root CLAUDE.md); verify exit 0 on the repo
- [x] 3.2 Implement secret/private-data scanning with synthetic-fixture allowlist; verify tests detect PEM key, AWS key, token, `C:\Users\<name>` and private product names
- [x] 3.3 Write `tests/test_validate.py` (valid repo + broken copies: missing description, name mismatch, `..` source, non-implementer with Edit, oversize rules); verify `python -m unittest tests.test_validate`

## 4. Guard hook

- [x] 4.1 Implement `hooks/policy.json`, `guard.py`, `run-guard.sh`, `hooks.json`; verify `claude plugin validate plugins/forge`
- [x] 4.2 Write `tests/test_guard.py` (deny, ask, legitimate no-decision, reviewer read-only with and without `forge:` prefix, secret files, invalid JSON, messages without full command); verify `python -m unittest tests.test_guard`
- [x] 4.3 Run `run-guard.sh` end-to-end in Git Bash with a sample `rm -rf /` payload; verify JSON `deny` output
- [x] 4.4 Write `docs/security.md` and `SECURITY.md` (threat model, technical vs prose controls, fail-open, limits); verify validator link check passes

## 5. Global methodology rules

- [x] 5.1 Write `global-config/rules/core.md`, `sdd.md`, `memory.md`, `delegation.md`, `tokens.md`, `autonomy.md` and `global-config/templates/profile.md` (generic); verify validator budget (≤120 lines) and required-clause checks
- [x] 5.2 Write `docs/configuration.md` (plugin vs user rules vs profile vs project config vs Gentle AI/Engram/OpenSpec ownership); verify link check

## 6. Engineering Manual and tool catalog

- [x] 6.1 Write `manual/README.md` and `core/`, `delivery/`, `security/`, `providers/aws.md` with normative markers; verify validator index, marker and provider-isolation checks
- [x] 6.2 Write `manual/catalog/technologies.md` (initial entries for the user's current stacks) and complete `catalog/tools.md` with the ten assessed tools; verify entry-field checks

## 7. Engineering workflows

- [x] 7.1 Write `plan-work`, `implement`, `review-code`, `verify-changes`, `documentation`, `devops-iac` (with references); verify validator
- [x] 7.2 Write `feature`, `bugfix`, `release` skills; verify validator and a test that finds the release stop step
- [x] 7.3 Write `project-init` with templates (AGENTS.md, CLAUDE.md, ADR, `.engram/config.json`, decision log); verify validator and a dry walkthrough on a synthetic fixture repo under `tests/fixtures/` that lists files without writing

## 8. Learning workflows

- [x] 8.1 Write `learn-concept`, `hands-on-lab`, `research-technology`, `aws-security`, `networking-lab`, `study-topic`; verify validator section checks (diagnostic, checkpoint/skip, lab sections, research sections, progress storage)

## 9. Agents

- [x] 9.1 Write `architect`, `explorer`, `implementer`, `reviewer`, `security-reviewer`, `tutor`; verify validator privilege table and `claude plugin validate plugins/forge`

## 10. Installer and metrics

- [x] 10.1 Implement `scripts/agentcfg.py` (install/uninstall/restore/status, dry-run, manifest, backups, atomic writes, path and symlink checks, forge-owned permissions, optional plugin registration, optional Engram MCP wiring via `claude mcp add/remove` with conflict detection, prerequisite report)
- [x] 10.2 Implement `installers/*.ps1` and `*.sh` wrappers; verify dry-run against a temp `CLAUDE_CONFIG_DIR` in PowerShell and Git Bash
- [x] 10.3 Write `tests/test_installer.py` (dry-run no writes, idempotency, profile preserved, foreign config incl. fake third-party MCP entries intact, Engram wiring skipped on a mismatched existing entry, byte-identical restore, invalid path, symlink, foreign file conflict, missing tools); verify `python -m unittest tests.test_installer`
- [x] 10.4 Implement `scripts/session_metrics.py` and `scripts/doctor.py` with tests on synthetic transcripts and temp dirs (exact totals, unavailable usage, no content leak, doctor read-only); verify `python -m unittest`
- [x] 10.5 Write `docs/installation.md` and `docs/troubleshooting.md`; verify documented flags match `agentcfg.py --help`

## 11. Public docs and CI

- [x] 11.1 Write `README.md` (short English intro; architecture diagram; install for Windows/Linux; using skills/agents; SDD + OpenSpec cycle; memory; update; uninstall), `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/development.md`; verify validator (links, secret scan)
- [x] 11.2 Create `.github/workflows/ci.yml`; verify YAML validity and a test asserting no `secrets.`
- [x] 11.3 Run `python scripts/validate.py`, the full unittest suite, `claude plugin validate --strict` (marketplace and plugin) and `openspec validate establish-forge-system --strict`; record results
- [x] 11.4 Install marketplace + plugin with the real CLI into a temp `CLAUDE_CONFIG_DIR`; verify `claude plugin details forge` (16 skills, 6 agents, hooks) and that real `~/.claude` hashes are unchanged
- [x] 11.5 Record a usage-metrics baseline from an existing session transcript; verify the report contains only aggregates

## 12. Personal installation (each step requires explicit approval)

- [x] 12.1 Back up `~/.engram`, upgrade Engram to 3.4.0 with the official method, and wire it with the installer's `--with-engram`; verify `engram doctor`, `engram version` and `claude mcp list` showing `engram`
- [x] 12.2 Run the forge installer dry-run against real `~/.claude`, show it, get approval, then install with `--with-plugin`; verify `doctor.py`, `claude plugin list` and a controlled hook test in a real session
- [x] 12.3 Fill the private profile with the user's stated technical context; verify it is outside the repository
- [x] 12.4 Run the Engram cross-session retrieval and isolation checks with synthetic `forge-fixture-*` projects; record passed/failed/blocked

## 13. Rename to forge and migrate the existing install

- [x] 13.1 Replace every previous-name identifier (`facundo` + `-agent-config`) with `forge` (marketplace, installer paths, docs, specs, tests); verify a repository-wide grep for the old name finds nothing outside git history, then run the validator, the test suite, `claude plugin validate --strict` and `openspec validate --strict`
- [x] 13.2 Verify an isolated install of `forge@forge` with the real CLI (16 skills, 6 agents, hook) and that the real `~/.claude` is unchanged
- [x] 13.3 With explicit approval, migrate the user's install: uninstall the old one with the previous installer (keeping the profile), move the profile to `rules/forge/`, then install `forge@forge` with Engram wiring; verify with `doctor.py`, `claude plugin list` and `claude mcp get engram`

## Workflow follow-up

- Present results and wait for approval before `/opsx:archive establish-forge-system`.
- After archiving, verify `openspec/specs/` contains the 12 capabilities.
- Later changes: evaluate `code-graph-mcp`, GGA per-repo adoption, Context7; Gentle AI stays Deferred.
