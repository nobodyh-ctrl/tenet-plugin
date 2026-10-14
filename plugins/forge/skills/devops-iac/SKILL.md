---
name: devops-iac
description: Work safely on Docker, CI/CD, Terraform/OpenTofu, Ansible, Kubernetes and cloud deployments - plan before apply, least privilege, cost and destruction awareness. Use for any infrastructure, pipeline or deployment change.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[task]"
---

# DevOps and IaC

## When to use
For changes to any of these:
- Dockerfiles and Compose files
- CI/CD workflows
- IaC: Terraform, OpenTofu, CloudFormation, CDK
- Ansible
- Kubernetes manifests and Helm charts
- Cloud deployments

## Safety rules
The forge guard also enforces these.
- Before any `apply`, `destroy`, deploy or `kubectl apply`, run `plan`, `diff`, `--check` or `--dry-run`, show the output, and wait for explicit approval. The guard asks for confirmation on these commands.
- In every plan review, flag:
  - **Destruction:** resources replaced or destroyed, and any data loss.
  - **Cost:** new billable resources, NAT gateways, larger instances.
  - **IAM:** wildcards, admin policies, public exposure.
  - **State:** imports and moves.
- Never put secrets in code, state outputs, CI logs or images. Use OIDC for CI-to-cloud authentication.
- Change non-production first. Know the rollback before making the change.

## Steps
1. **Read the existing conventions.** Check the IaC and pipeline module layout, backends, environments, naming and tags.
2. **Make the change and validate it.** Edit the code, then run whichever formatters and validators are available: `terraform fmt -check`, `terraform validate`, `tflint`, `ansible-lint`, `hadolint`, `actionlint`, `kubeconform`.
3. **Scan for security issues.** Run the available scanners (`trivy config`, `checkov`) and report findings by severity.
4. **Produce the plan or diff.** Summarize it with [references/plan-review.md](references/plan-review.md).
5. **Apply only after explicit approval.** Then verify with health checks, smoke tests and a drift check.

Standards: `${CLAUDE_PLUGIN_ROOT}/manual/delivery/cloud-and-iac.md` and `${CLAUDE_PLUGIN_ROOT}/manual/delivery/containers-and-cicd.md`. Provider specifics: `${CLAUDE_PLUGIN_ROOT}/manual/providers/`.

## Verification
- Validators and scanners ran, and their results are reported.
- The plan was shown and summarized before any apply: adds, changes, destroys, plus cost and IAM flags.
- After an approved apply, the health check or smoke test output is reported.
