# Task sizing, delegation and orchestration (forge)

- Size by resumability, not by file or command count: a task is small when it is understood, its risk is contained, and it could be resumed from the original request plus `git diff` alone. Small tasks run inline on the lightweight path; larger ones get a plan or an OpenSpec change.
- The main session is the orchestrator: it owns requirements, conflict resolution between recommendations, integration, final verification, memory writes and the report. Subagent output is evidence to verify, not truth.
- Delegate only with a named reason: broad exploration whose evidence will not fit one inline batch (~3 searches/reads), parallel work on disjoint edit surfaces, independent review of a high-risk change, isolated research, or a long bounded task with a clear handoff.
- Prefer one focused `explorer` returning a `path:line` map over several agents reading the same files. Never run two agents on the same feature or edit surface.
- Every handoff states: objective, relevant paths, approved scope, expected deliverable, required verification, prohibited actions, and the OpenSpec change/task reference. Reference files; do not paste large content.
- Subagents do not inherit this conversation. They never push, deploy, apply infrastructure, delete persistent data or write memory.
