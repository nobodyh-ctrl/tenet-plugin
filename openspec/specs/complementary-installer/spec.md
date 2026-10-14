# complementary-installer Specification

## Purpose
Safely, idempotently and reversibly install what the plugin cannot ship (user-level rules, private profile, optional permissions) and register the plugin through the native CLI.

## Requirements

### Requirement: Platform entry points
The project SHALL provide `installers/install.ps1`, `uninstall.ps1`, `install.sh` and `uninstall.sh` that detect the OS, check prerequisites (Python, Claude Code, Engram, OpenSpec) and report what is missing with official install guidance, without installing third-party tools.

#### Scenario: Missing Python
- **WHEN** Python is unavailable
- **THEN** the installer exits non-zero with guidance and writes nothing

#### Scenario: Missing optional tool
- **WHEN** `openspec` or `engram` is missing
- **THEN** the installer reports it and continues

### Requirement: Dry run
With `--dry-run` (`-DryRun`) install and uninstall SHALL list every planned operation and MUST NOT write, delete or run CLI commands.

#### Scenario: No writes
- **WHEN** install runs with `--dry-run` on a temp config dir
- **THEN** the directory tree is identical before and after

### Requirement: Target directory validation
The installer SHALL target `--config-dir`, else `CLAUDE_CONFIG_DIR`, else `~/.claude`, and MUST reject a target that is a file, a symlink, or a missing path whose parent does not exist.

#### Scenario: Invalid path
- **WHEN** `--config-dir` points to a file
- **THEN** the installer exits with an error and writes nothing

### Requirement: Idempotent install with ownership manifest
The installer SHALL copy rules to `<config>/rules/forge/`, record owned files (with SHA-256) and permission rules in a manifest, and produce the same state on repeated runs.

#### Scenario: Reinstall
- **WHEN** install runs twice
- **THEN** nothing is duplicated and no new backup is created if nothing changed

### Requirement: No writes through links or over foreign files
The installer MUST NOT write through symlinks or overwrite an existing file absent from its manifest.

#### Scenario: Foreign file conflict
- **WHEN** a destination file exists and is not in the manifest
- **THEN** the installer aborts and names the conflict

### Requirement: Private profile preserved
The installer SHALL create the private profile from the template only if absent, and MUST NOT overwrite or delete it unless `--purge` is given.

#### Scenario: Edited profile
- **WHEN** the user edited the profile and reinstalls or uninstalls without `--purge`
- **THEN** the profile is unchanged

### Requirement: Backup and restore
Before modifying or deleting an existing file the installer SHALL back it up under `<config>/backups/forge/<timestamp>/` and SHALL support `--restore <timestamp>`.

#### Scenario: Byte-identical restore
- **WHEN** install runs with `--with-permissions` and the created backup is restored
- **THEN** `settings.json` is byte-identical to the original

### Requirement: Selective uninstall
Uninstall SHALL remove only manifest-listed files and rules and preserve everything else, including third-party MCP entries, hooks and Engram data.

#### Scenario: Foreign config intact
- **WHEN** foreign rules, skills, settings and MCP entries exist and uninstall runs
- **THEN** all foreign content is identical and forge components are gone

### Requirement: Native plugin registration
With `--with-plugin` the installer SHALL run `claude plugin marketplace add` and `claude plugin install` at user scope, and uninstall SHALL run the matching uninstall and remove commands; it MUST NOT download remote code or ask for credentials.

#### Scenario: Claude CLI missing
- **WHEN** `--with-plugin` is given and `claude` is not found (PATH or `~/.local/bin`)
- **THEN** the installer prints the exact manual commands and continues
