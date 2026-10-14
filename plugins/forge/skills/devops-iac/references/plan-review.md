# Plan review checklist

Summarize every IaC plan or deployment diff with:

| Item | What to report |
|---|---|
| Counts | to add / to change / to destroy |
| Replacements | Resources forcing replacement (`-/+`), and why |
| Data risk | Databases, volumes, buckets or queues being destroyed or replaced |
| Cost | New billable resources and size changes; estimate the monthly impact when possible |
| Exposure | Public IPs, `0.0.0.0/0` rules, public buckets, new endpoints |
| IAM | New or widened policies, wildcards, cross-account trust |
| State | Imports, moves, removals, backend changes |
| Rollback | How to revert if apply fails halfway |

Stop and ask for approval when any of these holds:
- the destroy count is greater than zero;
- there is a data risk;
- the change adds public exposure;
- IAM is widened;
- the target is a production environment.
