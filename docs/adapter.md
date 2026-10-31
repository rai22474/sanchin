# The adapter

[README](../README.md) · [Docs](index.md)

`.claude/sanchin.yaml` is the only place a project tells sanchin where its
artifacts live and what it calls them. The skills, the validator and the
hook all read it; none of them knows anything about a particular project.
`/sanchin:init` writes it, mapping what already exists.

*Why one file:* a process that is reproducible across projects needs one
seam between the generic and the specific. Everything project-specific goes
through it; everything else is the same everywhere.

## Full example

```yaml
version: 1
language: en                 # language of the project's docs
terms:                       # what the project calls each artifact
  story: story
  epic: epic
  narrative: narrative
  milestone: milestone
layers: [epic, narrative]    # optional layers in use; empty = stories only
components: [app, api]       # one plan per component a story touches

base_docs:                   # read by the skills (see artifacts.md)
  mission_vision: docs/product/vision.md
  component_vision: docs/{component}/vision.md
  stack: docs/stack.md
  constitution: docs/architecture/index.md
  glossary: docs/glossary.md
  decisions: docs/architecture/decisions/
  issues: docs/issues/
  proposals: docs/proposals/
  templates: docs/templates/
  process_log: docs/process-log.md   # where /sanchin:coach records its runs

docs:
  root: docs
  index: docs/index.md
  navigation_line: '^\[Docs\]\('          # regex for the line below each title
  unindexed_catalogs: [stories]           # directories listed by generated tables
  code_reference_globs: ['{component}/src/**/*.py']

stories:
  directory: docs/stories
  glob: 'st-*.md'
  keys: {id: id, state: state, date: date, plan: plan, scenarios: scenarios, kind: kind}
  technical_kind: technical
  states: {pending: pending, in_progress: in progress, implemented: implemented}
  criteria_heading: Acceptance criteria
  criterion_exemption: '(no scenario:'
  doubt_marker: '[DOUBT:'
  supersedes_pattern: '\*\*Supersedes:\*\*[^\n]*?\]\(([^)\s]+)\)'
  superseded_index: docs/stories/superseded.md
  delta_heading: Scenario delta
  rules_since: '2026-11-01'

scenarios:
  globs: ['{component}/tests/features/**/*.feature']
  trace_comment: '^\s*#\s*(?P<story>ST-\d+):\s*AC\s+(?P<criteria>\d+(?:,\s*\d+)*)\s*$'

acceptance:
  run: 'make acceptance COMPONENT={component}'
  costly: true                 # ask before entering a fix cycle

plans:
  directory: docs/plans
  rules_since: '2026-11-01'
  legacy: []                   # plans written before the rules
  required_sections:
    in_progress: [Current state, Design, Steps]
    implemented: [Current state, Design, Steps, Implementation, Review]
  open_questions_section: Open questions
  constitution:
    section: Constitution checklist
    globs: [docs/architecture/smells/*.md]
    verdicts: [n/a, ok, exception]   # the last one needs a D-n

gates:
  - {name: ruff, glob: '*.py', run: 'uv run ruff check {file}', level: edit}
  - {name: unit, glob: '*.py', run: 'uv run pytest -q', level: pre-push}
```

## Fields

| Field | Used by | Notes |
|---|---|---|
| `version` | all | Adapter format version. Only `1` exists. |
| `language`, `terms` | skills | The skills write artifacts in this language and with these names. |
| `layers` | skills | `epic`, `narrative`, `milestone`. Off by default. |
| `components` | skills, validator | `{component}` in any glob expands to each one. |
| `base_docs.*` | skills | Where the four base documents, decisions, issues, proposals and templates live. |
| `docs.*` | validator | Progressive-context rules ([context.md](context.md)). |
| `stories.*` | validator, skills | Story rules ([artifacts.md](artifacts.md#story)). `rules_since` lets a project adopt the traceability rules without rewriting history. |
| `scenarios.*` | validator | Where feature files are and how a trace comment looks; `story` and `criteria` named groups are required. |
| `acceptance.*` | developer, maintainer | How to run acceptance scenarios, and whether a run is costly. |
| `plans.*` | validator | Plan rules ([artifacts.md](artifacts.md#plan)). |
| `gates[]` | hook, `sanchin gates` | `level` is `edit`, `pre-commit`, `pre-push` or `ci`; `{file}` is replaced by the file path ([gates.md](gates.md)). |

Unknown keys are ignored by the validator; the skills may read keys it
doesn't. Paths are relative to the project root.

## Layers

`layers: []` gives the smallest process: stories, scenarios, plans. Turn a
layer on when the project needs it, not before. `/sanchin:init` turns on the
layers it finds already in use.
