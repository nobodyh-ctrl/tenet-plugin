---
name: aws-security
description: Teach and practice AWS cloud security through secure configurations, best practices and authorized, read-only-first checks (IAM, S3, VPC, CloudTrail, KMS, GuardDuty). Use when learning AWS security or reviewing an AWS setup the user owns.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[topic or account area]"
---

# AWS security

## Rules
- Work only in AWS accounts the user owns or is explicitly authorized to assess. Prefer a dedicated sandbox account.
- Read-only first: run `describe`, `list`, `get` and IAM Access Analyzer. Any mutating command (create, put, attach, delete) needs explicit approval at execution time; the forge guard asks.
- Never print access keys, secrets or session tokens. Use `aws sts get-caller-identity` to confirm identity, never `cat ~/.aws/credentials`.

## Steps
1. **Diagnostic.** Run the `learn-concept` diagnostic: what the learner knows about IAM, networking and AWS. Set the objective.
2. **Pick an area and explain it with the shared-responsibility model.** Areas:
   - identity: IAM, Identity Center, roles, policies, SCPs;
   - data: S3 Block Public Access, KMS, encryption;
   - network: VPC, security groups, NACLs, endpoints;
   - detection: CloudTrail, GuardDuty, Security Hub, Config.
3. **Show the secure baseline** from `${CLAUDE_PLUGIN_ROOT}/manual/providers/aws.md` and `${CLAUDE_PLUGIN_ROOT}/manual/security/cloud-infra-security.md`. Explain why each control exists, using a real incident pattern.
4. **Run authorized checks.**
   - Read-only commands, with expected secure results. Example: `aws s3control get-public-access-block --account-id <id>`.
   - Interpret each finding by severity.
5. **Remediate as a lab.** Use `/forge:hands-on-lab`, prefer IaC, include a cost estimate and cleanup.
6. **Checkpoint.** The learner explains the risk and the control before moving to the next area.

## Verification
- Every command used was read-only, or its mutation was explicitly approved.
- Findings name the resource, the risk and the remediation.
- No credentials appeared in output.
