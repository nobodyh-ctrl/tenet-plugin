# Containers, CI/CD, releases and environments

## Standards

- **MUST** Run tests, lint and build on every pull request. Merging requires a green pipeline.
- **MUST** Authenticate CI to cloud providers with OIDC and short-lived credentials where supported. Never store long-lived cloud keys in CI secrets when OIDC is available.
- **MUST** Require explicit approval for production deployments. Make every release traceable to a commit and a build artifact.
- **MUST** Know the rollback path before deploying (previous artifact, migration reversal or forward fix).
- **SHOULD** Build each artifact once and promote the same artifact across environments.
- **SHOULD** Use multi-stage container builds and small base images. Run as a non-root user and pin image versions by tag and digest.
- **SHOULD** Scan dependencies, containers and IaC in CI, and fail on new critical findings.
- **SHOULD** Make database migrations backward compatible (expand → migrate → contract) so app and schema can roll back independently.
- **SHOULD** Keep environment configuration outside the artifact (environment variables, parameter stores) and keep environments as similar as practical.
- **SHOULD** Use Docker Compose for local multi-service development.
- **EXPERIMENTAL** Progressive delivery (canary, feature flags) for user-facing services.

## Decision criteria

- **Kubernetes:** adopt only when many services, autoscaling needs or platform requirements justify its operational cost. Managed container services or PaaS are the default for small teams.
- **CI platform:** use the one native to the code host (for example GitHub Actions on GitHub) unless a requirement says otherwise.
