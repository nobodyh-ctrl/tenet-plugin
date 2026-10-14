---
name: learn-concept
description: Teach a technical concept at the learner's level - check prerequisites, explain with real-world scenarios and examples, propose exercises and check understanding in stages. Use when the user wants to understand a concept (networking, Linux, cloud, IaC, Kubernetes, security, etc.), not just get code.
argument-hint: "[concept]"
---

# Learn a concept

## Steps
1. **Diagnostic.**
   - Read the learner profile (`profile.md` in the user rules) and recall prior progress. Use `mem_search` with scope `personal` and the topic key `learning/<topic>` when Engram is available.
   - Ask 2-3 short questions to place the learner. Never assume mastery from adjacent skills: knowing Docker does not mean knowing Kubernetes.
2. **Prerequisites.**
   - List what the concept builds on.
   - If a prerequisite is missing, offer a short detour first.
3. **Explain in stages.** Each stage has:
   - the core idea in plain words;
   - how it works mechanically;
   - a real-world scenario where it matters;
   - a minimal example (command, config or diagram);
   - common mistakes.

   Connect each stage to what the learner already knows.
4. **Checkpoint between major stages.**
   - Ask the learner to explain back or predict an outcome before moving on.
   - Give feedback that corrects misconceptions precisely.
   - **Skip option:** if the learner says "skip checks" or the task is professional and not educational, continue without checkpoints.
5. **Exercises.**
   - Propose 1-3 exercises of increasing difficulty with expected results.
   - Offer `/forge:hands-on-lab` for a practical lab.
6. **Record progress.** With the user's confirmation, save gaps and next steps (see `study-topic` for where they are stored).

## Verification
- A diagnostic was done before explaining.
- Each major stage ended with a checkpoint, unless the user skipped it.
- Exercises have stated expected results.
- No claim is presented as fact without being verifiable. Uncertain points are marked.
