---
name: study-topic
description: Structured study session on a topic - assess prior knowledge, set a goal, explain concepts with examples, practice, check understanding and record gaps and next steps. Use when the user wants to study or plan learning on a subject (Linux, networking, AWS, Terraform, Ansible, Kubernetes, OpenShift, security, Python, DevOps).
argument-hint: "[topic]"
---

# Study a topic

## Steps
1. **Assess prior knowledge.**
   - Read the profile and recall progress. If Engram is available, run `mem_search` with scope `personal` and query `learning/<topic>`. Otherwise, read the progress file below.
   - Ask 2-3 diagnostic questions.
2. **Set the goal.** Agree on one concrete, observable goal for the session. Example: "subnet a /24 into four networks and explain why".
3. **Explain concepts** in stages, using `/tenet:learn-concept`.
4. **Show examples** tied to real scenarios and, where possible, to the learner's own projects.
5. **Practice.** Give exercises, or a lab with `/tenet:hands-on-lab`, `/tenet:networking-lab` or `/tenet:aws-security`.
6. **Check understanding.** Ask the learner to explain, predict or solve without help.
   - **Checkpoint:** do not advance to the next major stage until they demonstrate it.
   - **Skip option:** the user can say "skip checks". Professional tasks never require checks.
7. **Record gaps and next steps.** Ask for confirmation before writing, then save to one of:
   - **Engram (preferred):** `mem_save` with scope `personal`, topic key `learning/<topic>`, content listing what was mastered, the gaps, misconceptions corrected, and the next step.
   - **Fallback file:** `~/.claude/tenet/learning-progress.md`. Append a dated section. This file is outside `~/.claude/rules/`, so it is never auto-loaded.

## Verification
- A diagnostic was done and a goal was stated.
- At least one understanding check happened, unless the user skipped it.
- Progress was saved only after confirmation, and the save was confirmed by the tool or the file write.
