---
name: hands-on-lab
description: Design and guide a reproducible hands-on lab with objective, authorized scope, prerequisites, steps, validation, cleanup and cost estimate. Use when the user wants to practice a technology (Linux, networking, Docker, Kubernetes, Terraform, AWS, security) in a safe, controlled environment.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[topic]"
---

# Hands-on lab

## Steps
1. **Define the environment and the authorized scope.**
   - Where it runs: local VM, containers, a sandbox cloud account.
   - What is in scope. Use only systems the learner owns or is authorized to use.
   - Never scan or test third-party systems.
2. **Identify prerequisites and risks.**
   - Prerequisites: tools, versions, accounts.
   - Risks: cost, data loss, network exposure.
   - For anything billable, estimate the cost and set a budget alert first (`${CLAUDE_PLUGIN_ROOT}/manual/providers/aws.md` covers cost traps).
3. **Write the lab** using the template in [references/lab-template.md](references/lab-template.md). Every step has a command and its expected output.
4. **Run or guide it.**
   - The learner runs the steps.
   - If the agent runs them, it runs only the local, reversible ones. Cloud-creating and global-install commands need explicit approval at execution time; the tenet guard asks.
5. **Validate.**
   - Check each objective with a concrete command or observation.
6. **Explain errors.**
   - For every failure, explain the cause, how to diagnose it, and the fix.
   - Turn the failure into a learning point.
7. **Clean up.**
   - Tear down every resource created and verify nothing is left: list the resources, check billing.
   - Destructive cleanup of real resources needs approval.
8. **Record.** Note what was learned and what was hard (see `study-topic` for storage).

## Verification
- The lab document contains all seven sections from the template.
- Cleanup was executed and verified, or the remaining resources are listed explicitly.
- No action targeted systems outside the authorized scope.
