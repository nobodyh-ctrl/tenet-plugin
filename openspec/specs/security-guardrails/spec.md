# security-guardrails Specification

## Purpose
Enforce technical controls through a plugin hook that blocks clearly destructive actions and requires confirmation for risky ones, instead of relying only on written instructions.

## Requirements

### Requirement: Deny clearly destructive commands
The `PreToolUse` hook for `Bash` and `PowerShell` SHALL deny recursive deletion of root, home or a drive, disk formatting, raw device writes, fork bombs, and force push to `main` or `master`.

#### Scenario: Root deletion
- **WHEN** the hook receives `rm -rf /` or `Remove-Item -Recurse -Force C:\`
- **THEN** it returns `permissionDecision: deny` citing the rule id

#### Scenario: Legitimate command
- **WHEN** the hook receives `rm -rf ./build`, `npm test` or `git status`
- **THEN** it emits no decision

### Requirement: Ask on risky operations
The hook SHALL return `ask` for `git push`, tag or release creation, `terraform|tofu apply|destroy`, `kubectl delete|apply`, `helm install|upgrade|uninstall`, `docker volume rm`, `docker system prune`, global package installs, `sudo`, Git hook installation (`gga install`, writes to `.git/hooks`) and piping downloads to an interpreter.

#### Scenario: Push
- **WHEN** the hook receives `git push origin main`
- **THEN** it returns `ask` with a reason

### Requirement: Secret file protection
The hook SHALL return `ask` when `Read`, `Edit` or `Write` targets secret files (`.env*` except `.env.example`, `~/.ssh/`, `~/.aws/credentials`, `*.pem`, `*.key`) and `deny` for writes to private keys.

#### Scenario: Env file
- **WHEN** the hook receives `Read` of `app/.env`
- **THEN** it returns `ask`

#### Scenario: Env template
- **WHEN** the hook receives `Read` of `.env.example`
- **THEN** it emits no decision

### Requirement: Read-only Bash for reviewers
When the hook input's `agent_type` is `reviewer` or `security-reviewer` (with or without the `forge:` prefix), the hook SHALL deny any command outside a read-only allowlist or containing write redirections.

#### Scenario: Reviewer writes
- **WHEN** the hook receives `git commit -m x` with `agent_type` `forge:reviewer`
- **THEN** it returns `deny`

### Requirement: Safe failure and secret-free messages
The hook SHALL exit 0 without a decision on invalid input or missing Python (fail-open, documented), and MUST NOT echo the full command or file contents in its messages.

#### Scenario: Invalid JSON
- **WHEN** the hook receives non-JSON input
- **THEN** it exits 0 with no decision and a short stderr warning

### Requirement: Optional forge-owned permission rules
The optional `--with-permissions` install SHALL add only `ask` and `deny` rules absent from `settings.json`, tracked in the ownership manifest, and MUST NOT add broad `allow` rules or change `defaultMode`.

#### Scenario: Non-destructive merge
- **WHEN** `settings.json` has foreign rules and keys and `--with-permissions` runs twice
- **THEN** foreign content is unchanged and forge rules appear exactly once
