# Continuous improvement

[README](../README.md) · [Docs](index.md)

The process improves the way code does: signals are captured, sorted into
changes, and each change is verified by a test. Nothing depends on an
agent's private memory, which other sessions and sub-agents never see.

## Signals

| Signal | What it reveals |
|---|---|
| A user correction ("don't do X") | A rule missing or unclear |
| Review findings, by source | Which step or review adds nothing; which rule is broken often |
| A grill question that keeps coming back | Something the template or adapter should answer |
| A gate failing again and again | A check to move earlier, or a rule for a skill |
| A bug found after its story closed | Which step should have caught it |
| A plan's Implementation section (deviations) | A plan or technical grill that fell short |

## The retro

Written by each role as its cycle ends, in the same commit, where that
cycle's artifact lives. Two minutes, five fields:

| Cycle | Written by | Where |
|---|---|---|
| Product | product owner | the story's **Retro** section, when it goes ready |
| Planning | tech-lead | the plan's **Retro** section, *Planning* (with several plans, the first one the story lists) |
| Delivery | developer | the same section, *Delivery*, when the story closes |
| Architecture | architect | the decision record's **Retro** section |
| Bug lane | maintainer | the issue |

```markdown
## Retro
- Corrections: the user asked to … (core | project)
- Repeated questions: …
- Escaped: finding X reached review; the cross-check should have caught it
- Gates: ruff failed 3 times on …
- Friction: …
```

Each point is classified:

- **core** — a sanchin skill or document should change → an issue on the
  sanchin repository, written without anything project-specific, opened
  only after the user confirms (it is public);
- **project** — the adapter, the project's standards or its constitution
  should change → a project issue or a direct doc change.

*Why where the artifact is:* each artifact is already the record of its
cycle, and a separate retro file would be one more thing to keep. *Why one
per cycle:* a correction made while refining or planning is a signal about
that cycle; written later by another role, it is second-hand or lost.

## Rule of two

A signal seen **once** stays in the retro. Seen **twice**, it becomes a
change: to a skill or a document, or — if a script can check it — a gate
([gates.md](gates.md)). *Why:* one occurrence may be noise; two is a pattern
worth the cost of a rule.

## Changing a skill

A skill change follows the same loop as a story:

1. add an eval case that fails without the change
   ([evals/](../evals), run with `evals/run.sh`);
2. change the skill;
3. the new case passes and the existing ones still do.

Every real correction becomes a regression case. *Why:* a skill rule that
isn't tested drifts silently, just like code.

## `/sanchin:coach`

Reads the retros since its last run, counts findings by source and by rule,
lists the signals that reached two, and proposes each change together with
its eval case. Run it monthly, or when a review feels redundant: it is also
what answers whether the two reviews are both worth their cost.

## Releases

sanchin follows semantic versioning with a [changelog](../CHANGELOG.md).
Projects pin a version. On upgrade, re-running `/sanchin:init` reports what
the adapter needs.
