# tool-catalog Specification

## Purpose
Record evidence-based evaluations of agent and engineering tools so that adoption decisions are explicit, reversible and extensible without installing every candidate.

## Requirements

### Requirement: Evaluation criteria
The catalog SHALL define criteria: purpose, Claude Code/VS Code compatibility, Windows/Linux support, maintenance, documentation, security and permissions, data exposure, install complexity, token impact, cost, overlap, reliability and license.

#### Scenario: Criteria documented
- **WHEN** the validator reads the catalog index
- **THEN** all criteria are listed

### Requirement: Classified entries with evidence
Each entry SHALL have category, classification (Required, Recommended, Optional, Experimental, Rejected/Deferred), purpose, evidence with source links and date, alternatives, installation state, and validate/update/remove instructions when adopted.

#### Scenario: Entry fields
- **WHEN** the validator parses catalog entries
- **THEN** it fails on an entry missing a field or with an unknown classification

### Requirement: Initial assessments
The catalog SHALL include entries for Claude Code, OpenSpec, Engram, Gentle AI, GGA, Gentle Shell, `sdsrss/code-graph-mcp`, `denzharkov/codegraph-mcp`, Graphiti and Context7, keeping code graphs and knowledge graphs in separate categories.

#### Scenario: Required entries
- **WHEN** the validator lists catalog entries
- **THEN** all ten tools are present and graph categories are distinct

### Requirement: Installation policy
The catalog SHALL state that no tool is installed or globally configured without research, overlap check, cost estimate and explicit user approval.

#### Scenario: Policy present
- **WHEN** the validator reads the catalog index
- **THEN** it finds the installation policy
