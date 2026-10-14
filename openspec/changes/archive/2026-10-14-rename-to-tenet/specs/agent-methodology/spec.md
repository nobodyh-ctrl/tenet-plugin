# Spec Delta

## MODIFIED Requirements

### Requirement: Concise always-loaded rules
The methodology SHALL be shipped as Markdown rules for `~/.claude/rules/tenet/` totalling at most 120 lines, with detailed guidance moved to skills or the Engineering Manual and referenced, not copied.

#### Scenario: Size budget
- **WHEN** the validator counts lines across `global-config/rules/*.md`
- **THEN** it fails if the total exceeds 120 lines
