# Working rules

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

## Pacing

- Inside a cycle the user started, when a step finishes cleanly and the
  cycle defines the next one, proceed — don't ask "what next?". Stop at the
  cycle's end, at a decision only the user can make, and for the approvals
  below. *Why:* starting the cycle already gave the direction; ending it
  hands the next decision back.
- Put every judgement call to the user as selectable options, the
  recommended one first, each with its trade-off; never a prose list, and
  never only the recommendation. *Why:* the user picks faster than they
  type, and needs the alternatives to judge the recommendation.

## One session per cycle

- Start each cycle — refinement, planning, delivery, architecture — in a
  fresh session (`/clear`, or a new one). *Why:* the roles hand over through
  artifacts on `main`, not through the chat; a session that carries the
  earlier cycles re-reads all of them on every call, paying for context the
  next role doesn't use and letting a decision made in chat stand in for
  one that should be in the artifact.
- The plugin's prompt hook enforces it: invoking a role's skill in a
  session where another role's skill already ran is blocked with a reminder
  to `/clear` (the reviewer, `/sanchin:init` and `/sanchin:trust` are not
  cycles and pass). The adapter's `session.fresh_per_cycle` turns it to a
  warning (`warn`) or off (`off`).

## Models

- The adapter's `models` names a model per role (`product_owner`,
  `tech_lead`, `developer`, `architect`, `maintainer`, `reviewer`, `coach`):
  `opus`, `sonnet`, `haiku`, `fable` or `inherit` (the default: the
  session's model).
- **Sub-agents** a role dispatches run on that role's model; the reviewer's
  on `models.reviewer`.
- **The session itself** can't be switched by a skill for longer than a
  turn, and a cycle lasts many. So the role checks it when it starts: on
  another model, it says so and asks whether to go on or stop for
  `/model <model>`. *Why:* deciding roles (product owner, tech lead,
  architect) pay for judgement; delivery follows a closed plan, and its
  output is most of a story's cost.

## Long and costly runs

- Ask before entering a fix cycle around a costly suite (containers, paid
  model calls): the first run for a story, or the first after an unrelated
  failure. Re-running inside that cycle doesn't need asking again.
- Run targeted scenarios first; the full suite only once the design is
  closed, and never while known failing issues are still open.
- When a full run is the gate, stop at the first failure and diagnose;
  discard the partial summary of a killed run. *Why:* a red suite already
  fails the gate; the rest adds cost and no decision.
- Launch anything over about an hour detached and watch its log. *Why:*
  background-task limits are shorter than long runs, and a kill skips
  cleanup traps.

## Git: close to trunk-based

`main` is the trunk, and everything reaches it soon. A story's branch and
worktree stand in for a developer's own machine: they isolate one agent's
work from another's, not one release from another. They live as long as
the story — one short increment — and are merged into `main` and removed
when it closes. *Why:* a branch that lives longer than a story drifts from
`main`, and its merge becomes a project of its own; small stories merged
often keep every agent working on the code as it is.

- Product and planning artifacts (stories, scenarios tagged `@pending`,
  plans, milestones, decision records) and story state changes go straight
  to `main` as each cycle ends, with the user's approval. *Why:* they change
  no behaviour — `@pending` keeps the build green — and every role and
  session reads `main`.
- `main` is kept green: the local gates run before a merge, and a red `main`
  is fixed before anything else is merged.
- Commit with an explicit pathspec on `git commit` itself, and check
  `git show --stat HEAD` afterwards. *Why:* other sessions may have staged
  their own changes; a plain commit takes the whole index.

## Non-negotiable boundaries

- Ask before committing, merging into `main`, pushing, and touching live
  deploy configuration.
- After pushing, check the actual CI result — a push that returned 0 is not
  a green pipeline.
- A sub-agent's report is not user approval for anything.
