# repo-validation Specification

## Purpose
Guarantee through credential-free automated checks that the repository is structurally correct, safe to publish and compatible with Claude Code and OpenSpec.

## Requirements

### Requirement: Structural validator
`scripts/validate.py` SHALL check JSON/YAML syntax, manifests, marketplace, skill and agent frontmatter, `hooks.json`, internal links, manual and catalog structure, rule size budget and the absence of a plugin-root `CLAUDE.md`, exiting non-zero on any error.

#### Scenario: Valid repository
- **WHEN** `python scripts/validate.py` runs on the repository
- **THEN** it exits 0

#### Scenario: Broken skill
- **WHEN** a test copies the plugin and removes a skill's `description`
- **THEN** the validator exits non-zero naming the file

### Requirement: Secret and private-data scan
The validator SHALL fail on AWS keys, PEM private keys, GitHub/Anthropic tokens, local user paths (`C:\Users\<name>`, `/home/<name>`) and names of private products, except in fixtures marked as synthetic.

#### Scenario: Private key
- **WHEN** a test scans a file containing a PEM private key header
- **THEN** the scanner reports it

### Requirement: Read-only doctor
`scripts/doctor.py` SHALL report OS, Python, Claude Code, Engram, OpenSpec, GGA, Git and shells with versions, plugin and rules install state, and whether Engram is wired, without modifying anything.

#### Scenario: Read-only
- **WHEN** doctor runs against a temp config dir
- **THEN** the tree is unchanged

### Requirement: Dependency-free tests
The suite SHALL use stdlib `unittest`, run against temp dirs only, and cover the hook, installer, validator and metrics script.

#### Scenario: Suite run
- **WHEN** `python -m unittest discover -s tests` runs
- **THEN** all tests pass without touching real config or network

### Requirement: Continuous integration
A GitHub Actions workflow SHALL run validator and tests on Ubuntu and Windows, and on Ubuntu `shellcheck`, `claude plugin validate --strict` and `openspec validate --all --strict`, with no `secrets.` references.

#### Scenario: Credential-free workflow
- **WHEN** a test inspects `.github/workflows/ci.yml`
- **THEN** it contains no `secrets.` and defines the listed jobs
