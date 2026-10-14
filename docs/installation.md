# Installation

forge has two independent parts:

1. **The `forge` plugin:** skills, agents, the guard hook and the Engineering Manual. It is installed with Claude Code's native plugin commands.
2. **Complementary configuration:** methodology rules, a private profile, and optionally permission rules and Engram wiring. Plugins cannot ship these, so the repository's installer adds them.

You can use either part alone. Most people want both.

## Requirements

| Tool | Version | Needed for |
|---|---|---|
| Claude Code | 2.1+ | Everything |
| Python | 3.9+ | Guard hook, installer, validators |
| Git Bash (Windows) / bash (Linux) | any recent | Running the guard hook |
| Engram | 3.4+ recommended | Persistent memory (optional) |
| OpenSpec | 1.14+ | Spec-driven development in your projects (optional) |

The installer never installs these tools. It reports what is missing and links the official install instructions.

## 1. Plugin only

From GitHub, once the repository is published:

```bash
claude plugin marketplace add <owner>/forge
claude plugin install forge@forge
```

From a local clone:

```bash
claude plugin marketplace add /path/to/forge
claude plugin install forge@forge
```

The default scope is `user`, which means all your projects. To enable it for one repository only, use `--scope project`. That writes to the repository's `.claude/settings.json`, so teammates get the plugin too. Use `--scope local` for a project-only install that is not committed.

Check it with `claude plugin list` and `claude plugin details forge`.

## 2. Complementary configuration

Always preview first.

**Windows (PowerShell):**

```powershell
.\installers\install.ps1 -DryRun -WithPlugin -WithEngram
.\installers\install.ps1 -WithPlugin -WithEngram
```

If script execution is disabled, run it for that process only: `powershell -ExecutionPolicy Bypass -File .\installers\install.ps1 -DryRun`.

**Linux / Git Bash:**

```bash
installers/install.sh --dry-run --with-plugin --with-engram
installers/install.sh --with-plugin --with-engram
```

| PowerShell | Bash | Effect |
|---|---|---|
| `-DryRun` | `--dry-run` | Show every planned operation; write nothing; run no CLI commands |
| `-WithPermissions` | `--with-permissions` | Merge forge `ask`/`deny` rules into `settings.json` |
| `-WithPlugin` | `--with-plugin` | Run `claude plugin marketplace add <repo>` and `claude plugin install forge@forge --scope user` |
| `-WithEngram` | `--with-engram` | Run `claude mcp add --scope user engram -- <engram> mcp --tools=agent`. Skipped if an `engram` entry already exists |
| `-ConfigDir DIR` | `--config-dir DIR` | Target a different Claude config dir. The default is `$CLAUDE_CONFIG_DIR`, then `~/.claude` |
| `-Restore ID` | `--restore ID` | Restore the files of a backup |

The core is `python scripts/agentcfg.py {install,uninstall,restore,status}`. The wrappers only locate Python and pass the flags through.

### What gets written

| Path | When | Notes |
|---|---|---|
| `~/.claude/rules/forge/*.md` | Always | Methodology rules, loaded in every session |
| `~/.claude/rules/forge/profile.md` | Only if absent | Your private profile. Edit it; it is never overwritten |
| `~/.claude/settings.json` | `--with-permissions` | Only missing `ask`/`deny` rules are appended. Nothing else changes |
| `~/.claude/forge/manifest.json` | Always | Ownership manifest (files with hashes, rules added, CLI registrations) |
| `~/.claude/backups/forge/<id>/` | When something changes | Snapshot of every touched file, plus `index.json` |
| Plugin and marketplace entries, Engram MCP entry | `--with-plugin`, `--with-engram` | Written by the Claude Code CLI, not by forge |

### Safety guarantees (tested in `tests/test_installer.py`)

- **Idempotent.** A second run writes nothing and creates no backup.
- **Refuses dangerous targets.** The installer will not write through symlinks or junctions, will not overwrite files it does not own, and will not use a config dir that is a file.
- **Leaves corrupt settings alone.** A corrupt `settings.json` aborts the run before anything is written.
- **Leaves a different Engram entry alone.** An existing `engram` MCP entry with a different command is reported as a conflict and not touched.

## Personalize your profile

Edit `~/.claude/rules/forge/profile.md` to set:
- the language you want replies in;
- what you already master and what you are learning;
- your preferred defaults.

Keep it short, because it loads in every session. Do not put secrets, employer names or private project details in it.

## Using forge in a project

- **Nothing to install per project.** Skills are available everywhere: `/forge:feature`, `/forge:bugfix`, `/forge:project-init`, `/forge:study-topic`, and so on.
- **OpenSpec in a project.** Run `/forge:project-init`, or run `openspec init --tools claude` yourself. forge never initializes it automatically.
- **Pin the Engram project name.** Create `.engram/config.json` with `{"project_name": "<name>"}`. `project-init` offers this.

## Update

```bash
git pull
claude plugin marketplace update forge
claude plugin update forge@forge
installers/install.sh            # or .\installers\install.ps1, to refresh the rules
```

The plugin update needs a session restart, or run `/reload-plugins`. OpenSpec is updated on its own; see the tool catalog.

## Uninstall

```bash
installers/uninstall.sh --dry-run
installers/uninstall.sh            # keeps your profile
installers/uninstall.sh --purge    # also removes the profile
```

PowerShell: `.\installers\uninstall.ps1 [-DryRun] [-Purge]`.

Uninstall removes only what the manifest lists:
- the rule files (edited ones are backed up first);
- the permission rules forge added;
- the plugin and marketplace, if the installer registered them;
- the Engram MCP entry, if the installer added it.

Your own rules, settings, MCP servers and Engram data are untouched.

To remove only the plugin: `claude plugin uninstall forge@forge` and `claude plugin marketplace remove forge`.

## Restore a backup

Every install and uninstall prints a backup id.

```bash
python scripts/agentcfg.py status                 # lists recent backup ids
python scripts/agentcfg.py restore <id> --dry-run
python scripts/agentcfg.py restore <id>
```

Restore returns each file the run touched to its previous bytes, and deletes files the run created. It first snapshots the current state, so the restore itself can be undone. Plugin and MCP registrations are CLI state, not files. Remove them with uninstall or the `claude` CLI.

## Diagnose

```bash
python scripts/doctor.py
```

See [troubleshooting.md](troubleshooting.md).
