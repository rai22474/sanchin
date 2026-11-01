# Artifacts

[README](../README.md) · [Docs](index.md)

The documents the process produces, what each must contain, and which rules
the validator enforces on them. Names, keys, headings and states are the
defaults; a project renames them in its adapter ([adapter.md](adapter.md)).
Starting points live in [templates/](../templates/).

## Project base documents

Every project keeps four documents the skills read instead of holding
principles of their own. The adapter says where each one is; `/sanchin:init`
creates the missing ones and grills their content with the user.

| Document | Says | Read by |
|---|---|---|
| Mission and vision | Why the product exists, where it is going, the design principles it names. Optionally one vision per component. | product-owner, architect |
| Stack | Languages, frameworks, test runners, external services. | developer, reviewer, init (to propose gates) |
| Constitution | Decision records, standards and design smells: the rules code must follow. Its files feed the plan's constitution checklist. | architect, developer, reviewer |
| Glossary | Domain terms and the synonyms to avoid. | every skill, to name things the way the project does |

*Why separate documents:* each has one reader and one reason to change. A
single free-form "context" field mixes them and goes stale as a block.

## Story

The spec. One file per story, under `stories.directory`. Written by the
product owner (technical stories by the architect, escalated bugs by the
maintainer); its state says which role holds it ([process.md](process.md#states)).

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

**Supersedes:** criterion 2 of [ST-7](st-07-export.md)

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
| The story says only the "what": no code, no current state. | review |
| The story is SMART — specific, measurable, achievable, relevant, time-bound (fits `stories.increment`) — [process.md](process.md#13-stories-from-a-narrative). | product owner at ready; tech-lead re-checks A and T against the plans |
| An implemented story, and its plans, are never edited after the commit that set it implemented (skipped without git, for `stories.legacy`, and while the close isn't committed). | validator |

## Scenarios

Executable acceptance scenarios, Gherkin by default (the adapter names the
runner). Feature files are organized by capability and are the living spec.
The product owner writes them when refining a story, tagged `@pending`; the
developer makes them red, then green, and drops the tag when the story
closes.

```gherkin
Feature: export

  # ST-12: AC 1, 2
  @pending
  Scenario: export includes archived items
    Given …
```

| Rule | Enforced by |
|---|---|
| Each scenario covering a criterion carries the trace comment above it; a trace comment not above a scenario is an error. | validator |
| Every feature file parses as Gherkin. | validator |
| A scenario whose stories are all unimplemented is tagged `@pending` (on itself, its rule or its feature); one covering an implemented story isn't. The runner skips the tag. | validator |
| Red for the right reason before the code exists. | developer, review |

## Plan

The "how" of one story for one component, written by the tech-lead.
Frozen once the story is implemented.

```markdown
# Plan — <what changes> (ST-12)

**Story:** [ST-12 — …](…) · **Other plans:** [api](…)

## 1. Current state        what the code does today, with file:line citations
## 2. Design               modules, contract, why this shape
## 3. Constitution checklist
- tramp-data: n/a
- layered-architecture: ok
- god-module: exception → D2
## 4. Risks
## 5. Tests                scenarios that cover it, new unit tests
## 6. Steps                ordered, each green before the next
## 7. Open questions       empty before code
## 8. Decisions            D1, D2 … from the technical grill
## 9. Implementation       what changed against the plan, and why
## 10. Review              findings with their source label and outcome
## 11. Retro               Planning (tech-lead) and Delivery (developer); see improvement.md
```

| Rule | Enforced by |
|---|---|
| Planned and in progress: Current state, Design and Steps exist (`required_sections.in_progress`). Implemented: also Implementation and Review. | validator (`required_sections`) |
| Open questions empty once the story is planned — the tech-lead sets it planned only after the technical grill closes them. | validator |
| Constitution checklist answers every constitution item that applies to the plan (global rules plus its component's) with an allowed verdict; every exception names a `D-n`. | validator |
| Plans that predate the rules are listed in `plans.legacy` and skipped. | validator |
| The plan doesn't restate the story; the contract lives in the provider's plan only. | review |

## Optional layers

With `layers` in the adapter a project adds **epics**, **narratives** and
**milestones** above stories; the product owner walks them in that order
(mission → epics → narratives → stories) and skips the ones that are off.
Narratives are vertical slices ordered from less to more functionality.
Their states, and the epics', are derived from their stories and generated,
never written by hand — by the project's own script; sanchin's validator
generates and checks the milestone tables.

## Roadmap

With the `milestone` layer, the roadmap is a set of **milestones**, one file
each under `roadmap.directory`: an objective in prose, the product owner's
state line, and a generated table of the stories that deliver it.

```markdown
# Milestone 2 — Export my data

[Docs](../index.md) · [Roadmap](index.md)

**State:** in progress.

## Objective

Why these stories ship together, and what is true when they have.

## Stories

<!-- sanchin:milestone-stories:start -->
| Story | State |
|---|---|
| [ST-12 — Export my data as CSV](../stories/st-12-export.md) | ready |
<!-- sanchin:milestone-stories:end -->
```

A story joins a milestone through `milestone:` in its frontmatter; the
table is regenerated with `sanchin roadmap --write`.

| Rule | Enforced by |
|---|---|
| A story ready, planned or in progress names its milestone; every named milestone exists. | validator |
| The state is planned, in progress or closed; at most one milestone is in progress. | validator |
| A milestone reads closed exactly when it has stories and all are implemented. | validator |
| The stories table is up to date. | validator |
| The order of milestones, and which stories go in each, is the product owner's decision. | review |

## Issues

A known bug. Symptom, root cause (once known), workaround, goal. In the bug
lane ([process.md](process.md#bug-lane)) the issue is the spec, and its
retro goes in the issue itself.
