# Design

## Context

See proposal.md. Reference workflow studied in `initializ/forge` (2026-10-14):
- `release.yaml` runs on `v*` tags and uses GoReleaser to build six OS/arch archives plus `checksums.txt`.
- It also builds a multi-arch GHCR Docker image and updates a Homebrew tap.
- `edge.yaml` republishes a rolling `vnext` prerelease on every push to `main`.

## Goals / Non-Goals

**Goals:**
- A clean rename that leaves no `forge` identifiers outside history.
- Releases that are reproducible locally and in CI, with checksums and a pre-release flag.

**Non-Goals:**
- Binaries, containers or package-manager channels. tenet has no runtime to ship.

## Decisions

### D1. Name `tenet`
It is short, it means the principles a team works by, and a GitHub check found no Claude-related repository with that name. It replaces forge in the repo, marketplace, plugin, paths, prefixes and branding.
*Rejected:* keeping `forge` (collision with initializ/forge); `temper`, `rigor`, `kiln` (the user chose tenet; `kiln` also collides with Kiln AI).

### D2. Release assets built by a stdlib Python script
`build_release.py` zips `plugins/tenet/` as the plugin bundle and `git archive HEAD` as the full bundle, then writes SHA-256 checksums. The same command runs locally and in CI, and the tests run it on the real repository.
*Rejected:* GoReleaser, which is built for compiled binaries and would add a toolchain. *Rejected:* zipping inline in the workflow YAML, which cannot be tested before a real tag push.

### D3. Tag format `tenet--v<version>`
Releases use the tag that `claude plugin tag` creates. It already checks that `plugin.json` and the marketplace agree. The workflow derives the version from the tag, and the script re-checks it against `plugin.json`.
*Rejected:* plain `v*` tags, which would bypass the native consistency check.

### D4. Pre-release from the semver suffix
Any version with a `-suffix` is a pre-release, so `--prerelease` is passed. No manual flag is involved.

### D5. Least-privilege workflow
`permissions: contents: write` is granted only in `release.yml`. The workflow uses only `GITHUB_TOKEN`. Validation and tests must pass before `gh release create`.

### D6. No Docker image
initializ/forge ships a container because its product is a long-running agent service. tenet's product is configuration loaded by the user's own Claude Code, and nothing would run inside a container. A container for CI validation is unnecessary because GitHub runners already have Python.

### D7. Rename mechanics
- Text replacement is done with Python, not `sed -i`. A `sed -i` run deleted `installers/install.ps1` during the previous rename.
- `plugins/forge/` is moved with `git mv`.
- Archived changes under `openspec/changes/archive/` are left untouched as history.
- The `Purpose` sections of living specs that name the product are edited directly, as OpenSpec instructs.
- The unpushed tag `forge--v0.1.0-beta.1` is deleted locally and recreated as `tenet--v0.1.0-beta.1`.

## Risks / Trade-offs

- [Missed occurrences] → After the rename, a case-insensitive grep for `forge` outside the archive must return only intentional mentions: the initializ/forge comparison in docs and the catalog.
- [The user's installed plugin breaks between the rename and the migration] → The migration is run right after verification, in the same session.
- [The workflow is untested until the first real tag push] → Contract tests on the YAML, plus local runs of the same script.

## Migration Plan

1. `python scripts/agentcfg.py uninstall`, run from the pre-rename commit, keeps the profile.
2. Move `~/.claude/rules/forge/profile.md` to `~/.claude/rules/tenet/`.
3. `installers/install.ps1 -WithPlugin -WithEngram`.

Rollback: the uninstall and install backups, or `git checkout` of the previous commit and re-install.
