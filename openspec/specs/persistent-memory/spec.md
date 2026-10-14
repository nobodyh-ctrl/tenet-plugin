# persistent-memory Specification

## Purpose
Give agents verified cross-session memory through Engram, wired with the native Claude Code CLI, with a tenet-owned protocol for what to retrieve, save and hand off, and strict isolation and secret rules.

## Requirements

### Requirement: Engram wiring through the native CLI
With `--with-engram` the installer SHALL register Engram only via `claude mcp add --scope user engram -- <engram> mcp --tools=agent`, record it in the manifest, and remove it on uninstall only if it recorded it; tenet MUST NOT edit `.claude.json` or Engram data directly.

#### Scenario: Fresh wiring
- **WHEN** install runs with `--with-engram` against a temp config with no `engram` entry
- **THEN** the planned command is exactly the `claude mcp add` invocation and the manifest records ownership

#### Scenario: Existing different entry
- **WHEN** an `engram` MCP entry already exists with a different command
- **THEN** the installer reports a conflict, leaves it untouched and does not record ownership

### Requirement: Session lifecycle protocol
The memory rule SHALL require, for meaningful tasks, a targeted `mem_context`/`mem_search` at start, `mem_save` after decisions, root-caused fixes, discoveries, conventions, lessons, preference changes, unresolved issues and failed approaches, and `mem_session_summary` at handoff stating what changed, what was verified and the next step.

#### Scenario: Protocol present
- **WHEN** the validator reads the memory rule
- **THEN** it finds the start, during and handoff steps with the tool names verified against the installed Engram

### Requirement: Memory never overrides current evidence
The rule SHALL state that recalled memory is context to verify, never authority over current code, project constraints or security rules, and that a save is claimed only when the tool confirms it.

#### Scenario: Override clause
- **WHEN** the validator reads the memory rule
- **THEN** it finds the non-override and confirmation clauses

### Requirement: Isolation and secret exclusion
Project memories SHALL use the project scope resolved by Engram (`.engram/config.json` when present), personal preferences the personal scope; secrets and sensitive personal data MUST NOT be saved, and deletions or consolidations require user approval.

#### Scenario: Synthetic isolation test
- **WHEN** a synthetic memory is saved under project `tenet-fixture-a` and searched from `tenet-fixture-b`
- **THEN** a project-scoped search in B does not return it

### Requirement: Verified cross-session retrieval
The system SHALL provide a documented check that saves a synthetic observation in one session and retrieves it in a new session, reporting passed, failed or blocked.

#### Scenario: Retrieval check
- **WHEN** the check runs after Engram is wired
- **THEN** the report shows the observation id saved and retrieved, or states why it was blocked
