---
name: maintainer
description: Fixes a known bug through the short lane — the issue is the spec, diagnose first, regression scenario red, fix, both reviews, close — and escalates to the full loop when the fix changes user-visible behaviour, a contract between components, or needs a design decision. In a project set up for sanchin (one with .claude/sanchin.yaml), use when asked to fix a bug, an issue, a failing behaviour or a regression.
---

1. Read the project's adapter, `.claude/sanchin.yaml` (no adapter: stop and
   offer `/sanchin:init`), and the bug lane in
   `${CLAUDE_PLUGIN_ROOT}/docs/process.md#bug-lane`, together with its
   sections on pacing, costly runs, git and boundaries.
2. Find or create the issue where the adapter keeps issues
   (`base_docs.issues`), following an existing issue's structure.
3. Follow the lane in order. Write the root cause in the issue before
   touching code; the diagnosis is the spec of the fix.
4. Before fixing, check the escalation rule. If it applies, say so and hand
   over to `/sanchin:developer` with the issue as the starting point.
5. Close with the retro in the issue (`${CLAUDE_PLUGIN_ROOT}/docs/improvement.md`).
