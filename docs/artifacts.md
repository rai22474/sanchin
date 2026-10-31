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

The spec. One file per story, under `stories.directory`.

```markdown
---
id: ST-12
state: pending            # pending | in progress | implemented
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
| Frontmatter has an id and a known state. | validator |
| `plan` and `scenarios` paths exist. An in-progress story has its plan; a story implemented on or after `rules_since` has its plan and scenarios (technical stories need no scenarios). | validator |
| No doubt marker (`[DOUBT: …]`) once the story leaves `pending`. | validator |
| Every criterion of a story implemented on or after `rules_since` is cited by a scenario, unless it carries the exemption text; every citation names an existing criterion. | validator |
| A supersedes link points to an existing story; the superseded-by table is up to date. | validator |
| Scenario delta matches the feature files: before implementation `~` and `−` exist; after it `+` and `~` exist and `−` is gone. | validator |
| The story says only the "what": no code, no current state. | review |
| An implemented story is never edited. | review (and git history) |

## Scenarios

Executable acceptance scenarios, Gherkin by default (the adapter names the
runner). Feature files are organized by capability and are the living spec.

```gherkin
Feature: export

  # ST-12: AC 1, 2
  Scenario: export includes archived items
    Given …
```

| Rule | Enforced by |
|---|---|
| Each scenario covering a criterion carries the trace comment above it. | validator (through criteria coverage) |
| Red for the right reason before the code exists. | developer, review |

## Plan

The "how" of one story for one component. Frozen once the story is
implemented.

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
## 11. Retro               see improvement.md
```

| Rule | Enforced by |
|---|---|
| In progress: Current state, Design and Steps exist. Implemented: also Implementation and Review. | validator (`required_sections`) |
| Open questions empty once the story is in progress. | validator |
| Constitution checklist answers every constitution item with an allowed verdict; every exception names a `D-n`. | validator |
| Plans that predate the rules are listed in `plans.legacy` and skipped. | validator |
| The plan doesn't restate the story; the contract lives in the provider's plan only. | review |

## Optional layers

With `layers` in the adapter a project adds **epics**, **narratives** and
**milestones** above stories. Their rules: narratives are vertical slices
ordered from less to more functionality; their states, and the milestone
tables, are derived from the stories and generated, never written by hand.
The generation is the project's own script; sanchin's validator only reads
stories.

## Issues

A known bug. Symptom, root cause (once known), workaround, goal. In the bug
lane ([process.md](process.md#bug-lane)) the issue is the spec, and its
retro goes in the issue itself.
