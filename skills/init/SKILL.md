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
   Set `rules_since` to today; list plans of in-progress stories that predate
   the rules in `plans.legacy`.
4. **Create only what is missing**, after confirmation: a base document
   (grill its content with the user — mission, vision, stack, glossary), a
   minimal constitution, templates (from `${CLAUDE_PLUGIN_ROOT}/templates/`,
   translated to the project's language and terms), missing indexes. Never
   move or rename existing files.
5. **Gates**: list the ones found and propose the ones the stack is missing,
   each with its level ([gates.md](${CLAUDE_PLUGIN_ROOT}/docs/gates.md)).
   Install nothing without confirmation. Offer to replace per-tool edit
   hooks with the adapter's `gates:` list.
6. **Run** `${CLAUDE_PLUGIN_ROOT}/scripts/sanchin check` and report.

## With an adapter (doctor)

Run the validator; compare the adapter against the current adapter format
(new or renamed fields after a sanchin upgrade, see the changelog); check
that every path it names still exists; report what to change, as options.
