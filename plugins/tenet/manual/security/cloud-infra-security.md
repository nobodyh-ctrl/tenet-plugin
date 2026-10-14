# Cloud and infrastructure security

## Standards

- **MUST** Do no routine work with the root or owner account. Lock it with MFA and use it only for break-glass.
- **MUST** Encrypt data at rest and in transit with provider-managed or customer-managed keys.
- **MUST** Make storage and databases private by default. Public exposure needs an explicit, reviewed reason.
- **MUST** Enable audit logging of control-plane actions in every account, retained and protected from tampering.
- **SHOULD** Use network segmentation: private subnets for workloads and data, and minimal ingress through load balancers or gateways.
- **SHOULD** Write identity policies scoped to specific actions and resources. No wildcards in production.
- **SHOULD** Enable the provider's threat detection and configuration posture services.
- **SHOULD** Scan IaC (for example Checkov, tfsec/Trivy) and container images before deployment.
- **SHOULD** Patch hosts and base images regularly. Prefer immutable replacement over in-place patching.
- **EXPERIMENTAL** Service control or organization policies as guardrails across accounts.

## Decision criteria

- A separate account or project per environment gives the strongest blast-radius isolation. Choose it when compliance or the cost of a production incident is high.
