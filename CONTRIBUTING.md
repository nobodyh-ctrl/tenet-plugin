# Contributing

Thanks for helping improve forge.

## Ground rules

- **Behavior changes need an OpenSpec change.** Skills, agents, hook policy, installer, rules and normative manual standards all count. Open an issue first, or include the proposal under `openspec/changes/` in your PR.
- **Keep always-loaded rules tiny.** Detail belongs in skills or the manual.
- **No new dependencies.** Python stdlib, PowerShell and Bash only. MCP servers and external services are out of scope unless a reviewed change adds them.
- **Never commit secrets, local user paths or private project details.** `scripts/validate.py` checks for them.
- **Write in English.** Use conventional commit messages (`feat:`, `fix:`, `docs:`, ...).

## Before opening a PR

```bash
python scripts/validate.py
python -m unittest discover -s tests
openspec validate --all --strict
```

CI runs the same checks on Ubuntu and Windows, plus `shellcheck` and `claude plugin validate --strict`.

See [docs/development.md](docs/development.md) for adding skills and guard rules.
