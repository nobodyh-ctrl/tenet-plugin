# Spec Delta

## MODIFIED Requirements

### Requirement: Valid marketplace
The repository SHALL contain `.claude-plugin/marketplace.json` named `tenet` with an `owner` and a `tenet` entry whose `source` is a relative path without `..`, and it SHALL pass `claude plugin validate .` with no errors.

#### Scenario: Native validation
- **WHEN** `claude plugin validate .` runs at the repository root
- **THEN** it exits 0 and reports no errors

#### Scenario: Offline validation
- **WHEN** `python scripts/validate.py` runs without Claude Code available
- **THEN** it checks required fields, kebab-case names, absence of `..` and existence of each `source`, failing on any violation

### Requirement: Consistent plugin manifest
The plugin SHALL have `.claude-plugin/plugin.json` with `name: tenet` matching the marketplace entry, a semver `version`, `description`, `author` and `license`.

#### Scenario: Names and versions agree
- **WHEN** the validator compares `marketplace.json` with `plugin.json`
- **THEN** it reports an error if name or version differ

### Requirement: Standard component layout
Skills, agents and hooks SHALL live in `skills/<name>/SKILL.md`, `agents/*.md` and `hooks/hooks.json` inside the plugin, and the plugin root MUST NOT contain a `CLAUDE.md`.

#### Scenario: Inventory detected
- **WHEN** the plugin is installed and `claude plugin details tenet` runs
- **THEN** the inventory lists 17 skills, 6 agents and the declared hooks

### Requirement: Native installation without external services
Documentation SHALL describe installation with `claude plugin marketplace add <path|owner/repo>` and `claude plugin install tenet@tenet`, and the plugin MUST NOT declare MCP servers or require credentials.

#### Scenario: Isolated install
- **WHEN** the marketplace is added from the local path and the plugin is installed with `CLAUDE_CONFIG_DIR` pointing to a temp directory
- **THEN** `claude plugin list` shows `tenet@tenet` enabled and the real user configuration is unchanged

### Requirement: Version reporting
The plugin SHALL provide a user-invoked `/tenet:version` skill that reads the version from the plugin manifest at run time and reports it with its release channel (`beta` for pre-release versions, `stable` otherwise), and the installer SHALL print the repository version with `--version`.

#### Scenario: Version in a session
- **WHEN** a user runs `/tenet:version` in any project
- **THEN** the answer contains the exact `version` string from `plugin.json` and the channel, without a permission prompt

#### Scenario: Version from the installer
- **WHEN** `python scripts/agentcfg.py --version` runs
- **THEN** it prints `tenet <version>` matching `plugin.json` and exits 0

#### Scenario: Not auto-invoked
- **WHEN** the validator parses the `version` skill
- **THEN** it declares `disable-model-invocation: true`
