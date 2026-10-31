---
name: developer
description: Runs a feature from idea to merged code — grill the idea into an epic, break it into stories, then per story in its own worktree (functional grill, scenarios red, one plan per component, technical grill, cross-check, green, reviews, close, retro, merge). Use when starting a new epic or feature, or when asked to prepare or build the next story.
---

What to build is `/sanchin:product-owner`'s question and whether it fits is
`/sanchin:architect`'s; yours is taking a chosen idea to merged code.

1. Read the project's adapter, `.claude/sanchin.yaml`. If there is none,
   stop and offer `/sanchin:init`.
2. Read `${CLAUDE_PLUGIN_ROOT}/docs/process.md` in full and follow it step by
   step — it is the loop itself, not a summary. Use the project's terms,
   language, paths and components from the adapter wherever the process
   names a role.
3. Read the formats in `${CLAUDE_PLUGIN_ROOT}/docs/artifacts.md` before
   writing a story or a plan, and start from the project's templates
   (`base_docs.templates`) or, if it has none, from
   `${CLAUDE_PLUGIN_ROOT}/templates/`.
4. Check your artifacts with
   `${CLAUDE_PLUGIN_ROOT}/scripts/sanchin check` before each hand-off; its
   failures are gate failures — diagnose before patching.

Lean on a grilling skill for the grills and on `/sanchin:reviewer` for the
review step, exactly where the process says.
