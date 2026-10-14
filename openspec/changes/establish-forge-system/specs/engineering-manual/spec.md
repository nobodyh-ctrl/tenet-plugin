# Spec Delta

## Purpose

Maintain a reusable, versioned Engineering Manual of standards and decision frameworks that skills load on demand, guiding any project without imposing one stack.

## ADDED Requirements

### Requirement: Manual structure
The manual SHALL live in the plugin under `manual/` with an index and sections for core engineering, infrastructure and delivery, security, and technology catalog, each covering the domains listed in design decision D6.

#### Scenario: Index coverage
- **WHEN** the validator reads `manual/README.md`
- **THEN** every section file it links exists and every section file is linked

### Requirement: Normative levels
Every standard SHALL be marked `MUST`, `SHOULD` or `EXPERIMENTAL`, and mandatory standards MUST be few and justified.

#### Scenario: Levels marked
- **WHEN** the validator scans manual standards
- **THEN** each standard line carries one of the three markers

### Requirement: Provider-agnostic principles
Principles SHALL be provider-agnostic; provider specifics SHALL live in provider subsections (AWS first) tied to concrete use cases, so another provider can be added without editing principles.

#### Scenario: Provider isolation
- **WHEN** the validator scans principle files
- **THEN** AWS service names appear only in provider-specific files

### Requirement: Technology entries
Each technology catalog entry SHALL state purpose, use cases, trade-offs, security, cost, operational complexity, alternatives and status.

#### Scenario: Entry completeness
- **WHEN** the validator parses catalog entries
- **THEN** it fails on an entry missing any of the eight fields

### Requirement: Controlled evolution
The manual SHALL state that normative changes go through OpenSpec and that project-specific lessons are promoted only when reusable.

#### Scenario: Evolution rule
- **WHEN** the validator reads `manual/README.md`
- **THEN** it finds the evolution rule

### Requirement: On-demand loading
The manual MUST NOT be imported into always-loaded rules; skills SHALL reference specific sections by path.

#### Scenario: Not always loaded
- **WHEN** the validator scans `global-config/rules/`
- **THEN** no rule imports or inlines manual files
