---
name: init
description: Sets a project up for sanchin, or checks an existing setup — detects the docs, stories, scenarios, plans, constitution and gates the project already has, maps them into .claude/sanchin.yaml, creates only what is missing, and reports what the validator finds. Use when adopting sanchin in a repository, when a sanchin skill finds no adapter, or after upgrading sanchin.
---

Read `${CLAUDE_PLUGIN_ROOT}/docs/adapter.md` and
`${CLAUDE_PLUGIN_ROOT}/docs/adopting.md` first.

## With no adapter yet

1. **Detect** what exists — never assume a layout: docs root and entry
   index, the navigation line pages use, stories (directory, file pattern,
   frontmatter keys and state values, criteria heading), feature files and
   their trace comments, plans and their headings, decision records,
   standards and design smells, mission/vision/stack/glossary, issues and
   proposals, layers in use (epics, narratives, milestones), components,
   and existing gates (git hooks, CI jobs, linter configs).
2. **Ask** only what the repository can't answer, as selectable options with
   a recommendation first.
3. **Write** `.claude/sanchin.yaml` with the project's own names and paths.
   If the write is refused, show the adapter in full in a YAML block so the
   user can save it — never only a summary of it.
   Map all five story states (`pending`, `ready`, `planned`, `in_progress`,
   `implemented`) to the project's words; a project with fewer states gets
   the missing ones proposed in its language, as options. With milestones in
   use, turn the `milestone` layer on and fill `roadmap:` (directory, state
   line, state values); with feature files, set `scenarios.pending_tag` to
   the tag the runner already skips, or propose `@pending` and the runner
   change that skips it.
   Set `rules_since` to today; list plans of in-progress stories that predate
   the rules in `plans.legacy`, and in `stories.legacy` both implemented
   stories with no date and stories already in flight.
4. **Write the wrapper** `scripts/sanchin`, a copy of
   `${CLAUDE_PLUGIN_ROOT}/templates/sanchin`, executable. It is how the
   user, git hooks and scripts run sanchin from the project. If
   `scripts/sanchin` already exists and isn't this wrapper, ask for another
   path and use it everywhere below.
5. **Create only what is missing**, after confirmation: a base document
   (grill its content with the user — mission, vision, stack, glossary), a
   minimal constitution, templates (from `${CLAUDE_PLUGIN_ROOT}/templates/`,
   translated to the project's language and terms), missing indexes. Never
   move or rename existing files.
6. **Gates**: list the ones found and propose the ones the stack is missing,
   each with its level ([gates.md](${CLAUDE_PLUGIN_ROOT}/docs/gates.md)).
   Install nothing without confirmation. Offer to replace per-tool edit
   hooks with the adapter's `gates:` list, and to write the `pre-commit`
   and `pre-push` git hooks as one line each calling
   `scripts/sanchin git-hook <level>` (or a step in
   the project's hook manager, if it has one); never overwrite an existing
   hook — add the line to it. The hook runs the gates only
   once the user approves them: tell the user to run `/sanchin:trust`
   (or `scripts/sanchin trust` in a shell) themselves — never run it for
   them ([gates.md](${CLAUDE_PLUGIN_ROOT}/docs/gates.md#trust)).
7. **Run** `scripts/sanchin check` and report.

## With an adapter (doctor)

Run the validator; compare the adapter against the current adapter format
(new or renamed fields after a sanchin upgrade, see the changelog); check
that every path it names still exists; that `scripts/sanchin` is the
current `${CLAUDE_PLUGIN_ROOT}/templates/sanchin` (offer to update it
otherwise); and that the git hooks call it rather than a plugin path, which
moves on every upgrade. Report what to change, as options.
