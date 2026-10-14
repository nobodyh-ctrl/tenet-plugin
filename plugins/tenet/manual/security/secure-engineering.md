# Secure engineering

## Standards

- **MUST** Threat model new systems and security-relevant changes. Cover assets, entry points, trust boundaries, and STRIDE-style threats with their mitigations.
- **MUST** Apply least privilege to users, services, CI and agents. Start with nothing and grant only what is needed.
- **MUST** Validate all input at trust boundaries. Use parameterized queries and contextual output encoding. Never build commands or queries by string concatenation with untrusted data.
- **MUST** Use vetted libraries for authentication, sessions, password hashing and cryptography. Never write your own.
- **MUST** Ship secure defaults: deny by default, TLS everywhere, secure cookie flags, no debug endpoints in production.
- **SHOULD** Follow the OWASP ASVS level that matches the risk. Check changes against the OWASP Top 10 (API Top 10 for APIs).
- **SHOULD** Pin dependencies with lockfiles, update them regularly, and review new dependencies for maintenance, license and popularity before adding them.
- **SHOULD** Generate an SBOM for released artifacts, and sign artifacts where the platform supports it.
- **SHOULD** Rate limit and audit authentication and other sensitive endpoints.
- **EXPERIMENTAL** SLSA provenance for build pipelines.

## Decision criteria

- Higher data sensitivity or exposure means stronger controls: more review, more testing, more monitoring.
- Treat AI agents and their tools as untrusted automation. Give them scoped permissions and human approval for irreversible actions.
