# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Optional forge-owned permission rules`
- TO: `### Requirement: Optional tenet-owned permission rules`

## MODIFIED Requirements

### Requirement: Read-only Bash for reviewers
When the hook input's `agent_type` is `reviewer` or `security-reviewer` (with or without the `tenet:` prefix), the hook SHALL deny any command outside a read-only allowlist or containing write redirections.

#### Scenario: Reviewer writes
- **WHEN** the hook receives `git commit -m x` with `agent_type` `tenet:reviewer`
- **THEN** it returns `deny`

### Requirement: Optional tenet-owned permission rules
The optional `--with-permissions` install SHALL add only `ask` and `deny` rules absent from `settings.json`, tracked in the ownership manifest, and MUST NOT add broad `allow` rules or change `defaultMode`.

#### Scenario: Non-destructive merge
- **WHEN** `settings.json` has foreign rules and keys and `--with-permissions` runs twice
- **THEN** foreign content is unchanged and tenet rules appear exactly once
