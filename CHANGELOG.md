# Changelog

[README](README.md)

All notable changes to sanchin. Versions follow [semantic versioning](https://semver.org);
a change to the adapter format is a major version.

## 0.1.2 — 2026-11-01

Approving the gates no longer needs a path the user can't find.

- `/sanchin:trust`: shows the adapter's gates, asks for an explicit
  confirmation and records the approval. Only the user can invoke it
  (`disable-model-invocation`); the agent still never approves gates.
- `scripts/sanchin` in the project: `/sanchin:init` writes a thin wrapper
  (`templates/sanchin`) that finds the installed plugin — `$SANCHIN`,
  `$CLAUDE_PLUGIN_ROOT`, Claude Code's plugin registry, then the cache — so
  the README's commands work from a project, and git hooks get a path that
  survives upgrades.
- The edit hook's "not trusted" message points to `/sanchin:trust`.

## 0.1.1 — 2026-11-01

- `generate` in the adapter: the project's own commands that regenerate
  derived files, run by the roles at every hand-off — for a project whose
  roadmap is built by its own script.
- `stories.legacy` also takes stories already in flight when a project
  adopts sanchin: they need no scenarios, like their plans in `plans.legacy`.
- The immutability rule applies only to stories closed under the rules
  (dated on or after `rules_since`, not legacy): adopting a project edits
  the metadata of older stories, and the rule flagged every one of them.
- CI on GitHub Actions: the validator's unit tests and `sanchin check` on
  sanchin's own docs, on every push to `main` and every pull request.

## 0.1.0 — 2026-11-01

First version, extracted from the process of a real multi-service project.

- Seven role skills: `init`, `product-owner`, `architect`, `developer`,
  `maintainer`, `reviewer`, `coach`.
- The process ([docs/process.md](docs/process/index.md)): story loop, bug lane,
  pacing, costly runs, git and approvals.
- Adapter format version 1 ([docs/adapter.md](docs/adapter.md)).
- Validator: doc references, links, navigation and indexes; story
  frontmatter, doubt markers, criteria traceability, supersedes and the
  generated superseded-by table, scenario delta; plan sections by state,
  open questions, constitution checklist, legacy plans.
- PostToolUse hook: doc rules on edited docs and the adapter's edit-level gates.
- Templates for story, plan, issue, epic, narrative and a minimal adapter.
- Eval cases for the critical skill rules.
- Plugin dependency on `mattpocock-skills` for the grills and the generic review.
- Twenty-one decision records.

### Changed before release: four cycles, one role each

- The process is four cycles ([0019](docs/decisions/0019-roles-per-cycle.md)):
  **product** (`product-owner`: mission → epics → narratives → stories,
  scenarios tagged `@pending`, roadmap), **planning** (new `tech-lead`:
  plans, technical grill, cross-check), **delivery** (`developer`: red,
  green, reviews, close, merge) and **architecture** (`architect`: technical
  idea → decision record → technical stories). Each role stops at its
  hand-off.
- Stories have five states — pending, ready, planned, in progress,
  implemented — and the validator checks what each requires.
- Scenarios written ahead of their code carry `@pending` (configurable);
  the validator checks the tag against the stories' states.
- The roadmap is the milestone layer: stories name their milestone, and
  `sanchin roadmap [--write]` generates and checks each milestone's stories
  table and state.
- Escalated bugs go to the product owner as pending stories.
- Stories are short increments and SMART ([0020](docs/decisions/0020-short-increments-smart-stories.md)):
  each letter has a test, the product owner checks all five before ready,
  the tech-lead re-checks achievable and time-bound against the plans;
  `stories.increment` sets the increment's length.
- The wiki is the project's memory ([0021](docs/decisions/0021-wiki-as-memory.md)):
  every decision is written in the repository's docs by the role that took
  it; progressive disclosure is how an agent finds the right part.
- The process and the formats are directories — `docs/process/` (an index,
  one document per cycle, states, bug lane, working rules) and
  `docs/artifacts/` (one per format) — and each role skill reads only its
  own; the 4,200-word `process.md` is gone.
- Git is close to trunk-based: story branches stand in for a developer's
  machine, live one increment, and merge into `main`; product and planning
  artifacts go straight to `main`.
- The README opens with "specs that don't rot", citing
  [Agarwal et al., 2026](https://arxiv.org/abs/2608.25202).

### Fixed before release

- An implemented story without a `date` no longer slips past every rule
  (old ones go in the new `stories.legacy`); duplicated story ids are
  reported.
- The hook checks the git working tree that holds the edited file, so it
  works in a story's worktree (inside or outside the repository) with that
  worktree's adapter.
- The hook runs a repository's gates only after the user approves that
  exact list with `sanchin trust`; an unknown or changed list is skipped
  with a message to the user.
- A plan's constitution checklist answers the global rules plus its own
  component's (`{component}` in `constitution.globs`), not every component's.
- The validator fails an implemented story, or its plans, edited after the
  commit that closed it (it was a review-only rule).
- `sanchin git-hook pre-commit|pre-push`: the body of a git hook, working
  out the staged or pushed files itself; `init` offers to write the hooks.
- Role skills take over only in a project with an adapter; the README
  recommends enabling the plugin per project.
- `merge: local | pr` in the adapter: a team with a protected `main` closes
  a story with a pull request instead of a local merge (revision of 0006).
- A story goes in progress only after the technical grill closes its
  plans' open questions, so the validator no longer fails mid-loop.
- Frontmatter accepts ` # comments` (as the examples in the docs use).
- A trace comment counts only when it sits above a scenario.
- Feature files are read with the official Gherkin parser
  (`gherkin-official`, pinned): every Gherkin language and `Rule:` blocks
  work, and a feature file that doesn't parse is an error.
- A gate without `{file}` runs once for all files, not once per file;
  gates take a `timeout` and a timed-out gate fails instead of crashing.
- The hook exits before starting Python in a project without an adapter,
  and reports an invalid adapter instead of turning the gates off silently.
- `file.ext:NNN` references match whole path segments (`a.py` no longer
  matches `data.py`).
- The `developer-without-adapter-offers-init` eval has its `case.yaml`.
- Eval cases for the maintainer (escalation), the reviewer (skips what
  gates enforce, labels sources) and the coach (rule of two).
- `evals/run.sh` runs the suite on a copy without the plugin dependency:
  the eval sandbox can't resolve it, and sanchin silently didn't load, so
  every case had measured Claude without the plugin.
- `init` shows the full adapter when it can't write it; its eval judges
  the adapter written or shown (the eval sandbox refuses writes to
  `.claude/`).
- The README says the official marketplace must be added for the
  dependency — without it sanchin installs but doesn't load.
