# Principles, SDLC and definition of done

## Standards

- **MUST** Keep the source of truth explicit: code and tests describe actual behavior; specs and ADRs describe intent and rationale. Contradictions are bugs to resolve.
- **MUST** Make every change small, reviewable and reversible. Prefer several focused changes over one large one.
- **MUST** Verify with evidence (tests, commands, observed behavior) before calling work done.
- **SHOULD** Choose the simplest design that meets current, stated requirements. Speculative generality needs a concrete upcoming requirement.
- **SHOULD** Automate any check that is run more than twice (lint, test, build, scan).
- **SHOULD** Follow the SDLC loop: discover → specify → design → implement → verify → release → operate → learn.

## Definition of done

A change is done when all of these hold. Items that don't apply are explicitly marked N/A.

1. Acceptance criteria are met and demonstrated.
2. Tests were added or updated and the relevant suite passes.
3. Lint and type checks pass.
4. Security implications were considered; high-risk changes were reviewed independently.
5. Docs, ADRs or specs reflect the new behavior.
6. Deployment and rollback steps are known for deployable changes.
7. Durable decisions and lessons are recorded (repo artifacts and, if available, memory).

## Decision criteria

- When two options are close, pick the one that is easier to change later and to operate by one person.
- Weigh total cost: build, run, operate, secure, and learn.
