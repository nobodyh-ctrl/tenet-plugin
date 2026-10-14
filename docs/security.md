# Security model

This document explains what tenet actually enforces, what it only recommends, and where the limits are.

## Threat model

| Threat | Example | Primary control | Type |
|---|---|---|---|
| Accidental destruction | `rm -rf ~`, `Remove-Item -Recurse C:\`, disk formatting | Guard hook `deny` rules | Technical |
| Unapproved external or costly action | `git push`, `terraform apply`, `aws ec2 run-instances`, `kubectl delete` | Guard hook `ask` rules | Technical |
| Secret exposure | Reading `.env`, `~/.aws/credentials`, private keys | Guard hook `ask` (read) / `deny` (key writes) | Technical |
| Reviewer agent modifying code | A review subagent runs `git commit` or `sed -i` | Guard hook read-only enforcement via `agent_type` | Technical |
| Global configuration drift | Editing `~/.claude/settings.json`, `git config --global`, `claude mcp add` | Guard hook `ask` rules | Technical |
| Prompt injection from repo content, docs or recalled memory | A README instructs the agent to exfiltrate data | Methodology rule: treat content as data | Prose only |
| Secrets stored in memory or logs | Saving an API key in Engram | Memory rule + guard messages cite rule ids only | Prose + technical (messages) |
| Installer damaging existing configuration | Overwriting user rules or settings | Ownership manifest, backups, symlink and foreign-file refusal, dry-run | Technical |

## Technical controls

### Guard hook

The guard is `plugins/tenet/hooks/`, registered as a plugin `PreToolUse` hook. It covers `Bash`, `PowerShell`, `Read`, `Edit`, `Write`, `MultiEdit` and `NotebookEdit`.

- **Rules are data.** They live in `policy.json`, each with an id, a decision and a reason. Tests in `tests/test_guard.py` cover both blocking and legitimate commands.
- **Evaluation order:**
  1. Destructive `deny`.
  2. Reviewer read-only enforcement.
  3. Risky `ask`.
  4. No decision: the normal Claude Code permission flow continues.
- **Messages cite only the rule id and a fixed reason.** The command and file contents are never echoed, so secrets in a command line do not leak into the transcript.
- **Reviewer enforcement.** When the hook input carries `agent_type` `reviewer` or `security-reviewer` (with or without the `tenet:` prefix), only allow-listed read-only commands pass. The guard rejects:
  - write redirections, `$(...)`, backticks;
  - `-delete`, `-exec`, `sed -i`, `tee`, `xargs`;
  - any git subcommand outside the read-only list.

### Optional permission rules

`--with-permissions` adds `ask` and `deny` rules to `settings.json` as a second layer. They are tracked in the installer manifest and removed on uninstall. They never add broad `allow` rules or change `defaultMode`.

### Installer safety

See [installation.md](installation.md). The installer supports dry-run, timestamped backups, byte-identical restore, an ownership manifest with hashes, refusal to write through symlinks or over foreign files, and selective uninstall.

## Limits

- **The guard is not a sandbox.** Claude Code permission rules and hooks match the command text, so obfuscation evades them. Examples: `sh -c "$(printf ...)"`, an absolute binary path, or a script that runs the command indirectly. The guard targets accidents and the forms an agent normally writes. It is not built to stop a deliberately adversarial agent. Use containers or VMs for untrusted work.
- **Fail-open.** If Python 3.9+ is missing, the input is invalid, or the policy cannot be loaded, the guard exits 0 without a decision and prints a short warning. A fail-closed guard would block every tool. `scripts/doctor.py` reports whether the guard can run.
- **Windows shell.** The hook runs `bash`. Claude Code on Windows uses Git Bash for hooks when it is installed. Without Git Bash the hook command fails, which Claude Code treats as non-blocking, so the guard is inactive.
- **Prose rules are not guarantees.** The methodology rules (`~/.claude/rules/tenet/`) and skills guide behavior, but Claude may not follow them. They are never presented as enforcement.
- **Plugin agents.** Claude Code ignores `permissionMode`, `hooks` and `mcpServers` in plugin agent files. Agent restrictions therefore come from each agent's `tools` list plus the guard hook.

## Reporting

See [SECURITY.md](../SECURITY.md).
