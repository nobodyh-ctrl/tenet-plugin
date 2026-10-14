---
name: bugfix
description: Workflow to fix a bug - reproduce or characterize it, find the root cause, apply a minimal fix with a regression test, and verify no regressions. Use when the user reports a bug, failing test, error or incorrect behavior.
argument-hint: "[bug description or error]"
---

# Bugfix workflow

## Steps
1. **Recall.** Run `mem_search` for the error message or the component (when Engram is available). Earlier root causes and failed approaches save time.
2. **Reproduce.**
   - Turn the report into a failing test or an exact command, with expected versus actual behavior.
   - If it cannot be reproduced, characterize the conditions (inputs, environment, versions) and say so explicitly.
3. **Locate.**
   - Trace from the symptom to the cause with targeted reads, logs and `git log -S`/`git blame` on suspicious lines.
   - Optional `explorer`: use it only when the cause could be anywhere across a large codebase.
4. **Find the root cause.**
   - State the cause and the evidence for it. Separate the root cause from the trigger.
   - If several causes are plausible, test the cheapest discriminating hypothesis first.
5. **Apply a minimal fix.**
   - Change only what fixes the root cause. No refactors in the same change.
   - If the fix changes specified behavior in an OpenSpec project, open a change through `/opsx:propose`.
6. **Add a regression test.**
   - The failing test from step 2 must now pass.
   - Add a test for adjacent edge cases when the cause suggests them.
7. **Verify.**
   - Run `/tenet:verify-changes` on the full relevant suite.
   - For security-sensitive bugs, also run `security-reviewer`.
8. **Record.**
   - Run `mem_save` with the root cause, the fix, and any failed approaches (type `bugfix`).
   - Write a short note in the PR or changelog if the project keeps one.

## Output
- **Cause:** with evidence.
- **Fix:** with `file:line`.
- **Regression test:** its name.
- **Verification:** results.
- **Residual risks.**

## Verification
- The regression test failed before the fix and passes after it (both runs reported).
- The full relevant suite passes.
- The diff is limited to the fix and its tests.
