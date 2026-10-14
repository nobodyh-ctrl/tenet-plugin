# Coding, testing and documentation

## Standards

- **MUST** Match the repository's existing conventions (naming, structure, error handling) over personal preference.
- **MUST** Add or update automated tests with every behavior change. A bug fix starts with a failing test that reproduces it, when feasible.
- **MUST** Keep the main branch buildable and its test suite green.
- **SHOULD** Enforce formatting, linting and type checking in CI with the ecosystem's standard tools.
- **SHOULD** Follow the test pyramid: many fast unit tests, focused integration tests against real dependencies (containers), and few end-to-end tests on critical paths.
- **SHOULD** Make tests deterministic: no real time, randomness or network unless controlled.
- **SHOULD** Handle errors explicitly at boundaries; never swallow them silently. Log with context, without secrets.
- **SHOULD** Keep a README with purpose, prerequisites, run, test and deploy commands; document decisions as ADRs; keep docs next to the code they describe.
- **SHOULD** Comment the non-obvious *why*, not the *what*.
- **EXPERIMENTAL** Mutation testing for critical domain logic.

## Decision criteria

- Coverage is a signal, not a goal. Prioritize tests on business rules, security checks, and code that changed recently or often.
- Choose integration tests over mocks when the mock would encode assumptions about a dependency you do not control.
