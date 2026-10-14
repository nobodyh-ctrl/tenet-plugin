---
name: review-code
description: Review a diff, branch or files for correctness, regressions, security and maintainability, with severity-ordered findings backed by evidence. Use before merging, after implementing a change, or when the user asks for a review.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[diff-range|files]"
---

# Review code

## When to use
- After implementation, before declaring the work done or opening a PR.
- On request, for any diff, branch or set of files.

## Steps
1. **Collect the target.** Use `git diff <base>...HEAD`, the staged changes, or the named files. If an OpenSpec change exists, read its specs and tasks and review against those requirements, not only style.
2. **Check in priority order:**
   1. Correctness against the requirements and acceptance criteria.
   2. Regressions and broken contracts.
   3. Security: input validation, authentication and authorization, secrets, injection, unsafe defaults. See `${CLAUDE_PLUGIN_ROOT}/manual/security/secure-engineering.md`.
   4. Error handling and edge cases.
   5. Missing or weak tests.
   6. Maintainability and conformance with the repository's conventions.
3. **Confirm before claiming.** Reproduce a suspected bug with a test, a command or a precise trace through the code. Anything not reproduced is a potential risk, not a confirmed finding.
4. **Get an independent review for high-risk changes** (auth, payments, data migration, infrastructure, security controls). Delegate to `reviewer`, and also to `security-reviewer` when security is involved. Give them the diff range and the spec paths. The forge guard keeps their Bash read-only.
5. **In OpenSpec projects,** check that every requirement and scenario in the change has an implementation and a test, then run `openspec validate <change> --strict`.

## Output
Keep it short and skip file summaries. Use three sections:
- **Confirmed findings:** severity (critical, high, medium or low), `file:line`, evidence, suggested fix.
- **Potential risks:** what to check, and why.
- **Suggestions:** optional improvements.

## Verification
- Each confirmed finding has reproducible evidence.
- Findings are ordered by severity.
- Requirements without tests are listed.
