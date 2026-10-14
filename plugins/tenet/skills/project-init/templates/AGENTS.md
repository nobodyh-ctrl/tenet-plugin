# <Project name>

<One paragraph: what the product does and for whom.>

## Stack

- Runtime and framework: <...>
- Data: <...>
- Infrastructure and deployment target: <...>

## Commands

| Task | Command |
|---|---|
| Install | `<...>` |
| Run locally | `<...>` |
| Test | `<...>` |
| Lint / type check | `<...>` |
| Build | `<...>` |

## Conventions

- <Structure, naming, error handling, API style>
- Tests live in `<...>` and use `<framework>`.

## Constraints

- Security: <data sensitivity, auth model>
- Cost: <ceiling>
- Availability: <target>

## Workflow

- Specs: <OpenSpec in `openspec/`, or "lightweight plans">
- Decisions: `docs/adr/` and `docs/decisions.md`
- Never commit secrets. `.env.example` lists the variable names.
