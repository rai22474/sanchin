---
name: maintainer
description: Fixes a known bug through the short lane — the issue is the spec, diagnose first, regression scenario red, fix, both reviews, close — and escalates to the product owner, as a story, when the fix changes user-visible behaviour, a contract between components, or needs a design decision. In a project set up for sanchin (one with .claude/sanchin.yaml), use when asked to fix a bug, an issue, a failing behaviour or a regression.
---

1. Read the project's adapter, `.claude/sanchin.yaml` (no adapter: stop and
   offer `/sanchin:init`). Then read only these:
   `${CLAUDE_PLUGIN_ROOT}/docs/process/bug-lane.md`, `process/working-rules.md`,
   and `${CLAUDE_PLUGIN_ROOT}/docs/artifacts/issue.md`.

   **Model.** If the adapter's `models.maintainer` names a model other than the
   one you run on, say so in one line — naming
   `/model <that model>` — and go on; don't ask. Every sub-agent you
   dispatch gets `model: <models.maintainer>` unless it is `inherit` or unset
   ([working-rules.md](${CLAUDE_PLUGIN_ROOT}/docs/process/working-rules.md#models)).

2. Find or create the issue where the adapter keeps issues
   (`base_docs.issues`), following an existing issue's structure.
3. Follow the lane in order. Write the root cause in the issue before
   touching code; the diagnosis is the spec of the fix.
4. Before fixing, check the escalation rule. If it applies, say so, write
   a pending story linking the issue (no fix, no design), and hand it to
   `/sanchin:product-owner`: the story goes through the cycles. Don't
   offer to do part of it in this lane: a smaller slice that still changes
   what the user sees is still a story. *Why:* the slice skips the same
   grills the escalation exists to keep. A part that changes nothing the
   user sees (a data-loss guard, say) may stay here — name it as such.
5. Close with the retro in the issue (`${CLAUDE_PLUGIN_ROOT}/docs/improvement.md`).
