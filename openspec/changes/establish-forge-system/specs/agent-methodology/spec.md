# Spec Delta

## Purpose

Define, in short always-loaded user-level rules, how agents discover context, apply SDD, use memory, delegate, save tokens, verify work and respect autonomy limits in every project.

## ADDED Requirements

### Requirement: Concise always-loaded rules
The methodology SHALL be shipped as Markdown rules for `~/.claude/rules/facundo-agent-config/` totalling at most 120 lines, with detailed guidance moved to skills or the Engineering Manual and referenced, not copied.

#### Scenario: Size budget
- **WHEN** the validator counts lines across `global-config/rules/*.md`
- **THEN** it fails if the total exceeds 120 lines

### Requirement: Source-of-truth order
The rules SHALL state the precedence: code and executable config, then tests and execution evidence, approved OpenSpec artifacts, ADRs, Engineering Manual, project instructions, and Engram, and SHALL require investigating contradictions instead of picking a convenient source.

#### Scenario: Precedence present
- **WHEN** the validator reads the methodology rules
- **THEN** it finds the source-of-truth list in the stated order

### Requirement: SDD policy
The rules SHALL require OpenSpec for meaningful behavior, architecture, security, infrastructure, workflow, memory or installer changes in projects that use it, allow a lightweight path for editorial changes and behavior-neutral refactors, and forbid running `openspec init` without an explicit user request.

#### Scenario: SDD policy present
- **WHEN** the validator reads the methodology rules
- **THEN** it finds the OpenSpec trigger list, the lightweight exception and the no-auto-init rule

### Requirement: Delegation policy
The rules SHALL allow subagent delegation only for broad exploration, disjoint parallel edits, independent high-risk review, isolated research or bounded long tasks, and SHALL require each handoff to state objective, paths, scope, deliverables, verification, prohibited actions and the OpenSpec task reference.

#### Scenario: Handoff fields
- **WHEN** the validator reads the delegation rule
- **THEN** it finds all seven handoff fields

### Requirement: Token efficiency policy
The rules SHALL require targeted reads (search, line ranges, symbol skeletons), progressive disclosure, specific Engram queries, avoidance of repeated reads of unchanged files, and concise outputs, without trading off correctness or security.

#### Scenario: Token rule present
- **WHEN** the validator reads the methodology rules
- **THEN** it finds the token-efficiency section with the listed practices

### Requirement: Autonomy limits
The rules SHALL list operations requiring explicit approval: global installs or config changes, production deploys, cost-incurring cloud operations, destructive actions, sensitive permission changes, Git hook changes, publishing or pushing, memory integration changes, and sharing private data externally; approving a proposal MUST NOT authorize them.

#### Scenario: Approval list present
- **WHEN** the validator reads the autonomy rule
- **THEN** every listed operation appears

### Requirement: Task sizing by resumability
The rules SHALL classify a task as small when it is understood, its risk is contained and it could be resumed from the original request plus `git diff` alone; small tasks take the lightweight path without durable task artifacts, and file or command counts MUST NOT decide the size.

#### Scenario: Sizing rule present
- **WHEN** the validator reads the delegation rule
- **THEN** it finds the resumability criterion and the statement that file counts do not decide size

### Requirement: Main session as orchestrator
The rules SHALL state that the main session orchestrates: it owns requirements, conflict resolution, integration, final verification, memory writes and reporting, never runs two agents on the same feature or edit surface, and keeps subagent results as evidence to verify.

#### Scenario: Orchestrator responsibilities present
- **WHEN** the validator reads the delegation rule
- **THEN** it finds each orchestrator responsibility and the no-concurrent-writers clause
