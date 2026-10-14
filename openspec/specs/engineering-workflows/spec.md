# engineering-workflows Specification

## Purpose
Provide invocable engineering skills and end-to-end workflows (feature, bugfix, release, project onboarding) that apply the methodology and the Engineering Manual in any repository.

## Requirements

### Requirement: Engineering skills
The plugin SHALL include `plan-work`, `implement`, `review-code`, `verify-changes`, `documentation` and `devops-iac`, each with `name` equal to its directory, a `description` of at most 1536 characters stating when to use it, and a `## Verification` section.

#### Scenario: Metadata and sections
- **WHEN** the validator parses each engineering `SKILL.md`
- **THEN** it finds valid frontmatter and a `## Verification` section

### Requirement: Concise skills with references
Each `SKILL.md` SHALL be under 300 lines; longer material MUST live in referenced files that exist.

#### Scenario: Size and links
- **WHEN** the validator checks every skill
- **THEN** it fails on a `SKILL.md` of 300+ lines or a link to a missing file

### Requirement: OpenSpec delegation without duplication
`plan-work`, `implement`, `verify-changes`, `review-code` and `documentation` SHALL delegate to the official OpenSpec workflows (`/opsx:propose`, `/opsx:apply`, `openspec validate`, `/opsx:archive`) when the project has `openspec/`, and use a lightweight plan otherwise.

#### Scenario: Official commands referenced
- **WHEN** the validator scans those skills
- **THEN** each references `/opsx:` or `openspec validate`

### Requirement: Feature, bugfix and release workflows
The plugin SHALL include `feature`, `bugfix` and `release` workflow skills; `release` MUST stop before push, tag, release or deploy until the user explicitly approves.

#### Scenario: Release stop point
- **WHEN** the validator reads `release`
- **THEN** it finds an explicit stop step before publishing operations

### Requirement: Project onboarding
`project-init` SHALL inspect the repository, read instructions, query Engram, check Git status, capture product constraints, select architecture and technologies against Manual criteria, define testing, deployment and observability, record decisions, and offer (never force) OpenSpec init, a project instruction file and `.engram/config.json`.

#### Scenario: Files only with approval
- **WHEN** `project-init` is run on a synthetic fixture repository
- **THEN** it presents the files it would create and writes none before approval

#### Scenario: No imposed stack
- **WHEN** the validator reads `project-init`
- **THEN** it states that AWS, Terraform, Docker and Kubernetes are options requiring justification, not defaults for every project

### Requirement: IaC safety
`devops-iac` SHALL require reviewing `plan`/`diff`/`--check` output before any apply and flag cost, broad IAM and resource destruction risks.

#### Scenario: Plan before apply
- **WHEN** the validator reads `devops-iac`
- **THEN** it finds the plan-review and approval requirement before `apply` or `destroy`

### Requirement: Workflow orchestration points
`feature`, `bugfix` and `project-init` SHALL name where subagents may be used (`explorer` for broad discovery, `architect` for design alternatives, `implementer` for bounded disjoint edits, `reviewer`/`security-reviewer` for independent checks of high-risk changes) and SHALL keep each optional, gated by the delegation triggers.

#### Scenario: Orchestration steps
- **WHEN** the validator reads the `feature` skill
- **THEN** it finds each named agent tied to a step and a condition for delegating
