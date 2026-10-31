<p align="center">
  <img src="assets/logo.svg" alt="sanchin" width="160">
</p>

<h1 align="center">sanchin</h1>

<p align="center"><b>A reproducible, spec-first development process for Claude Code.</b><br>
Executable specs · validated artifacts · deterministic gates · progressive context.</p>

---

*Sanchin* (三戦, "three battles") is the foundational kata of Naha-te and
Gōjū-ryū: the form a karateka repeats for life, the same way every time,
until it is second nature. This plugin is that idea applied to building
software with an agent — one process, repeated the same way on every story,
in every project, and improved a little after each one.

It packages a loop that grew inside a real multi-service project: stories
grilled with the user, scenarios red before code, a plan per component, two
reviews, and a retro that feeds the process itself. Everything specific to
that project went into an **adapter**; what is left is the process.

## Contents

- [The four pillars](#the-four-pillars)
- [The loop](#the-loop)
- [Roles](#roles)
- [Quickstart](#quickstart)
- [Decisions](#decisions)
- [How it compares](#how-it-compares)
- [Docs](#docs)

## The four pillars

1. **Executable specs.** Every acceptance criterion has a scenario that
   cites it and that fails for the right reason before the code exists.
   Feature files, organized by capability, are the living description of the
   system — not a prose spec someone has to keep true by hand.
2. **Validated artifacts.** Stories, plans, scenario deltas, doubt markers
   and constitution checklists are checked by a validator, not by goodwill.
3. **Deterministic gates.** What can be checked by code is checked by code,
   at the earliest level where it is cheap — from the moment Claude saves a
   file to CI.
4. **Progressive context.** Thin entry points and indexes that say *what*
   each document holds and *when* to read it, so an agent loads the ten
   documents its task needs instead of all two hundred.

And one principle that ties them together: **specs are immutable and
incremental.** An implemented story is never edited; a change is a new
story with a *supersedes* line and a scenario delta (+ / ~ / −), and the
current behaviour is whatever the scenarios — kept true by the tests — say.

## The loop

```mermaid
flowchart TD
  idea([idea]) --> PO["product-owner · what, in which order"]
  PO --> AR["architect · does it fit"]
  AR --> EP["developer · grill into an epic, break into stories"]
  EP --> FG

  subgraph story ["per story — own branch + worktree"]
    FG["functional grill<br/>doubt markers answered"] --> RED["scenarios red<br/>traced to criteria"]
    RED --> PL["one plan per component<br/>constitution checklist"]
    PL --> TG["technical grill<br/>open questions closed"]
    TG --> XC["cross-check<br/>story ↔ scenarios ↔ plans"]
    XC --> GR["green<br/>local gates"]
    GR --> RV["reviewer<br/>findings with source"]
    RV --> CL["close · retro · merge"]
  end

  CL --> NX["prepare next story · stop for the human"]
  CL -. retros .-> CO["coach · rule of two → skill change + eval"]

  bug([bug]) --> MT["maintainer · issue as spec → diagnose → red → fix → reviews → close"]
  MT -. escalates if behaviour, contract or design changes .-> FG
```

Each step carries a *why* in [docs/process.md](docs/process.md) — the general
reason behind it, never the anecdote that produced it, so it applies to
cases nobody has seen yet.

## Roles

| Skill | Role |
|---|---|
| `/sanchin:init` | Maps an existing project into the adapter (or scaffolds a new one), creates only what's missing, proposes gates. Re-run it as a doctor. |
| `/sanchin:product-owner` | What to build next and in what order; leaves a proposal draft. |
| `/sanchin:architect` | Whether a change fits the decisions in force; leaves a decision-record draft. |
| `/sanchin:developer` | Takes a chosen idea to merged code through the loop. |
| `/sanchin:maintainer` | Fixes a bug through the short lane, or escalates. |
| `/sanchin:reviewer` | Reviews against the project's standards and the story's spec, without repeating the gates or a generic review. |
| `/sanchin:coach` | Reads the retros, finds what keeps recurring, proposes process changes with their eval. |

None of them holds principles of its own: they read the project's mission
and vision, stack, constitution and glossary, wherever the adapter says
they are.

## Quickstart

```text
/plugin marketplace add rai22474/sanchin
/plugin install sanchin@sanchin
/sanchin:init
```

`init` looks at what the repository already has — stories, feature files,
plans, decision records, standards, git hooks, CI — and writes
`.claude/sanchin.yaml` with the project's own names and paths. In a new
repository it creates the minimum: base documents (grilled with you),
templates and indexes. Nothing is moved or renamed.

The adapter is the only project-specific file:

```yaml
version: 1
language: en
components: [app, api]
stories:   {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-11-01'}
scenarios: {globs: ['{component}/tests/features/**/*.feature']}
plans:     {directory: docs/plans, rules_since: '2026-11-01'}
gates:
  - {name: ruff, glob: '*.py', run: 'uv run ruff check {file}', level: edit}
```

Then check the project at any time — locally, in a git hook, or in CI:

```bash
scripts/sanchin check        # inside Claude Code: ${CLAUDE_PLUGIN_ROOT}/scripts/sanchin
```

To share the plugin with everyone working on the project, add it to the
project's `.claude/settings.json` (`extraKnownMarketplaces` and
`enabledPlugins`). See [docs/adopting.md](docs/adopting.md) for bringing it
into a repository that already has its own process.

## Decisions

| | Decision | Why |
|---|---|---|
| [0001](docs/decisions/0001-plugin-and-adapter.md) | A plugin for the process, one adapter per project | A copied template can't receive improvements; a pinned plugin can. |
| [0002](docs/decisions/0002-executable-scenarios.md) | Executable scenarios are the living spec | A spec the tests run can't silently become false. |
| [0003](docs/decisions/0003-immutable-incremental-stories.md) | Stories are immutable and incremental | History is added to, never rewritten. |
| [0004](docs/decisions/0004-story-core-optional-layers.md) | Story at the core; epics, narratives, milestones optional | Ceremony for small projects, discipline for large ones. |
| [0005](docs/decisions/0005-story-order.md) | Functional grill first, red once, cross-check before code | Each check where it is cheapest. |
| [0006](docs/decisions/0006-plans-worktrees-merge.md) | One plan per component, one worktree per story, local merge | A contract written twice diverges; shared working trees mix commits. |
| [0007](docs/decisions/0007-validator.md) | Built-in validator rules, configurable values | Same guarantees everywhere, no checker to rewrite. |
| [0008](docs/decisions/0008-deterministic-gates.md) | Gates at four levels; broken twice → a gate | A rule in a prompt is enforced only as well as the prompt is read. |
| [0009](docs/decisions/0009-progressive-context.md) | Progressive context: format, not layout | Adoption shouldn't be a migration. |
| [0010](docs/decisions/0010-doubt-markers.md) | Doubts are marked, and block the story | An agent asked to fill a gap invents something plausible. |
| [0011](docs/decisions/0011-constitution-checklist.md) | Plans answer the constitution as a checklist | Records that every rule was looked at. |
| [0012](docs/decisions/0012-two-reviews-measured.md) | Two reviews, measured by source | Whether the second earns its cost is a question for data. |
| [0013](docs/decisions/0013-bug-lane.md) | A short lane for bugs, with escalation | Most bugs don't need two grills; the ones that do are stories in disguise. |
| [0014](docs/decisions/0014-role-skills-without-principles.md) | Role skills without principles of their own | Copied principles go stale and argue against the project. |
| [0015](docs/decisions/0015-continuous-improvement.md) | Retro per story, rule of two, eval-driven skill changes | Skills drift like code unless tested like code. |
| [0016](docs/decisions/0016-general-whys.md) | Every rule carries a general why | Anecdotes are matched by shape; reasons generalize. |
| [0017](docs/decisions/0017-english.md) | sanchin in English, projects in their own language | Widest common language for the plugin; each team keeps its words. |

## How it compares

sanchin borrows from [Spec Kit](https://github.com/github/spec-kit) and
[OpenSpec](https://github.com/Fission-AI/OpenSpec), and parts ways where
experience on a real project pointed elsewhere.

| Idea | Spec Kit | OpenSpec | sanchin |
|---|---|---|---|
| Where the current spec lives | Spec documents | `openspec/specs/`, prose merged from deltas on archive | **Executable feature files**; no prose spec to keep true |
| Changing behaviour | New spec | Delta (ADDED / MODIFIED / REMOVED) merged into the spec | New immutable story with *supersedes* + scenario delta, checked against the feature files |
| Ambiguity | `[NEEDS CLARIFICATION]`, `/clarify` | `/opsx:explore` | Doubt markers, answered in a functional grill, **blocked by the validator** |
| Principles | Constitution + plan gates | Free-form `context` in `config.yaml` | Constitution checklist in every plan, exceptions tied to decisions; mission, vision, stack and glossary as separate documents |
| Consistency across artifacts | `/analyze` | `/opsx:verify` | Cross-check before code, and a spec review after it |
| Verification | Checklists | `validate` | Validator + four gate levels + scenarios red before green |
| Context for the agent | Templates | Project context | Progressive disclosure: indexes with *what* and *when*, checked |
| Improving the process | Extensions, presets | Schemas | Retro per story, rule of two, **eval-tested skills**, a coach |
| Bugs | Bug extension | — | Short lane with an escalation rule |

What sanchin deliberately does **not** take: a hand-maintained living spec
(the scenarios are it), an archive of change folders (stories and plans
already record each change), and a fixed folder layout (the adapter maps
whatever the project has).

## Docs

| Document | For |
|---|---|
| [process.md](docs/process.md) | The loop, the bug lane, pacing, git and approvals — what the skills follow. |
| [artifacts.md](docs/artifacts.md) | Base documents, stories, scenarios, plans, layers, issues — format and rules. |
| [adapter.md](docs/adapter.md) | Every field of `.claude/sanchin.yaml`. |
| [validator.md](docs/validator.md) | Validator commands, rules, hooks and CI. |
| [gates.md](docs/gates.md) | The four gate levels and how to declare a project's gates. |
| [context.md](docs/context.md) | Progressive disclosure: entry points, indexes, navigation. |
| [improvement.md](docs/improvement.md) | Retros, the rule of two, evals, the coach, releases. |
| [adopting.md](docs/adopting.md) | Bringing sanchin into an existing project. |
| [decisions/](docs/decisions/index.md) | sanchin's own decision records. |
| [templates/](templates/index.md) · [evals/](evals/README.md) | Starting points, and the skills' own tests. |

## License

[MIT](LICENSE)
