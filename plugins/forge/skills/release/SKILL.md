---
name: release
description: Prepare a release - inspect git state, review changes and tests, identify risks and pending requirements, draft notes and the exact publish steps, then STOP for approval before any push, tag, release or deploy. Use when the user wants to ship, tag, publish or deploy.
argument-hint: "[version or target]"
---

# Release workflow

## Steps
1. **Check git state.** Run `git status`, find the current branch, compare with upstream (`git fetch` is fine), and list the commits since the last tag (`git log <last-tag>..HEAD --oneline`).
2. **Review the changes.** Read the diff since the last release.
   - Flag breaking changes, migrations, config or env changes, and dependency updates.
   - In OpenSpec projects, list archived and active changes. An active, unarchived change is a release blocker unless the user decides otherwise.
3. **Verify.** Run the full test suite, lint and build (`/forge:verify-changes`), and the security scans the project has. Report actual results.
4. **Assess risk and pending work.**
   - Migrations and their rollback.
   - Feature flags.
   - Required secrets or config in the target environments.
   - Known issues.
   - Monitoring for the new behavior.
5. **Prepare.**
   - Propose the version number (semver from the change types).
   - Draft the changelog and release notes.
   - Write the exact commands for tag, push, release creation and deploy, in order, plus the rollback commands.
6. **STOP. Wait for explicit approval.**
   - Present steps 1-5 and wait.
   - Do not run `git push`, `git tag`, `gh release create`, `npm publish` or any deploy command until the user approves that specific action now.
   - Approval of earlier steps or plans does not count. The forge guard also asks before these commands.
7. **Execute only the approved actions,** one at a time. Verify each one: the tag exists, CI is green, the deployment health check passes.
8. **Record.** Run `mem_save` with the release version, any notable issues, and the rollback steps.

## Verification
- Tests and build ran on the exact commit being released.
- Release notes list breaking changes and migrations.
- No publish or deploy command ran before explicit approval in this session.
- Post-release health was checked, or "not verified" is stated.
