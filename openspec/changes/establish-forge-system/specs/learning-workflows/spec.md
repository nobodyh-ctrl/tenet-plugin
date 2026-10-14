# Spec Delta

## Purpose

Support staged technical learning (concepts, labs, research, cloud security, networking) with prerequisite checks, comprehension checkpoints and progress tracking, without blocking professional work.

## ADDED Requirements

### Requirement: Learning skills
The plugin SHALL include `learn-concept`, `hands-on-lab`, `research-technology`, `aws-security`, `networking-lab` and `study-topic` with the same metadata and `## Verification` rules as engineering skills.

#### Scenario: Valid metadata
- **WHEN** the validator parses the learning skills
- **THEN** all have valid frontmatter and a `## Verification` section

### Requirement: Staged progression
`learn-concept` and `study-topic` SHALL start with a prior-knowledge check and place a comprehension checkpoint between major stages, which the user can explicitly skip; professional tasks MUST NOT require checkpoints.

#### Scenario: Checkpoints present
- **WHEN** the validator reads those skills
- **THEN** it finds the diagnostic step, the checkpoint and the skip option

### Requirement: Safe reproducible labs
`hands-on-lab`, `aws-security` and `networking-lab` SHALL define objective, authorized scope, prerequisites, steps, validation, cleanup and estimated cost for cloud resources, and MUST NOT target systems without authorization.

#### Scenario: Lab template
- **WHEN** the validator reads the `hands-on-lab` template
- **THEN** it contains all seven sections

### Requirement: Sourced research
`research-technology` SHALL prefer official documentation and separate sourced facts, recommendations and hypotheses in its output.

#### Scenario: Output sections
- **WHEN** the validator reads `research-technology`
- **THEN** its output format has the three separate sections

### Requirement: Progress tracking
Learning skills SHALL record gaps and next steps in Engram (`personal` scope, topic key per subject) when available, and otherwise in a user progress file outside `~/.claude/rules/`, after user confirmation.

#### Scenario: Storage location documented
- **WHEN** the validator reads `study-topic`
- **THEN** it names the Engram scope and the fallback file path
