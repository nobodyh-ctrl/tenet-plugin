# Proposal

## Why

forge is ready for other people to try, but nothing marks it as pre-release, explains what this version contains, or lets a user check the installed version from inside a session. A first public beta needs:

- an explicit pre-release version;
- release notes;
- a version command that users can quote when they report problems.

## What Changes

- Version `0.1.0-beta.1` in `plugin.json` and the marketplace entry. The beta status is visible in the version string.
- `/forge:version` skill. It runs only when the user invokes it and reports:
  - the plugin version and release channel, read from the plugin manifest;
  - the commands that show the full install state.
- `python scripts/agentcfg.py --version` prints the version of the checked-out repository.
- Release notes in `docs/releases/v0.1.0-beta.1.md`: what the version includes, known limitations, how to install, try and report feedback. A matching `CHANGELOG.md` section.
- A local release tag created with the native `claude plugin tag`, named `forge--v0.1.0-beta.1`.
- Branding: the banner uses the orange forge palette. This is editorial and has no spec impact.

**Out of scope:**
- Creating the GitHub repository and pushing. This needs a remote and the user's explicit approval at that moment; the notes file is ready for `gh release create --prerelease --notes-file`.
- Automated release pipelines.
- Update notifications.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `plugin-distribution`: adds version reporting and pre-release versioning, and the skill inventory grows from 16 to 17.

## Impact

- Files: `plugins/forge/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, a new `skills/version/`, `scripts/agentcfg.py`, `scripts/validate.py`, tests, `docs/releases/`, `CHANGELOG.md`, `README.md`.
- Installed users get the new version after `claude plugin update forge@forge`. Local-path installs read the files in place.
