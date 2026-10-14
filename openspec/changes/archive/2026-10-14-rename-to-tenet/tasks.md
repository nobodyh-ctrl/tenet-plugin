# Tasks

## 1. Rename

- [x] 1.1 Save the pre-rename installer for migration, `git mv plugins/forge plugins/tenet`, and replace identifiers with Python (not sed) everywhere except `openspec/changes/archive/`. Verify with a case-insensitive grep that the only remaining `forge` mentions are the intentional initializ/forge references
- [x] 1.2 Update the living-spec `Purpose` sections that name the product, and redesign the banner wordmark as TENET in orange. Verify by rendering the banner and running `openspec validate --specs --strict`
- [x] 1.3 Run the validator, the test suite, `claude plugin validate --strict` (marketplace and plugin) and `openspec validate rename-to-tenet --strict`; all must pass
- [x] 1.4 Install `tenet@tenet` into a temporary `CLAUDE_CONFIG_DIR` with the real CLI. Verify 17 skills, 6 agents and the hook, and that the real `~/.claude` hashes are unchanged

## 2. Release pipeline

- [x] 2.1 Implement `scripts/build_release.py` (assets, checksums, tag/version check, `--print-prerelease`) with tests in `tests/test_release.py`. Verify with `python -m unittest tests.test_release`
- [x] 2.2 Add `.github/workflows/release.yml` and contract tests for trigger, ordering, notes file and secrets. Verify YAML validity with PyYAML and run the tests
- [x] 2.3 Document the release process in `docs/development.md` and add the initializ/forge comparison to the tool catalog. Verify the validator's link checks

## 3. Release tag and migration

- [x] 3.1 Commit, delete the unpushed local tag `forge--v0.1.0-beta.1`, and run `claude plugin tag plugins/tenet`. Verify that `git tag -l` shows only `tenet--v0.1.0-beta.1`
- [x] 3.2 Build the release assets locally from the tag. Verify the checksums, and load the plugin zip with `claude --plugin-dir` in a headless `/tenet:version` run
- [x] 3.3 With explicit approval, migrate the local install from forge to tenet, keeping the profile. Verify with `doctor.py`, `claude plugin list` and `claude mcp get engram`

## Workflow follow-up

- Publishing (`gh repo create tenet`, push, push tag) needs explicit approval at that moment. The workflow then creates the GitHub release.
- Archive this change after approval.
