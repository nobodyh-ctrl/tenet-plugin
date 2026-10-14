# Spec-Driven Development (tenet)

- In projects with an `openspec/` directory, use OpenSpec for meaningful changes: new behavior, architecture, integrations, security, infrastructure, agent workflows, memory policies, installers or breaking changes.
- Cycle: explore -> `/opsx:propose` -> user review -> explicit approval -> `/opsx:apply` -> `openspec validate --strict` -> user approval -> `/opsx:archive`. Creating a proposal is not approval.
- Lightweight path (no OpenSpec change) only for small tasks (see delegation rule) and for editorial fixes or behavior-neutral refactors. Never invent requirements to satisfy validation.
- Mark a task done only with evidence. If scope or a key decision changes, stop and update the artifacts first.
- Never run `openspec init` unless the user explicitly asks; offer it through `/tenet:project-init` instead.
- In projects without OpenSpec, still state scope and acceptance criteria before non-trivial work.
