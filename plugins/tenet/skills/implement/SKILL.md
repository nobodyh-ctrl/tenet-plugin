---
name: implement
description: Implement an approved plan or OpenSpec change in small, verified steps that follow the repository's conventions. Use after the user approved a plan or proposal, or for small tasks on the lightweight path.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[change-or-task]"
---

# Implement

## When to use
- **Approved OpenSpec change:** run `/opsx:apply <change>`, which drives task tracking, and follow the rules below while doing so.
- **Approved lightweight plan or small task:** follow the steps below directly.

## Steps
1. **Re-read the source of truth.** For OpenSpec, re-read the change's tasks, specs and design from disk. Otherwise, re-read the approved plan.
2. **Follow conventions.** Read nearby code and tests before editing. Match the existing naming, structure, error handling and test style. If the repository gives no guidance, use `${CLAUDE_PLUGIN_ROOT}/manual/core/quality.md`.
3. **One task at a time.** Write a failing test first when feasible. Make the smallest change that makes it pass, then run the relevant checks.
4. **Record progress only with evidence.** Tick a task (`- [x]` in the OpenSpec `tasks.md`) only after its verification has run and passed.
5. **Guard the scope.** If a task needs work beyond the specs, or a design assumption breaks, stop. Explain the gap, then update the artifacts (`/opsx:update`) or the plan before continuing.
6. **Delegate carefully.** Use the `implementer` subagent only for bounded tasks whose edit surfaces don't overlap. Give it a handoff with the objective, paths, scope, deliverable, verification, prohibited actions and task id. Never run two writers on the same files.
7. **Ask before risky operations.** Dependency installs, migrations against real data, pushes and deploys each need explicit approval at the moment of execution.

## Verification
- Every completed task shows or summarizes the output of its verification command.
- The full relevant test suite passes. Lint and type checks pass where the project has them.
- `git diff` contains only in-scope changes.
- For OpenSpec changes, `openspec validate <change> --strict` still passes.
