---
name: verify-changes
description: Identify and run the checks that prove a change works (tests, lint, types, build, OpenSpec validation, acceptance scenarios) and report real results. Use before claiming any task or change is done.
---

# Verify changes

## When to use
- Before saying "done".
- Before archiving an OpenSpec change.
- After fixing review findings.

## Steps
1. **Discover the project's checks.** Look in its instructions, package scripts, Makefile, CI workflow, `*.csproj`, `pyproject.toml`, `package.json` and pre-commit config. Prefer the commands CI runs.
2. **Map acceptance criteria to evidence.** For OpenSpec changes, read each scenario in the change's specs and identify the test or command that proves it. A scenario with no check is a gap.
3. **Run checks from narrow to broad.** Start with the affected tests, then the full suite, lint, type checks and build. Run only commands that read or test locally. Ask before anything that installs packages, migrates real data or touches remote systems.
4. **Validate OpenSpec.** Run `openspec validate <change> --strict`. Confirm every task in `tasks.md` is ticked only where there is evidence.
5. **Report honestly.** Give each check one of these results, with the exact command and the key output lines:
   - **passed**
   - **failed**
   - **not executed**, with the reason
   - **blocked**, naming the missing tool or permission
6. **On failure,** stop and diagnose, or hand the work back to `implement`. Never weaken a test to make it pass.

## Output
A table with these columns, then the uncovered scenarios and the next step:

| check | command | result | evidence |
|---|---|---|---|

## Verification
- No check is reported as passed unless it ran in this session.
- Every acceptance criterion is either covered by evidence or listed as a gap.
