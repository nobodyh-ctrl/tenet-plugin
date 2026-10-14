# Observability, reliability, operations and cost

## Standards

- **MUST** Emit structured logs with a request or correlation id. Never log secrets or sensitive personal data.
- **MUST** Have health checks and alerts for user-facing availability on every deployed service.
- **MUST** Back up persistent data, and test restores periodically.
- **MUST** Set a budget and cost alerts for every cloud account or project.
- **SHOULD** Track the golden signals (latency, traffic, errors, saturation). Use OpenTelemetry for traces and metrics when the stack supports it.
- **SHOULD** Define SLOs for critical user journeys, and alert on symptoms rather than causes.
- **SHOULD** Write runbooks for known failure modes. After incidents, run blameless post-incident reviews with tracked actions.
- **SHOULD** Set timeouts, retries with backoff, and circuit breaking on external calls.
- **SHOULD** Review costs monthly. Delete unused resources and right-size them.
- **EXPERIMENTAL** Chaos experiments in non-production environments.

## Decision criteria

- Take on the observability stack's operational cost only when needed. Managed or provider-native first, self-hosted only with a reason.
- Choose recovery objectives (RPO/RTO) with the user before choosing a backup and replication strategy.
