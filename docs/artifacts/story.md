# Story

[README](../../README.md) · [Docs](../index.md) · [Artifacts](index.md)

The spec. One file per story, under `stories.directory`. Written by the
product owner (technical stories by the architect, escalated bugs by the
maintainer); its state says which role holds it ([process/states.md](../process/states.md#states)).

```markdown
---
id: ST-12
state: ready              # pending | ready | planned | in progress | implemented
milestone: m-02-export    # with the milestone layer: the roadmap places it
date: 2026-11-03          # set when implemented
plan: docs/plans/app/export.md, docs/plans/api/export.md
scenarios: app/features/export.feature
kind: technical           # only for technical stories
---
# ST-12 — Export my data as CSV

As a <user>, I want <capability>, so that <value>.

## Acceptance criteria

1. …
2. … (no scenario: why this criterion can't be automated)

**Supersedes:** criterion 2 of [ST-7](../st-07-export.md)

## Scenario delta

- + app/features/export.feature: export includes archived items
- ~ app/features/export.feature: export of an empty account
- − app/features/export.feature: export only active items

## Out of scope

- …
```

| Rule | Enforced by |
|---|---|
| Frontmatter has a unique id and a known state; an implemented story has its date. | validator |
| `plan` and `scenarios` paths exist. | validator |
| **ready** on: no doubt marker; its scenarios (technical stories excepted), every criterion cited unless it carries the exemption text; its milestone, with that layer on. | validator |
| **planned** and **in progress**: its plans, held to the plan rules. | validator |
| **implemented** on or after `rules_since`: plans and scenarios, every criterion cited. | validator |
| Every citation names an existing story and criterion. | validator |
| A supersedes link points to an existing story; the superseded-by table is up to date. | validator |
| Scenario delta matches the feature files: pending, `~` and `−` exist; ready on, `+` too; implemented, `+` and `~` exist and `−` is gone. | validator |
| A delta's `+` scenarios (ready on) and `~` scenarios (implemented) carry this story's trace; a rename says `(no trace: …)` on its line. | validator |
| The story says only the "what": no code, no current state. | review |
| The story is SMART — specific, measurable, achievable, relevant, time-bound (fits `stories.increment`) — [process/product.md](../process/product.md#13-stories-from-a-narrative). | product owner at ready; tech-lead re-checks A and T against the plans |
| An implemented story, and its plans, are never edited after the commit that set it implemented (skipped without git, for `stories.legacy`, and while the close isn't committed). | validator |
