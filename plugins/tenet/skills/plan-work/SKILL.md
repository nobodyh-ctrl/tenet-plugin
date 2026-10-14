---
name: plan-work
description: Turn a goal into a scoped, reviewable plan before writing code. Use when starting a feature, fix or refactor that is not trivially small, when the user asks for a plan, or before any OpenSpec proposal. Explores the code, reads specs, defines scope, risks and acceptance criteria.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[goal]"
---

# Plan work

## When to use
- Any task that is not small. A task is small when it is understood, low-risk, and resumable from the request plus `git diff` alone.
- Not for typo fixes or one-line changes with obvious verification.

## Steps
1. **Context.** Read the project instructions (AGENTS.md, CLAUDE.md) and check `git status`. If Engram is available, call `mem_current_project`, then run a targeted `mem_search` on the goal.
2. **Explore narrowly.** Use targeted search, symbol skeletons and line ranges. If understanding needs more than about 3 inline searches or reads, delegate one `explorer` subagent with a precise question and ask for a `path:line` map.
3. **Existing intent.** If `openspec/` exists, run `openspec list --specs` and read the related specs with `openspec show <spec> --type spec`.
4. **Define the change:**
   - goal;
   - in scope and out of scope;
   - acceptance criteria, written as WHEN/THEN;
   - affected areas;
   - risks (security, data, cost, compatibility);
   - open questions.
5. **Choose the path:**
   - **OpenSpec project, meaningful change:** run `/opsx:propose` with the material above. OpenSpec writes the proposal, specs, design and tasks.
   - **No OpenSpec, or a lightweight change:** present a short plan in which every step has its own verification. Do not run `openspec init` unless the user asks for it; suggest `/tenet:project-init` for long-lived projects.
6. **Design alternatives.** For architecture choices, consult `${CLAUDE_PLUGIN_ROOT}/manual/core/architecture.md`. Delegate to the `architect` agent only for hard trade-offs that have several viable options.
7. **Stop.** Present the plan and wait for explicit approval. A plan is not authorization to implement.

## Output
- Scope.
- Acceptance criteria.
- Risks.
- Tasks, each with its verification.
- Open questions.

## Verification
- Every acceptance criterion is observable and maps to a test or command.
- Out-of-scope items are listed.
- In OpenSpec projects, `openspec validate <change> --strict` passes.
- The user explicitly approved the plan before implementation started.
