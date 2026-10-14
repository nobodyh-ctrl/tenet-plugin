# Tasks

## 1. Version reporting

- [x] 1.1 Add `plugins/forge/skills/version/SKILL.md` (user-invoked only, reads `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`); verify with `python scripts/validate.py` and `claude plugin validate plugins/forge --strict`
- [x] 1.2 Add `--version` to `scripts/agentcfg.py`; verify with a unit test asserting the output matches `plugin.json`
- [x] 1.3 Extend the validator (17 skills, `disable-model-invocation` on `version`, release notes and CHANGELOG section for the current version) with tests for the failure cases; verify `python -m unittest discover -s tests`

## 2. Beta release

- [x] 2.1 Set version `0.1.0-beta.1` in `plugin.json` and the marketplace entry; verify `claude plugin validate . --strict`
- [x] 2.2 Write `docs/releases/v0.1.0-beta.1.md` and the CHANGELOG section, and link them from the README; verify the validator's link and release-notes checks
- [x] 2.3 Verify `/forge:version` in a real headless session in an unrelated project: the output contains `0.1.0-beta.1`, the channel `beta`, and there are no permission denials
- [x] 2.4 Commit, then create the local tag with `claude plugin tag plugins/forge`; verify with `git tag -l "forge--v*"`

## Workflow follow-up

- Publishing (`gh repo create`, push, `gh release create v0.1.0-beta.1 --prerelease --notes-file docs/releases/v0.1.0-beta.1.md`) needs explicit user approval at that moment.
- Archive this change after the user approves.
