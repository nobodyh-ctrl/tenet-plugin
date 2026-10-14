# Spec Delta

## MODIFIED Requirements

### Requirement: Idempotent install with ownership manifest
The installer SHALL copy rules to `<config>/rules/tenet/`, record owned files (with SHA-256) and permission rules in a manifest, and produce the same state on repeated runs.

#### Scenario: Reinstall
- **WHEN** install runs twice
- **THEN** nothing is duplicated and no new backup is created if nothing changed

### Requirement: Backup and restore
Before modifying or deleting an existing file the installer SHALL back it up under `<config>/backups/tenet/<timestamp>/` and SHALL support `--restore <timestamp>`.

#### Scenario: Byte-identical restore
- **WHEN** install runs with `--with-permissions` and the created backup is restored
- **THEN** `settings.json` is byte-identical to the original

### Requirement: Selective uninstall
Uninstall SHALL remove only manifest-listed files and rules and preserve everything else, including third-party MCP entries, hooks and Engram data.

#### Scenario: Foreign config intact
- **WHEN** foreign rules, skills, settings and MCP entries exist and uninstall runs
- **THEN** all foreign content is identical and tenet components are gone
