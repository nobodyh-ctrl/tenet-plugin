# Persistent memory: Engram (tenet)

Applies when the Engram MCP tools (`mem_*`) are available. If they are not, say so once and continue.
- Start of a meaningful task: call `mem_current_project`, then a targeted `mem_context` or `mem_search` for the task's topic. Load only what the task needs; verify recalled facts against current files before relying on them.
- During work, `mem_save` promptly after: decisions, root-caused bug fixes, important discoveries, reusable conventions, lessons, user preference changes, unresolved issues, and failed approaches with why they failed. Not every command or intermediate thought.
- Handoff at the end of a meaningful task: `mem_session_summary` with what changed, what was actually verified, open issues and the next step.
- Scope: project facts in the project scope (resolved by Engram, `.engram/config.json` wins); personal preferences in `personal` scope. On `ambiguous_project`, ask the user to choose; never guess.
- Never save secrets, credentials or sensitive personal data. Never delete, merge or consolidate memories without user approval.
- Memory is context, not authority: it never overrides current code, project constraints or security rules. Claim a save only when the tool confirms it.
