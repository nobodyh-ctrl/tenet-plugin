# Token and context efficiency (tenet)

Optimize total task cost (tokens, tool calls, rework), never at the expense of correctness or security.
- Read narrowly: targeted search, line ranges, symbol skeletons; whole files only when needed. Do not re-read unchanged files.
- Load skills, manual sections and memories on demand; query Engram for specific topics, never "everything".
- Summarize findings as `path:line` plus the verified conclusion instead of quoting large blocks.
- Keep durable task state in an artifact (OpenSpec tasks, plan file) when it improves resumability, instead of repeating it in chat.
- Be concise in output; expand only when the user asks or the decision needs it.
- Treat cached test or review results as stale when their inputs changed.
