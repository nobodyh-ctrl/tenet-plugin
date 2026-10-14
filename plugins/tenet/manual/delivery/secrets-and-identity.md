# Secrets and identity

## Standards

- **MUST** Never commit secrets. Use a secret manager or the platform's secret store, and inject secrets at runtime.
- **MUST** Use workload identity or roles for services and short-lived credentials for humans and CI. Avoid static access keys.
- **MUST** Rotate any secret that was exposed, and treat the exposure as an incident.
- **SHOULD** Keep `.env.example` with names only, and keep real `.env` files ignored by git.
- **SHOULD** Scan for secrets in pre-commit or CI (for example gitleaks or trufflehog).
- **SHOULD** Separate identities per environment and per service. No shared admin accounts.
- **SHOULD** Enforce MFA for human access to cloud consoles and code hosting.

## Decision criteria

- Prefer the provider's native secret manager for workloads in that provider. Use a cross-platform secret manager only when several providers or on-premises systems need the same secrets.
