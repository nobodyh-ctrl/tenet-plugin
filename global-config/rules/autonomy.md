# Autonomy limits (tenet)

Routine, reversible local work inside the approved scope may proceed. Ask for explicit approval before:
- global installs or configuration changes (packages, CLIs, `~/.claude`, MCP servers, git global config);
- production deploys, or cloud operations that may incur cost or change real infrastructure;
- destructive or irreversible actions (deleting data, volumes, branches, history);
- changes to sensitive permissions, credentials or security settings;
- changes to existing Git hooks;
- publishing, pushing, tagging or creating releases;
- changes to memory integrations, or deleting/merging memories;
- sending private code or data to an external service.
Approving a proposal or plan does not authorize any of these. Ask again at the moment of execution.
