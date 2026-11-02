---
name: coach
description: Aggregates the retros of closed stories and bug fixes, finds the signals that reached the rule of two, measures what each review contributes, and proposes process changes each with its eval case. In a project set up for sanchin (one with .claude/sanchin.yaml), use monthly, when asked to improve the process or the skills, or when a review or a rule feels redundant or keeps failing.
---

Read `${CLAUDE_PLUGIN_ROOT}/docs/improvement.md` first: it defines the
signals, the retro and the rule of two.

**Model.** If the adapter's `models.coach` names a model other than the
one you run on, say so in one line — naming
`/model <that model>` — and go on; don't ask. Every sub-agent you
dispatch gets `model: <models.coach>` unless it is `inherit` or unset
([working-rules.md](${CLAUDE_PLUGIN_ROOT}/docs/process/working-rules.md#models)).

1. **Collect** the Retro sections written since the last coach run (the
   last run's date is in the project's process log, or ask) — stories
   (product), plans (planning and delivery), decision records
   (architecture), issues (bug lane) — and the review sections of the same
   plans. Count each signal under the cycle that wrote it.
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
