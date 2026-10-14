# Proposal

## Why

`initializ/forge` is an established open-source agent runtime with 246 stars, Apache-2.0, a commercial company and a domain behind it. It sits in the same ecosystem (Claude, `SKILL.md`) and has a `.claude/skills/forge.md` of its own. Keeping the name `forge` would confuse users and searches. Separately, publishing the beta needs a repeatable release process with downloadable assets.

## What Changes

- **BREAKING:** rename the product from `forge` to `tenet` everywhere:
  - repository, marketplace and plugin;
  - install id `tenet@tenet`;
  - commands `/tenet:<skill>`;
  - user rules in `~/.claude/rules/tenet/`, state in `~/.claude/tenet/`, backups in `~/.claude/backups/tenet/`;
  - guard messages and the `tenet:` agent prefix;
  - banner, docs and specs.

  Archived changes are left as history.
- Version stays `0.1.0-beta.1`, since nothing was published. The unpushed local tag `forge--v0.1.0-beta.1` is replaced by `tenet--v0.1.0-beta.1`.
- New `scripts/build_release.py`. It builds `tenet-plugin-<version>.zip`, `tenet-<version>.zip` and `checksums.txt`, validates the tag against `plugin.json`, and reports whether the version is a pre-release.
- New `.github/workflows/release.yml`. On `tenet--v*` tags it validates, tests, builds the assets, and creates the GitHub release with the notes file, marked as a pre-release for `-beta` versions.
- One-time migration of the existing local install, with approval: uninstall the forge install keeping the profile, move the profile, install tenet.

**Out of scope:**
- Docker image. tenet is files installed into Claude Code, not a service, so a container has nothing to run.
- Homebrew or other package managers.
- Rolling `vnext` prereleases.
- Creating the GitHub repository or pushing. Those need approval when they happen.

## Capabilities

### New Capabilities
- `release-pipeline`: deterministic release assets, tag-triggered publishing, pre-release marking.

### Modified Capabilities
- `plugin-distribution`: names, install id and version command become `tenet`.
- `complementary-installer`: install paths, manifest location and backups move to `tenet`.
- `persistent-memory`: installer-owned Engram wiring references `tenet`.
- `security-guardrails`: reviewer prefix `tenet:` and tenet-owned permission rules.
- `agent-methodology`: rules folder `~/.claude/rules/tenet/`.

## Impact

- Every file that references the old name, outside archived changes.
- The plugin directory moves from `plugins/forge/` to `plugins/tenet/`.
- Existing installs must migrate once. Only the author's machine has one.
