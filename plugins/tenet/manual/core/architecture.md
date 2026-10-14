# Architecture and ADRs

## Standards

- **MUST** Record significant, hard-to-reverse decisions as ADRs. Each ADR covers context, decision, alternatives considered, and consequences.
- **SHOULD** Start with a modular monolith, with clear module boundaries. Split into services only for a demonstrated need: independent scaling, team ownership, or a different runtime or security boundary.
- **SHOULD** Keep domain logic independent from frameworks, transport and persistence, so it can be tested without infrastructure.
- **SHOULD** Define API contracts explicitly (OpenAPI, schemas) and version breaking changes.
- **SHOULD** Design for idempotency and retries at every network boundary.
- **SHOULD** Draw a context diagram and a container diagram (C4 level 1-2) for any deployable system.
- **EXPERIMENTAL** Event-driven integration between modules inside a single deployable.

## Decision criteria

Evaluate options against:
- the requirements they satisfy;
- operational complexity for a small team;
- failure modes and blast radius;
- security boundary;
- cost at expected and 10x load;
- reversibility;
- team familiarity, which counts as cost, not as a reason by itself.

Data store: relational by default. Choose otherwise only for a stated access pattern (key-value at scale, documents with variable shape, search, time series, graph).

Sync vs async: use synchronous calls when the caller needs the answer now. Use queues or events when work can be retried later, must survive downstream outages, or fans out.

## ADR template

`docs/adr/NNNN-title.md` with these sections: Status, Context, Decision, Alternatives, Consequences, Date.
