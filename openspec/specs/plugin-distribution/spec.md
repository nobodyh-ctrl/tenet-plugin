# plugin-distribution Specification

## Purpose
Distribute the system's skills, agents and hooks as the `forge` Claude Code plugin through a marketplace owned by this repository, installable with native commands.

## Requirements

### Requirement: Valid marketplace
The repository SHALL contain `.claude-plugin/marketplace.json` named `forge` with an `owner` and a `forge` entry whose `source` is a relative path without `..`, and it SHALL pass `claude plugin validate .` with no errors.

#### Scenario: Native validation
- **WHEN** `claude plugin validate .` runs at the repository root
- **THEN** it exits 0 and reports no errors

#### Scenario: Offline validation
- **WHEN** `python scripts/validate.py` runs without Claude Code available
- **THEN** it checks required fields, kebab-case names, absence of `..` and existence of each `source`, failing on any violation

### Requirement: Consistent plugin manifest
The plugin SHALL have `.claude-plugin/plugin.json` with `name: forge` matching the marketplace entry, a semver `version`, `description`, `author` and `license`.

#### Scenario: Names and versions agree
- **WHEN** the validator compares `marketplace.json` with `plugin.json`
- **THEN** it reports an error if name or version differ

### Requirement: Standard component layout
Skills, agents and hooks SHALL live in `skills/<name>/SKILL.md`, `agents/*.md` and `hooks/hooks.json` inside the plugin, and the plugin root MUST NOT contain a `CLAUDE.md`.

#### Scenario: Inventory detected
- **WHEN** the plugin is installed and `claude plugin details forge` runs
- **THEN** the inventory lists 17 skills, 6 agents and the declared hooks

### Requirement: Native installation without external services
Documentation SHALL describe installation with `claude plugin marketplace add <path|owner/repo>` and `claude plugin install forge@forge`, and the plugin MUST NOT declare MCP servers or require credentials.

#### Scenario: Isolated install
- **WHEN** the marketplace is added from the local path and the plugin is installed with `CLAUDE_CONFIG_DIR` pointing to a temp directory
- **THEN** `claude plugin list` shows `forge@forge` enabled and the real user configuration is unchanged

### Requirement: Read-only pre-approval scoped to the plugin
Skills that read plugin files (manual sections, references, templates) SHALL declare `allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)` so those reads do not prompt, and no skill SHALL pre-approve any other tool or path.

#### Scenario: Manual readable without prompts
- **WHEN** a skill that references `${CLAUDE_PLUGIN_ROOT}` runs in a headless session in an unrelated project
- **THEN** it reads the referenced plugin file without a permission denial

#### Scenario: No broader pre-approval
- **WHEN** the validator parses skill frontmatter
- **THEN** it fails if `allowed-tools` grants anything other than `Read(${CLAUDE_PLUGIN_ROOT}/**)`, or if a skill reading plugin files lacks it

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
