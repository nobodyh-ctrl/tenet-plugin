# Troubleshooting

Start with `python scripts/doctor.py`. It is read-only and points at most problems below.

| Symptom | Cause | Fix |
|---|---|---|
| `claude: command not found` in a terminal, but VS Code works | The native install lives in `~/.local/bin`, which is not on `PATH` | Add `~/.local/bin` to `PATH`, or call it by full path. The installer looks there automatically |
| Installer says `Python 3.9+ not found` on Windows | Only the Microsoft Store alias exists | Install Python (`winget install Python.Python.3.12`) or disable the alias under *Manage app execution aliases* |
| PowerShell: "running scripts is disabled" | Execution policy | `powershell -ExecutionPolicy Bypass -File .\installers\install.ps1 ...` (applies to that process only) |
| `error: ... is not owned by tenet` | A file with the same name already exists in `rules/tenet/` | Move it away, or compare it with `global-config/rules/` and delete it if it is an old copy, then re-run |
| `error: ... is a symlink or junction` | The config dir or a target folder is a link | Point `--config-dir` at the real directory. tenet never writes through links |
| Skills like `/tenet:feature` don't appear | Plugin not installed or not enabled, or the session predates the install | `claude plugin list`, `claude plugin details tenet`, then restart or run `/reload-plugins` |
| Guard never asks or blocks | Hook can't run (no bash or Python), or the plugin is disabled | `doctor.py` → "guard hook". On Windows install Git for Windows (Git Bash) |
| Guard blocks something legitimate | False positive in `plugins/tenet/hooks/policy.json` | Approve once if it was an `ask`. Otherwise open an issue with the rule id from the message (never paste secrets) |
| `mem_*` tools missing | Engram MCP not registered, or the session started before registration | `claude mcp list`, then `installers/install.sh --with-engram` and restart |
| Engram returns `ambiguous_project` | Started from a folder containing several repositories | Open the specific repository, or add `.engram/config.json` with `project_name` |
| `CONFLICT: an engram MCP entry with a different command exists` | Engram was wired by another tool (Gentle AI, the Engram plugin, or by hand) | Keep it, or remove it with `claude mcp remove engram --scope user` and re-run with `--with-engram` |
| OpenSpec commands `/opsx:*` missing in a project | OpenSpec not initialized there | Run `openspec init --tools claude` in that repository, then restart the session |
| Want to undo an install | | `python scripts/agentcfg.py status` to list backups, then `restore <id>`; or `uninstall` |
