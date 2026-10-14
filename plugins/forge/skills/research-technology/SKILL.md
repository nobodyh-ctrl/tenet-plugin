---
name: research-technology
description: Research a technology, tool or approach using official documentation and reliable sources, compare alternatives, and separate verified facts from recommendations and hypotheses. Use when choosing a technology, checking current versions or capabilities, or answering "should we use X".
allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)
argument-hint: "[question]"
---

# Research a technology

## Steps
1. **Frame the questions.** Write 1-3 precise research questions and the decision they feed into.
2. **Check what is already known.**
   - Check `${CLAUDE_PLUGIN_ROOT}/manual/catalog/technologies.md` and `${CLAUDE_PLUGIN_ROOT}/manual/catalog/tools.md`.
   - Run `mem_search` for previous evaluations.
3. **Gather sources, best first.**
   - Official docs, release notes and repositories first.
   - Then reputable secondary sources.
   - Record the version and date for each fact. Fetch only the sections you need; never dump whole docs into context.
   - Optional: delegate isolated research to a subagent when it would otherwise flood the main context.
4. **Compare alternatives.**
   - Use the criteria in `${CLAUDE_PLUGIN_ROOT}/manual/catalog/README.md`: purpose, compatibility, platforms, maintenance, security, data exposure, cost, overlap, license.
5. **Record the outcome.**
   - Propose a catalog entry update when relevant. Normative changes go through OpenSpec in the forge repo.
   - `mem_save` the decision (type `decision`).
6. **Next steps.** Prototype, lab, or adopt, with what would change the conclusion.

## Output format
- **Verified facts:** each with a source link and its date or version.
- **Recommendations:** what to do and why, tied to the facts above.
- **Hypotheses and unknowns:** what is assumed or unverified, and how to verify it.
- **Next steps.**

## Verification
- Every fact has a source.
- Facts, recommendations and hypotheses are in separate sections.
- Version-sensitive claims name the version checked.
