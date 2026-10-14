# Catalogs

- [tools.md](tools.md): agent and engineering tooling such as memory, configuration, code intelligence, review and documentation.
- [technologies.md](technologies.md): languages, frameworks, data stores, infrastructure and delivery technologies used to build products.

## Evaluation criteria

Each tool or technology is evaluated against these criteria. An entry records the ones that matter for its decision.

1. Clear purpose and the problem it solves.
2. Compatibility with Claude Code and VS Code.
3. Windows and Linux support.
4. Maintenance activity: releases, commits, issue response.
5. Documentation quality.
6. Security and the permissions it requires.
7. Data exposure: what leaves the machine, and to whom.
8. Installation complexity and footprint on global configuration.
9. Token and context impact.
10. Runtime and infrastructure cost.
11. Overlap with tools already adopted.
12. Reliability and measurable value.
13. License and distribution constraints.

## Classifications

**Tools:**
- `Required`: part of the core system.
- `Recommended`: default when its need applies.
- `Optional`: use per project when justified.
- `Experimental`: under evaluation in isolation.
- `Rejected`: do not use; the reason is recorded.
- `Deferred`: revisit later.

**Technologies:**
- `Adopted`: proven default.
- `Trial`: use on a real project with a fallback.
- `Assess`: learn and prototype only.
- `Hold`: do not start new work with it.

## Entry format

**Tool entries** are `###` headings with these bullets:
- Category
- Classification
- Purpose
- Evidence (sources and date)
- Alternatives
- Installation state
- Lifecycle (validate, update, remove)

**Technology entries** are `###` headings with these bullets:
- Purpose
- Use cases
- Trade-offs
- Security
- Cost
- Operational complexity
- Alternatives
- Status

## Installation policy

No tool is installed or allowed to change global configuration until all of these are done:
1. Its official repository and docs were researched.
2. Maintenance, compatibility, prerequisites and security were verified.
3. Overlapping tools were identified.
4. Operational and token cost were estimated.
5. The expected benefit was stated.
6. A minimal configuration was proposed.
7. The user explicitly approved it.

After installation, it is tested, and the validate, update and remove steps are recorded in its entry.

Never run install commands copied from a repository without reading what they change. Prefer an isolated trial (temp `HOME`, `CLAUDE_CONFIG_DIR`) before touching real configuration.
