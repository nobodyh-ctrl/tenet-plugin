# Project onboarding

Used by `/forge:project-init` for new repositories and for repositories new to forge.

## Standards

- **MUST** Inspect before proposing: read the repository's instructions, check git status, map the structure, and identify the stack from manifests (package.json, *.csproj, pyproject, go.mod, Dockerfile, IaC folders).
- **MUST** Capture product context: purpose, users, critical flows, data sensitivity, and expected scale. Ask the user only what cannot be inferred.
- **MUST** Identify constraints: security, compliance, cost ceiling, availability target, deployment target, and team size.
- **MUST** Choose architecture and technologies with explicit criteria (see [architecture](architecture.md) and the [technology catalog](../catalog/technologies.md)). Every deviation from a SHOULD default needs a recorded reason.
- **SHOULD** Create project instructions (`AGENTS.md`, plus a `CLAUDE.md` importing it) with the stack, commands, conventions and constraints.
- **SHOULD** Define the test strategy, CI checks, deployment target, environments and observability before the first feature.
- **SHOULD** Pin the Engram project name with `.engram/config.json` so memories don't fragment across directories.
- **SHOULD** Offer OpenSpec (`openspec init --tools claude`) for long-lived projects. Never initialize it without the user's explicit request.

## Outputs

- Project instruction files.
- An initial ADR set: architecture, data store, deployment.
- A testing and CI plan.
- A list of open decisions with owners and next steps.
