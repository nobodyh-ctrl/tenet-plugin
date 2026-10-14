# Development

This repository is developed with Spec-Driven Development using OpenSpec.

## Setup

```bash
git clone https://github.com/nobodyh-ctrl/tenet-plugin && cd tenet-plugin
python --version          # 3.9+
openspec --version        # 1.14+ (optional, for changing behavior)
```

To use your working copy as the installed plugin, add the clone as a local marketplace. Edits then take effect on the next session or after `/reload-plugins`:

```bash
claude plugin marketplace add "$(pwd)"
claude plugin install tenet@tenet
```

## Change workflow

- **Behavior changes:** skills, agents, hook policy, installer, rules, normative manual standards. Run `/opsx:propose <change>`, get the proposal reviewed and approved, run `/opsx:apply`, verify, then `/opsx:archive`.
- **Editorial fixes and behavior-neutral refactors:** a direct commit is fine.

## Checks

Run all of these before committing:

```bash
python scripts/validate.py                       # structure, content contracts, links, secret scan
python -m unittest discover -s tests             # hook, installer, validator, metrics, doctor
claude plugin validate . --strict
claude plugin validate plugins/tenet --strict
openspec validate --all --strict
```

The validator also scans for private terms listed in `local/private-terms.txt`, which is git-ignored and holds one term per line. Use it for names of private projects that must never be published.

Test fixtures that contain fake secrets or paths must include the marker `tenet:synthetic-fixture`.

## Adding a skill

1. Create `plugins/tenet/skills/<name>/SKILL.md` with `name` (equal to the folder) and `description` (what it does and when to use it).
2. Include a `## Verification` section, and keep the file under 300 lines. Move long material into `references/`.
3. Reference manual sections as `${CLAUDE_PLUGIN_ROOT}/manual/...` instead of copying them.
4. Add the skill to `SKILLS` in `scripts/validate.py`, plus any content contract it must keep.

## Adding a guard rule

1. Add a rule with a unique `id`, a `decision` (`deny` only for unambiguous destruction, otherwise `ask`), a `pattern` and a `reason` to `plugins/tenet/hooks/policy.json`.
2. Add positive and negative cases to `tests/test_guard.py`, including legitimate commands that must not match.

## Measuring token usage

```bash
python scripts/session_metrics.py                # current project's sessions
python scripts/session_metrics.py --session ~/.claude/projects/<project>/<id>.jsonl --json
```

The script reports recorded usage, tool calls, redundant reads and subagent use. Compare reports before and after a methodology change, and keep the change only if it helps without hurting results.

## Releasing

Releases are cut from tags created by `claude plugin tag`, in the form `tenet--v<version>`.

1. Bump `version` in `plugins/tenet/.claude-plugin/plugin.json` and in the marketplace entry. Use a semver pre-release suffix such as `-beta.2` for test builds.
2. Write `docs/releases/v<version>.md` and add a `## [<version>]` section to `CHANGELOG.md`. The validator enforces both.
3. Build and inspect the assets locally:
   ```bash
   python scripts/build_release.py --out dist
   ```
   This produces:
   - `tenet-plugin-<version>.zip`: the plugin, loadable with `claude --plugin-dir`;
   - `tenet-<version>.zip`: the full repository with installers;
   - `checksums.txt`: SHA-256 of both zips.

   The zips are deterministic, so the same tree gives the same checksums.
4. Commit, then tag with `claude plugin tag plugins/tenet`. It checks that `plugin.json` and the marketplace agree.
5. Push the tag with `git push origin refs/tags/tenet--v<version>`. `.github/workflows/release.yml` then:
   1. validates the repository and runs the tests;
   2. rebuilds the assets and checks the tag against `plugin.json`;
   3. creates the GitHub release with `docs/releases/v<version>.md` as notes.

   Versions with a pre-release suffix are marked as **pre-release** automatically.

There is no Docker image. tenet is configuration loaded by each user's Claude Code, so a container would have nothing to run.
