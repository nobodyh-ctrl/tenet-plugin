# specialist-agents Specification

## Purpose
Provide a small set of least-privilege subagents with explicit responsibilities, compact handoff contracts and structured outputs, used only when delegation pays off.

## Requirements

### Requirement: Native agent definitions
The plugin SHALL include `architect`, `explorer`, `implementer`, `reviewer`, `security-reviewer` and `tutor` with `name`, `description` and explicit `tools`, and MUST NOT use `permissionMode`, `hooks` or `mcpServers`, which Claude Code ignores for plugin agents.

#### Scenario: Valid frontmatter
- **WHEN** the validator parses `agents/*.md`
- **THEN** each has the three fields and none declares ignored fields

### Requirement: Least privilege
Only `implementer` SHALL have `Edit` or `Write`; `architect`, `explorer` and `tutor` SHALL be read/research-only; `reviewer` and `security-reviewer` SHALL get Bash only under the guard hook's read-only enforcement.

#### Scenario: Privilege table
- **WHEN** the validator compares each agent's `tools` with the privilege table
- **THEN** it fails if a non-implementer agent has `Edit`, `Write` or `NotebookEdit`

### Requirement: Compact evidence-based outputs
`explorer` SHALL return a short repository map with file:line evidence; `reviewer` and `security-reviewer` SHALL separate "Confirmed findings", "Potential risks" and "Suggestions", ordered by severity with file references, checked against approved requirements when an OpenSpec change exists.

#### Scenario: Output sections
- **WHEN** the validator reads `reviewer`
- **THEN** its output format contains the three sections

### Requirement: No delegated dangerous operations
No agent SHALL push, deploy, run IaC apply/destroy, delete persistent data or write memory on behalf of the parent; these return to the main session.

#### Scenario: Escalation instruction
- **WHEN** the validator reads each agent
- **THEN** it finds the escalation restriction
