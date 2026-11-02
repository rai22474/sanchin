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

## Grills

- **Every grill starts with the Skill tool — `mattpocock-skills:grilling`
  — before its first question**: the product owner's at each level, the
  tech-lead's technical grill, the architect's. It is not optional, and
  asking good questions without it is not running it. *Why:* the skill
  holds the method — the design tree, the frontier asked whole in each
  round and recomputed after every answer, facts looked up by sub-agents
  instead of asked, and the end only when the frontier is empty and the
  user confirms the shared understanding. A grill run from memory keeps the
  questions and drops the parts that catch what nobody thought to ask.
- **Format:** each round's questions go to the user as selectable options
  (below, *Pacing*), the recommended answer first — that is the skill's
  "recommended answer", in this process's format. The rest of the method is
  the skill's.
- If the skill isn't available, stop and tell the user the dependency
  (`mattpocock-skills`) is missing. Don't grill without it.

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
  another model, it says so in one line — naming `/model <model>` — and
  goes on; the user interrupts to switch. It doesn't ask: the answer was
  the same every time, and a stop that always gets it costs a round trip. *Why:* deciding roles (product owner, tech lead,
  architect) pay for judgement; delivery follows a closed plan, and its
  output is most of a story's cost.

## Long and costly runs

- Ask before entering a fix cycle around a costly suite (containers, paid
  model calls): the first run for a story, or the first after an unrelated
  failure. Re-running inside that cycle doesn't need asking again. With
  `approvals.costly_runs: auto` ([approvals](#approvals)), say in one line
  what runs and run it.
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
  to `main` as each cycle ends, with the user's approval
  ([approvals](#approvals)). *Why:* they change
  no behaviour — `@pending` keeps the build green — and every role and
  session reads `main`.
- `main` is kept green: the local gates run before a merge, and a red `main`
  is fixed before anything else is merged.
- Commit with an explicit pathspec on `git commit` itself, and check
  `git show --stat HEAD` afterwards. *Why:* other sessions may have staged
  their own changes; a plain commit takes the whole index.

## Approvals

The adapter's `approvals` let the user approve, once and in writing, the
steps that otherwise stop a cycle to ask
([adapter.md](../adapter.md#fields)). Each is `ask` (the default) or `auto`:

| Action | With `auto`, done without asking |
|---|---|
| `commit` | the commits the process prescribes: a cycle's artifacts and state changes on `main`, and the story's commits on its branch — each with an explicit pathspec |
| `costly_runs` | the first run of a costly suite in a story's fix cycle |
| `merge` | integrating a closed story the way `merge` says — merge, push, check CI, remove the worktree; or push the branch and open the pull request — only with every local gate green |

With `auto`, say in one line what you are doing and do it; anything that
doesn't fit the row — a commit outside the process, a push without green
gates, a force push — is still asked. *Why:* in a delivery cycle the plan
is closed and these answers never changed; the stops cost round trips and
attention, and the user who wants them keeps `ask`.

**Approvals are the user's to set, never Claude's.** Don't edit the
`approvals` section, by any tool, nor suggest that you do; when one would
help, name the line for the user to write. A hook denies Claude's edits to
it. *Why:* an agent that could write its own approvals has none.

## Non-negotiable boundaries

- Ask before committing, merging into `main` and pushing, except as the
  adapter's `approvals` allow ([approvals](#approvals)). Always ask before
  touching live deploy configuration.
- After pushing, check the actual CI result — a push that returned 0 is not
  a green pipeline.
- A sub-agent's report is not user approval for anything.
