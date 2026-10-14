---
name: version
description: Show the installed forge version and release channel. Use when the user asks which forge version is installed, or when reporting a problem.
disable-model-invocation: true
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
---

# forge version

## Steps
1. Read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` and take its `version` field. Never guess or reuse a version from memory or from this file's text.
2. Set the channel: `beta` if the version has a pre-release suffix (for example `-beta.1`), otherwise `stable`.
3. Reply in the user's language, using exactly this format:

```text
forge <version> (<channel>)
plugin path: ${CLAUDE_PLUGIN_ROOT}
```

4. Add one line:

   > For the full install state (rules, profile, Engram), run `python scripts/doctor.py` in the forge repository. To check from a terminal, run `claude plugin list`.

## Verification
- The version shown is the exact string read from `plugin.json` in this run.
- The channel matches the presence of a pre-release suffix.
