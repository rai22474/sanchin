---
name: coach
description: Aggregates the retros of closed stories and bug fixes, finds the signals that reached the rule of two, measures what each review contributes, and proposes process changes each with its eval case. In a project set up for sanchin (one with .claude/sanchin.yaml), use monthly, when asked to improve the process or the skills, or when a review or a rule feels redundant or keeps failing.
---

Read `${CLAUDE_PLUGIN_ROOT}/docs/improvement.md` first: it defines the
signals, the retro and the rule of two.

1. **Collect** the Retro sections of plans and issues closed since the last
   coach run (the last run's date is in the project's process log, or ask),
   and the review sections of the same plans.
2. **Count**: findings by source label and by rule; corrections, repeated
   questions, escaped findings and gate failures by theme.
3. **Find** the signals that reached two. For each, decide where the change
   belongs: core (a sanchin skill or document) or project (adapter,
   standards, constitution); and whether a script could check it (then the
   change is a gate).
4. **Reviews**: report unique findings per source; if one source adds
   nothing over several stories, say so and propose dropping or narrowing it.
5. **Propose**, as selectable options, each change with the eval case that
   would fail today and pass after it (for core changes, in the shape of
   `${CLAUDE_PLUGIN_ROOT}/evals/`). Nothing is changed without the user's
   choice; core issues go to the sanchin repository only after confirmation,
   with nothing project-specific in them.
6. Record the run date and the outcome where the adapter says the project
   keeps its process log (`base_docs.process_log`), or in the coach's report.
