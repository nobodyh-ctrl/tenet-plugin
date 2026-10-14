# Engineering Manual

Reusable engineering standards and decision frameworks for any project. It guides decisions without imposing one stack. Skills load single sections on demand. This index is never loaded in full by default.

## Normative levels

Every standard under a `## Standards` heading carries exactly one marker:

- **MUST**: applies to every project. Deviating requires an explicit, recorded reason (ADR or OpenSpec design). Kept few on purpose.
- **SHOULD**: the default. A project may choose otherwise with a stated reason.
- **EXPERIMENTAL**: being evaluated. Use it only when a project opts in.

`## Decision criteria` sections are guidance for choosing between options. They are not rules.

## Sections

### Core engineering
- [Principles, SDLC and definition of done](core/principles.md)
- [Requirements, acceptance criteria and SDD](core/requirements-and-sdd.md)
- [Architecture and ADRs](core/architecture.md)
- [Coding, testing and documentation](core/quality.md)
- [Project onboarding](core/onboarding.md)

### Infrastructure and delivery
- [Cloud and Infrastructure as Code](delivery/cloud-and-iac.md)
- [Containers, CI/CD, releases and environments](delivery/containers-and-cicd.md)
- [Secrets and identity](delivery/secrets-and-identity.md)
- [Observability, reliability, operations and cost](delivery/operations.md)

### Security
- [Secure engineering: threat modeling, least privilege, appsec, supply chain](security/secure-engineering.md)
- [Cloud and infrastructure security](security/cloud-infra-security.md)
- [Security operations: logging, audit, vulnerabilities, testing](security/security-operations.md)

### Providers
- [AWS](providers/aws.md). This is the initial provider reference. Add `providers/<name>.md` for others without touching the principles.

### Catalogs
- [Tool catalog: criteria and policy](catalog/README.md)
- [Tools](catalog/tools.md)
- [Technologies](catalog/technologies.md)

## Evolution

- Changes to a `MUST` or `SHOULD` standard go through an OpenSpec change in the forge repository. Editorial fixes do not.
- When a project reveals a lesson, promote it here only if it is reusable across independent projects. Project-specific decisions stay in that project's ADRs.
- Prefer adding decision criteria over adding mandatory rules. Depth grows from real project evidence, not up front.
