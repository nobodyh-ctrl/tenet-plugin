# Requirements, acceptance criteria and SDD

## Standards

- **MUST** State scope, out-of-scope and acceptance criteria before non-trivial work.
- **MUST** Write acceptance criteria as observable behavior, in WHEN/THEN form when possible. Each one maps to a test or a concrete check.
- **SHOULD** Use OpenSpec for meaningful changes in long-lived projects. The cycle is: proposal → specs → design → tasks → approval → apply → validate → archive.
- **SHOULD** Keep requirements free of implementation detail (no class names or libraries). Those belong in design.
- **SHOULD** Separate non-functional requirements explicitly: security, performance, availability, cost, compliance.
- **EXPERIMENTAL** Custom OpenSpec schemas per project type (`openspec schema init`).

## Decision criteria

- **When to use OpenSpec:** the change alters behavior other people or systems rely on, crosses modules, touches security or infrastructure, or will need explaining in six months.
- **When to use the lightweight path:** small, contained, resumable from the request plus the diff. Also editorial fixes and behavior-neutral refactors.
- **When to skip specs:** use `skip_specs: true` in `.openspec.yaml` only when no behavior changes. Never invent requirements to satisfy validation.
