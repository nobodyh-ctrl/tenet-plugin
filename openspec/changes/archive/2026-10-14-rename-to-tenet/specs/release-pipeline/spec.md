# Spec Delta

## Purpose

Publish reproducible, verifiable GitHub releases of tenet from a version tag, with downloadable assets and release notes, without manual packaging.

## ADDED Requirements

### Requirement: Deterministic release assets
`scripts/build_release.py` SHALL build, from the checked-out repository and without network access:
- `tenet-plugin-<version>.zip`, containing only the plugin directory contents, loadable with `claude --plugin-dir`;
- `tenet-<version>.zip`, containing the git-tracked repository with installers;
- `checksums.txt`, with the SHA-256 of each asset.

#### Scenario: Assets built locally
- **WHEN** `python scripts/build_release.py --out <dir>` runs on a clean checkout
- **THEN** the three files exist, each zip is listed in `checksums.txt` with a matching SHA-256, and the plugin zip has `.claude-plugin/plugin.json` at its root

#### Scenario: Version mismatch rejected
- **WHEN** the script is given `--tag tenet--v9.9.9` while `plugin.json` says another version
- **THEN** it exits non-zero without writing assets

### Requirement: Tag-triggered release workflow
A GitHub Actions workflow SHALL run on pushed tags matching `tenet--v*` (the `claude plugin tag` format). Before publishing, it SHALL run the validator and the test suite. It SHALL then build the assets and create a GitHub release with them, using `docs/releases/v<version>.md` as notes. Only this workflow may use write permissions.

#### Scenario: Workflow contract
- **WHEN** a test reads `.github/workflows/release.yml`
- **THEN** it triggers only on `tenet--v*` tags, runs `scripts/validate.py` and the unit tests before `scripts/build_release.py`, publishes with `--notes-file docs/releases/`, and references no secret other than `GITHUB_TOKEN`

### Requirement: Pre-release marking
A release SHALL be marked as a GitHub pre-release when its version has a semver pre-release suffix (for example `-beta.1`). Otherwise it SHALL be published as a normal release.

#### Scenario: Beta flagged
- **WHEN** `build_release.py --print-prerelease` runs for version `0.1.0-beta.1`
- **THEN** it prints `true`, and for `1.0.0` it prints `false`
