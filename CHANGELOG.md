# Changelog

[README](README.md)

All notable changes to sanchin. Versions follow [semantic versioning](https://semver.org);
a change to the adapter format is a major version.

## 0.1.0 — unreleased

First version, extracted from the process of a real multi-service project.

- Seven role skills: `init`, `product-owner`, `architect`, `developer`,
  `maintainer`, `reviewer`, `coach`.
- The process ([docs/process.md](docs/process.md)): story loop, bug lane,
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
- Eighteen decision records.

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
