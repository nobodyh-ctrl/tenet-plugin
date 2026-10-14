# Cloud and Infrastructure as Code

Provider-agnostic principles. Provider specifics live in [providers](../providers/aws.md).

## Standards

- **MUST** Manage persistent infrastructure as code in version control. Manual console changes are temporary and get reconciled.
- **MUST** Review a plan or diff before every apply. Destructive plans need explicit approval.
- **MUST** Protect remote state: encrypted, access-restricted, locked during apply, versioned, and never committed.
- **MUST** Separate environments (at least dev and prod) by account, project or subscription where the provider allows it, or at least by state and naming.
- **SHOULD** Use modules for repeated patterns. Pin provider and module versions.
- **SHOULD** Run format, validate, lint and policy/security scans on IaC in CI.
- **SHOULD** Detect drift periodically (scheduled plan) and treat drift as an incident to explain.
- **SHOULD** Tag every resource with owner, environment, project and cost center.
- **EXPERIMENTAL** Policy as code (OPA/Conftest, Sentinel) gates in CI.

## Decision criteria: tool by role

These tools solve different problems. Do not treat them as interchangeable.

| Role | Default | Alternatives | Notes |
|---|---|---|---|
| Provisioning (multi-cloud or general) | Terraform or OpenTofu | Pulumi | OpenTofu is the open-source fork; prefer it if licensing matters |
| Provisioning (single provider, native) | Provider-native (for example CloudFormation, CDK) | Terraform | Choose native when deep integration or provider support outweighs portability |
| Configuration management (servers) | Ansible | Cloud-init, provider run-command | Only when you manage long-lived hosts |
| Image building | Dockerfile; Packer for VM images | | Immutable images over in-place configuration |
| Deployment orchestration | CI/CD pipeline | GitOps (Argo CD, Flux) for Kubernetes | |

Prefer managed services over self-hosted ones when the operational burden is higher than the cost difference.
