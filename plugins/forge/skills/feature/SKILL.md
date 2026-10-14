---
name: feature
description: End-to-end workflow to build a new feature - inspect, scope, plan (OpenSpec when present), implement in small steps, verify, review and document. Use when the user asks to add or change functionality in a repository.
argument-hint: "[feature description]"
---

# Feature workflow

The main session orchestrates this workflow. Subagents are optional at the marked steps and need a named reason (see the delegation rule).

## Steps
1. **Inspect.**
   - Read the project instructions, check `git status`, and query Engram (`mem_current_project`, then `mem_search` on the feature).
   - Optional `explorer`: use it when understanding the affected area needs more than about 3 searches or reads. Ask it for a `path:line` map of the entry points, data flow and tests.
2. **Size the work.**
   - Small means understood, contained, and resumable from the request plus the diff. Small work goes straight to step 5 with a one-paragraph plan.
3. **Scope and plan.**
   - Use `/forge:plan-work`. In OpenSpec projects this runs `/opsx:propose`.
   - Optional `architect`: use it when several viable designs have real trade-offs. It returns options and a recommendation, and the main session writes `design.md`.
4. **Approval gate.**
   - Present the plan and wait for explicit approval.
5. **Implement.**
   - Use `/forge:implement`. In OpenSpec projects this runs `/opsx:apply`. Work in small steps, test first when feasible.
   - Optional `implementer`: use it only for bounded tasks on disjoint files, with a full handoff. Never have two writers on one file.
6. **Verify.**
   - Use `/forge:verify-changes` and report passed, failed, not executed or blocked for each check.
7. **Review.**
   - Use `/forge:review-code`.
   - Required independent check for high-risk changes (auth, data, payments, infrastructure, security controls): `reviewer`, plus `security-reviewer` when security is involved.
8. **Document.**
   - Use `/forge:documentation`: README, ADRs, runbooks.
9. **Handoff.**
   - Summarize what changed, what was verified (with evidence), and the open risks and next steps.
   - Run `mem_session_summary` if Engram is available.
   - In OpenSpec projects, wait for approval before `/opsx:archive`.
   - Never commit, push or open a PR unless the user asks.

## Verification
- Acceptance criteria are covered by executed checks.
- The review found no unresolved confirmed findings, or the user accepted them.
- The docs are updated.
- The summary separates what was verified from what was not.
