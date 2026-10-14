# facundo-agent-config — development instructions

Engineering system for Claude Code: the `forge` plugin, user-level methodology rules, the Engineering Manual and a complementary installer.

## Layout

- `.claude-plugin/marketplace.json`: the marketplace (`facundo-agent-config`).
- `plugins/forge/`: the plugin, containing `skills/`, `agents/`, `hooks/` and `manual/` (the Engineering Manual and catalogs).
- `global-config/`: rules and profile template that the installer copies to `~/.claude/rules/facundo-agent-config/`.
- `installers/`: PowerShell and Bash wrappers over `scripts/agentcfg.py`.
- `scripts/`: `validate.py`, `doctor.py`, `session_metrics.py`.
- `tests/`: stdlib `unittest`, run against temp dirs only.
- `openspec/`: specs and changes. This repo is developed with SDD.

## Rules for working on this repo

- Meaningful behavior changes go through OpenSpec: `/opsx:propose`, then review and approval, then `/opsx:apply`, then `openspec validate --strict`, then `/opsx:archive`. Editorial fixes and behavior-neutral refactors don't need a change.
- Artifacts, docs, skills and agents are written in English.
- Never touch the real `~/.claude` in tests. Use `CLAUDE_CONFIG_DIR` or `--config-dir` with a temp dir.
- Never commit local user paths, secrets, or details of private products. `scripts/validate.py` scans for them.
- Do not write files owned by Gentle AI, Engram or OpenSpec (see `docs/configuration.md`).

## Verify before claiming done

```bash
python scripts/validate.py
python -m unittest discover -s tests
claude plugin validate . && claude plugin validate plugins/forge
openspec validate --all --strict
```
