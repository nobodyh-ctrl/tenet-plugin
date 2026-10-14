# Changelog

All notable changes are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0-beta.1] - 2026-10-14

First public beta. Release notes: [docs/releases/v0.1.0-beta.1.md](docs/releases/v0.1.0-beta.1.md).

### Added
- `/forge:version` skill and `agentcfg.py --version`.
- `forge` plugin and `forge` marketplace.
- 16 skills.
  - Engineering: `plan-work`, `implement`, `review-code`, `verify-changes`, `documentation`, `devops-iac`.
  - Workflows: `feature`, `bugfix`, `release`, `project-init`.
  - Learning: `learn-concept`, `hands-on-lab`, `research-technology`, `aws-security`, `networking-lab`, `study-topic`.
- 6 least-privilege agents: `explorer`, `architect`, `implementer`, `reviewer`, `security-reviewer`, `tutor`.
- `PreToolUse` guard hook:
  - denies destructive commands;
  - asks before risky operations;
  - protects secret files;
  - keeps reviewer agents read-only.
- User-level methodology rules: core, SDD, memory, delegation, tokens and autonomy.
- A private profile template.
- Engineering Manual with core, delivery, security, AWS provider, technology catalog and tool catalog sections.
- Installer (`scripts/agentcfg.py` plus PowerShell and Bash wrappers):
  - dry-run, backups and restore;
  - an ownership manifest;
  - optional permissions, plugin registration and Engram MCP wiring.
- `scripts/validate.py`, `scripts/doctor.py`, `scripts/session_metrics.py`, a `unittest` suite and GitHub Actions CI.
