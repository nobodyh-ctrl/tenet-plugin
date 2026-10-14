# Spec Delta

## MODIFIED Requirements

### Requirement: Engram wiring through the native CLI
With `--with-engram` the installer SHALL register Engram only via `claude mcp add --scope user engram -- <engram> mcp --tools=agent`, record it in the manifest, and remove it on uninstall only if it recorded it; tenet MUST NOT edit `.claude.json` or Engram data directly.

#### Scenario: Fresh wiring
- **WHEN** install runs with `--with-engram` against a temp config with no `engram` entry
- **THEN** the planned command is exactly the `claude mcp add` invocation and the manifest records ownership

#### Scenario: Existing different entry
- **WHEN** an `engram` MCP entry already exists with a different command
- **THEN** the installer reports a conflict, leaves it untouched and does not record ownership

### Requirement: Isolation and secret exclusion
Project memories SHALL use the project scope resolved by Engram (`.engram/config.json` when present), personal preferences the personal scope; secrets and sensitive personal data MUST NOT be saved, and deletions or consolidations require user approval.

#### Scenario: Synthetic isolation test
- **WHEN** a synthetic memory is saved under project `tenet-fixture-a` and searched from `tenet-fixture-b`
- **THEN** a project-scoped search in B does not return it
