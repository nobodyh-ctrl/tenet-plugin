# Spec Delta

## MODIFIED Requirements

### Requirement: Standard component layout
Skills, agents and hooks SHALL live in `skills/<name>/SKILL.md`, `agents/*.md` and `hooks/hooks.json` inside the plugin, and the plugin root MUST NOT contain a `CLAUDE.md`.

#### Scenario: Inventory detected
- **WHEN** the plugin is installed and `claude plugin details forge` runs
- **THEN** the inventory lists 17 skills, 6 agents and the declared hooks

## ADDED Requirements

### Requirement: Version reporting
The plugin SHALL provide a user-invoked `/forge:version` skill that reads the version from the plugin manifest at run time and reports it with its release channel (`beta` for pre-release versions, `stable` otherwise), and the installer SHALL print the repository version with `--version`.

#### Scenario: Version in a session
- **WHEN** a user runs `/forge:version` in any project
- **THEN** the answer contains the exact `version` string from `plugin.json` and the channel, without a permission prompt

#### Scenario: Version from the installer
- **WHEN** `python scripts/agentcfg.py --version` runs
- **THEN** it prints `forge <version>` matching `plugin.json` and exits 0

#### Scenario: Not auto-invoked
- **WHEN** the validator parses the `version` skill
- **THEN** it declares `disable-model-invocation: true`

### Requirement: Pre-release versioning and notes
Pre-release versions SHALL use a semver pre-release suffix (for example `0.1.0-beta.1`), `plugin.json` and the marketplace entry SHALL carry the same version, and each released version SHALL have release notes in `docs/releases/v<version>.md` and a matching `CHANGELOG.md` section.

#### Scenario: Notes exist for the current version
- **WHEN** the validator reads the plugin version
- **THEN** it fails if `docs/releases/v<version>.md` or a `## [<version>]` CHANGELOG section is missing
