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
layers: [epic, narrative, milestone]   # optional layers in use; empty = stories only
components: [app, api]       # one plan per component a story touches
merge: local                 # local: merge into main | pr: push and open a pull request
generate:                    # the project's own commands that regenerate derived files
  - python3 scripts/build_narratives.py docs/roadmap

base_docs:                   # read by the skills (see artifacts/base-documents.md)
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
  keys: {id: id, state: state, date: date, plan: plan, scenarios: scenarios, kind: kind, milestone: milestone}
  technical_kind: technical
  states:                      # in the order a story goes through them
    pending: pending           # draft; doubts allowed
    ready: ready               # refined by the product owner
    planned: planned           # plans closed by the tech-lead
    in_progress: in progress   # being built by the developer
    implemented: implemented
  criteria_heading: Acceptance criteria
  criterion_exemption: '(no scenario:'
  doubt_marker: '[DOUBT:'
  supersedes_pattern: '\*\*Supersedes:\*\*[^\n]*?\]\(([^)\s]+)\)'
  superseded_index: docs/stories/superseded.md
  delta_heading: Scenario delta
  delta_trace_exemption: '(no trace:'   # on a delta line: a changed scenario that only renames
  rules_since: '2026-11-01'
  legacy: []                   # stories that predate the rules: closed, or in flight at adoption
  increment: 2 days            # how long a story may take from ready to merged (SMART: time-bound)

scenarios:
  globs: ['{component}/tests/features/**/*.feature']
  trace_comment: '^\s*#\s*(?P<story>ST-\d+):\s*AC\s+(?P<criteria>\d+(?:,\s*\d+)*)\s*$'
  pending_tag: '@pending'      # on scenarios written ahead of their code; '' turns the rule off
  run_pending: 'uv run pytest -m pending {file}'   # optional: how the developer runs them in red

models:                        # optional; per role: opus | sonnet | haiku | fable | inherit (default)
  product_owner: opus
  tech_lead: opus
  developer: sonnet
  reviewer: sonnet

session:
  fresh_per_cycle: block       # block (default) | warn | off — a role's cycle starts in a fresh session

approvals:                     # optional, the user's to write — Claude may not edit it; each: ask (default) | auto
  commit: auto                 # the commits the process prescribes, on main and on the story's branch
  costly_runs: auto            # the first costly run of a story's fix cycle
  merge: ask                   # merge + push + CI (or push + pull request), only with the local gates green

roadmap:                       # with the milestone layer on
  directory: docs/roadmap/milestones
  glob: '*.md'
  state_pattern: '^\*\*State:\*\*\s*(?P<state>[^.\n]+?)\s*\.?\s*$'
  states: {planned: planned, in_progress: in progress, closed: closed}

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
    globs: [docs/architecture/smells/*.md, 'docs/{component}/standards/*.md']
    verdicts: [n/a, ok, exception]   # the last one needs a D-n

gates:
  - {name: ruff, glob: '*.py', run: 'uv run ruff check {file}', level: edit}
  - {name: unit, glob: '*.py', run: 'uv run pytest -q', level: pre-push, timeout: 600}
```

## Fields

| Field | Used by | Notes |
|---|---|---|
| `version` | all | Adapter format version. Only `1` exists. |
| `language`, `terms` | skills | The skills write artifacts in this language and with these names. |
| `layers` | skills, validator | `epic`, `narrative`, `milestone`. Off by default. The product owner walks them in that order and skips a layer that is off ([process/product.md](process/product.md#1-product-cycle)). |
| `components` | skills, validator | `{component}` in any glob expands to each one. |
| `merge` | developer, maintainer | How a closed story or fix reaches `main`: `local` (default) merges it, `pr` opens a pull request and leaves the merge to the team ([process/delivery.md](process/delivery.md#35-close-retro-and-merge)). |
| `generate` | product owner, developer | Commands that regenerate the project's own derived files (narrative and epic states, a roadmap its own script builds); the roles run them at every hand-off that changes a state. A project whose script builds its milestones keeps the `milestone` layer off. |
| `base_docs.*` | skills | Where the four base documents, decisions, issues, proposals and templates live. |
| `docs.*` | validator | Progressive-context rules ([context.md](context.md)). |
| `stories.*` | validator, skills | Story rules ([artifacts/story.md](artifacts/story.md#story)). `rules_since` lets a project adopt the traceability rules without rewriting history; `legacy` lists stories (paths from the project root) that predate the rules — implemented ones that may lack a date, and ones already in flight when the project adopted sanchin, which may lack scenarios. `increment` is the short increment a story must fit, from ready to merged — free text the product owner and tech-lead size stories against ([process/product.md](process/product.md#13-stories-from-a-narrative)). |
| `stories.states` | validator, skills | The five states in order — `pending`, `ready`, `planned`, `in_progress`, `implemented` — mapped to the project's words; each says what the role that sets it owes ([process/states.md](process/states.md#states)). Values must differ. |
| `scenarios.*` | validator | Where feature files are and how a trace comment looks; `story` and `criteria` named groups are required. `pending_tag` (default `@pending`) marks scenarios written ahead of their code: every scenario whose stories are all unimplemented carries it, and none covering an implemented story does — the runner must skip it. `run_pending` (optional, read by the developer) is the command that runs them anyway, for the red run; without it the developer overrides the runner's tag filter. |
| `models.*` | skills | The model per role — `product_owner`, `tech_lead`, `developer`, `architect`, `maintainer`, `reviewer`, `coach` — one of `opus`, `sonnet`, `haiku`, `fable`, `inherit` (default). The role's sub-agents run on it; the role itself, on starting, says so when the session runs another, and goes on ([process/working-rules.md](process/working-rules.md#models)). |
| `approvals.*` | skills, hook | `commit`, `costly_runs`, `merge`: `ask` (default) or `auto`, done without asking — the steps each covers are in [process/working-rules.md](process/working-rules.md#approvals). The user's to set: a hook denies Claude's edits to this section. |
| `session.fresh_per_cycle` | hook | `block` (default), `warn` or `off`: what the prompt hook does when a role's skill is invoked in a session another role already used ([process/working-rules.md](process/working-rules.md#one-session-per-cycle)). |
| `roadmap.*` | validator, product owner | Required with the `milestone` layer: where milestones live, the regex for a milestone's state line (a `state` group), and its three state values. Each story names its milestone (`keys.milestone`); `sanchin roadmap --write` regenerates each milestone's stories table ([artifacts/layers-and-roadmap.md](artifacts/layers-and-roadmap.md#roadmap)). |
| `acceptance.*` | developer, maintainer | How to run acceptance scenarios, and whether a run is costly. |
| `plans.*` | validator | Plan rules ([artifacts/plan.md](artifacts/plan.md#plan)). In `constitution.globs`, `{component}` expands to the plan's own component — the first component named in the plan's path — so a plan answers the global rules plus its component's; a plan whose path names no component answers every component's. |
| `gates[]` | hook, `sanchin gates` | `level` is `edit`, `pre-commit`, `pre-push` or `ci`; `{file}` is replaced by the file path, and a gate without it runs once for all files; `timeout` in seconds, default 120 ([gates.md](gates.md)). |

Unknown keys are ignored by the validator; the skills may read keys it
doesn't. Paths are relative to the project root.

## Layers

`layers: []` gives the smallest process: stories, scenarios, plans. Turn a
layer on when the project needs it, not before. `/sanchin:init` turns on the
layers it finds already in use.
