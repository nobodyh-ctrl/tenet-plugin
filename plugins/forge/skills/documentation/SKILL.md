---
name: documentation
description: Keep documentation in sync with implemented behavior - README, ADRs, runbooks, diagrams, API docs and OpenSpec specs. Use after behavior changes, when decisions are made, or when docs are missing or stale.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
---

# Documentation

## When to use
- After a behavior change.
- After an architecture or technology decision.
- When onboarding information is missing.
- Before archiving an OpenSpec change.

## Steps
1. **Find the audience and the location.** Users read the README and usage docs. Maintainers read ADRs, architecture docs and runbooks. Follow the project's existing doc structure.
2. **Record decisions.** Put each decision in `docs/adr/NNNN-title.md`. While an OpenSpec change is in flight, put it in that change's `design.md` instead. Format: `${CLAUDE_PLUGIN_ROOT}/manual/core/architecture.md`.
3. **Update behavior through the spec workflow.** In OpenSpec projects, specs are updated by the change and merged by `/opsx:archive`. Never hand-edit `openspec/specs/` to describe new behavior; use `/opsx:sync` or archive. Prose docs must not contradict the specs.
4. **Draw diagrams in Mermaid,** inside the Markdown, so they stay versioned and diffable. For systems, use C4 levels 1-2.
5. **Make documented commands work.** Run every command you document, or mark it "not verified".
6. **Keep docs short.** Cover purpose, prerequisites, and how to run, test, deploy and roll back. Link to deeper docs instead of copying them.

## Verification
- Every documented command was executed or is explicitly marked as not verified.
- No statement contradicts the code, the tests or the approved specs.
- Internal links resolve.
- No secrets, internal hostnames or personal data appear in the docs.
