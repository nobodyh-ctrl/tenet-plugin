---
name: project-init
description: Onboard a new or existing repository to the tenet way of working - inspect it, capture product context and constraints, choose architecture and technologies with explicit criteria, define testing, deployment and observability, and propose project instruction files, ADRs, Engram and OpenSpec setup. Use when starting a new app or bringing an existing repo under tenet.
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[product idea or repo path]"
---

# Project init

The main session orchestrates. **Nothing is written until the user approves the file list.**

## Steps
1. **Inspect the repository.**
   - Check `git status` and the branch, and read the existing instructions (AGENTS.md, CLAUDE.md, README).
   - Detect the stack from manifests (package.json, *.csproj/*.sln, pyproject.toml, go.mod, Dockerfile, compose files, IaC folders, `.github/workflows`).
   - For an empty repo, record that it is greenfield.
   - Optional `explorer`: use it for a large existing codebase, to get a `path:line` map of modules, entry points, data access and tests.
2. **Recall.** If Engram is available, run `mem_current_project` and `mem_search` for prior decisions about this product.
3. **Capture product context.** Ask only what cannot be inferred, in one compact round of questions:
   - purpose and users;
   - critical flows;
   - data sensitivity (personal data, payments);
   - expected scale;
   - availability target;
   - cost ceiling;
   - deployment target;
   - team size;
   - compliance needs.
4. **Choose the architecture and technologies.**
   - Use `${CLAUDE_PLUGIN_ROOT}/manual/core/architecture.md` and `${CLAUDE_PLUGIN_ROOT}/manual/catalog/technologies.md`.
   - Present the options with criteria and a recommendation.
   - AWS, Terraform, Docker and Kubernetes are options that need a justification. They are not defaults for every project.
   - Every deviation from a manual SHOULD needs a stated reason.
   - Optional `architect`: use it only when the trade-offs are genuinely close.
5. **Define how the project is built, tested and run.** Use `${CLAUDE_PLUGIN_ROOT}/manual/core/quality.md` and `${CLAUDE_PLUGIN_ROOT}/manual/delivery/containers-and-cicd.md`. Cover:
   - test strategy and the CI checks;
   - environments, deployment target and rollback;
   - observability and backups (`${CLAUDE_PLUGIN_ROOT}/manual/delivery/operations.md`);
   - security baseline (`${CLAUDE_PLUGIN_ROOT}/manual/security/secure-engineering.md`).
6. **Propose the files, then STOP.** List exactly which files you would create or change, with a one-line purpose each. Templates are in [templates/](templates/):
   - `AGENTS.md`: project instructions, from `templates/AGENTS.md`.
   - `CLAUDE.md`: contains `@AGENTS.md` and nothing else.
   - `docs/adr/0001-architecture.md` (plus data store and deployment ADRs as needed), from `templates/adr.md`.
   - `docs/decisions.md`: the decision log, from `templates/decision-log.md`.
   - `.engram/config.json`: pins the Engram project name, from `templates/engram-config.json`.
   - **Offer** OpenSpec (`openspec init --tools claude`) for long-lived projects. Run it only if the user explicitly says yes.

   Never overwrite existing files. If a target exists, propose a merge or diff instead.
7. **Write only after approval.** Fill the templates with the decided facts. Leave `TBD` for open decisions; never invent facts.
8. **Record.**
   - `mem_save` the key decisions (type `architecture`).
   - Report the unresolved decisions with owners and the next step, usually the first `/tenet:feature`.

## Verification
- No file was written before explicit approval of the file list.
- Existing files were not overwritten.
- Each technology choice has a recorded reason in an ADR or the decision log.
- `openspec init` ran only if the user explicitly asked for it.
- The resulting AGENTS.md lists real, working commands, or marks them TBD.
