# Security operations

## Standards

- **MUST** Log authentication events, authorization failures and administrative actions with who, what, when and where, and without secrets.
- **MUST** Triage vulnerability findings by exploitability and exposure. Fix critical, exploitable findings before release.
- **SHOULD** Run SAST, dependency (SCA) and secret scanning in CI, plus DAST against staging for web-facing services.
- **SHOULD** Track accepted risks with an owner and a review date.
- **SHOULD** Keep an incident response checklist: contain, preserve evidence, rotate credentials, communicate, review.
- **SHOULD** Centralize logs with retention that matches compliance needs, and alert on suspicious patterns.
- **EXPERIMENTAL** Detection-as-code rules versioned in the repository.

## Decision criteria

- Pick scanners that run locally and in CI with the same configuration, so findings are reproducible before pushing.
- Treat an AI review (for example GGA) as an extra signal. It does not replace tests, static analysis, or human judgment.
