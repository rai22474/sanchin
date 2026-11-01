# 1. Product cycle

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

`/sanchin:product-owner`, from the mission down. Each level is grilled
with the user — a grill that starts by invoking
`mattpocock-skills:grilling` ([working-rules.md](working-rules.md#grills))
— before the next is written from it. Dispatch research sub-agents for anything the repository can
answer, in parallel with asking the user the genuine judgement calls.
*Why:* the user's attention is the scarcest input; a question a search can
answer wastes it.

The order is fixed; a level whose layer is off in the adapter
([adapter.md](../adapter.md#layers)) is skipped — without narratives, an epic
breaks straight into stories. *Why:* small projects shouldn't carry
ceremony they don't need, but no project should write a story before
knowing which capability it serves.

Start every artifact from its template (the project's, or
[templates/](../../templates)) and read one real example of the same kind
first: the template gives the shape, the example the tone. Wire every new
document into its index ([context.md](../context.md)).

## 1.1 Epics from the mission

Grill the mission and vision into the capabilities the user needs: one
epic per capability, saying why the user needs it. Quote the principle of
the vision each one serves.

## 1.2 Narratives from an epic

Grill the epic into narratives: vertical slices ordered from less to more
functionality, each one complete and testable on its own. *Why:* a slice
that can't ship alone can't be verified alone either.

## 1.3 Stories from a narrative

Grill the narrative into stories — behaviour only: what the user sees,
edge cases, what counts as done; never the "how".

**Short increments.** A story is the smallest change that gives the user
something they can see working, and it goes from ready to merged in one
short increment — the length the project sets in its adapter
(`stories.increment`, e.g. `2 days`). A story that doesn't fit is split
into stories that each still work on their own, never into technical
layers. *Why:*

- **The agent writes faster than anyone can check.** With an agent,
  writing the code stops being the bottleneck; verifying it — the tests,
  the review, the user seeing it work — is what's left. An agent's mistakes
  are plausible and compound: the code compiles, the tests it wrote pass,
  and each step builds on the last, so a misunderstanding early is carried
  through everything after it. A short increment bounds how much gets built
  on a wrong turn before a red scenario or the user's eyes catch it.
- **Red and green are the agent's own feedback.** A scenario that fails for
  the right reason, then passes, tells the agent it is on track without
  asking anyone — but only when it pins one behaviour. With many at once,
  the agent "fixes" what fails by touching what shouldn't change.
- **The user's feedback is the check the agent doesn't have.** The agent
  knows whether the code meets what was written, not whether it is what was
  wanted. Seeing the behaviour work days after asking for it, not weeks,
  corrects the "what" before more is built on top of it.
- **It fits one agent's context.** A story whose story, plans, code and
  tests fit in one session is built from what was decided; a larger one is
  built from summaries of it, and the agent fills the gaps by inventing.
- **Every check works better on a small change.** The grills cover every
  case, the review reads every module the change grows in full, and the
  cross-check holds the whole story in mind. A large change is skimmed, and
  skimmed is where defects pass.
- **Less is in flight at once.** Fewer half-done branches, fewer merge
  conflicts, less work lost when priorities change — and a failure points
  at a handful of lines.
- **The roadmap tells the truth.** A milestone made of small stories shows
  its progress story by story; one made of large ones reads "in progress"
  until the end.

**SMART.** Every story is checked against SMART while it is grilled, and
the product owner doesn't set it ready until each letter holds:

| | The story is… | The test | If not |
|---|---|---|---|
| **S** | **Specific** | One behaviour, for one kind of user. Each criterion names an observable outcome — what the user sees or gets — not an intention ("better", "easier", "supports"). | Split it; rewrite vague criteria as outcomes. |
| **M** | **Measurable** | Each criterion can be checked as pass or fail by a scenario, or says why not (`(no scenario: …)`). "Done" is the scenarios passing — nothing left to opinion. | Rewrite the criterion until a scenario can decide it. |
| **A** | **Achievable** | Buildable with what exists and the decisions in force; no doubt marker left; no dependency on a story that isn't done or planned before it. | Mark the doubt; order the dependency first in the roadmap; a needed architecture change goes to the architect. |
| **R** | **Relevant** | Its *so that* names a value the user gets, and it serves its narrative — and through it, its epic and the mission. | Drop it, or find the narrative it really serves. |
| **T** | **Time-bound** | Fits one short increment (`stories.increment`) from ready to merged. | Split it into stories that each still work on their own. |

The tech-lead checks **A** and **T** again with the code in view: a plan
whose steps don't fit the increment, or that can't be built under the
decisions in force, goes back — to the product owner to split the story, or
to the architect. *Why:* the product owner sizes a story from the "what";
only the "how" shows its real size.

- **A story states only the "what"**: who wants what, and a numbered list
  of acceptance criteria. *Why:* a spec that describes code goes stale with
  the next refactor; the current state of the code goes in the plan.
- **Doubts are marked, not guessed.** Anything not yet clear is a doubt
  marker (`[DOUBT: …]` by default) where it belongs; the grill resolves
  each one in the story. *Why:* an agent that guesses fills gaps with
  plausible inventions; a marker turns each gap into a question.
- **Stories are immutable once implemented, and changes are incremental.**
  A story that changes behaviour an implemented story describes says so
  with a *supersedes* line naming the criterion and linking the earlier
  story, and lists its **scenario delta**: the scenarios it adds (+),
  changes (~) and removes (−). The earlier story is never edited.
  *Why:* an implemented story is the record of what was asked then; the
  current behaviour lives in the executable scenarios, never in prose that
  can drift.
- **Derived states are generated, never written by hand** (narrative and
  epic states, milestone tables). *Why:* a derived state written by hand
  drifts from what it is derived from.

## 1.4 Scenarios

Write the acceptance scenarios of the closed story — the executable form
of its criteria — in the feature files, organized by capability, not by
story. *Why:* they are the living spec, the place to read how the system
behaves today; a story is the record of one change to it.

- Every scenario carries a trace comment naming the criteria it covers
  (`# ST-12: AC 1, 3` by default), and the story lists its feature files.
  A criterion no scenario can check says why
  (`(no scenario: …)`).
- New scenarios are tagged **`@pending`**: they go to `main` long before
  the code, and the runner skips them until the developer makes them pass.
  *Why:* a spec merged ahead of its code must not turn the build red.
- Write the delta's added (+) scenarios now; its changes (~) and removals
  (−) touch scenarios that pass today, so the developer applies them in
  delivery.
- **Each scenario fails on today's code.** Before writing one down, know
  why it is red now; a negative one ("no section X", "as many commits as
  before") first establishes that its subject exists — a step that creates
  it, or one that asserts it is there. *Why:* a negative outcome passes
  empty when its precondition doesn't exist yet, and a scenario that passes
  before the story can't tell before from after; caught at delivery's red
  run, it is already on `main` and comes back to you.
- A scenario the delta adds (+) or changes (~) carries this story's trace —
  a changed scenario now asserts this story's criterion.
- Don't run them: they are red by construction until delivery writes their
  steps. Check they parse — the validator does.

## 1.5 Roadmap

The roadmap is a set of **milestones**, each with an objective in prose and
the stories that deliver it ([artifacts/layers-and-roadmap.md](../artifacts/layers-and-roadmap.md#roadmap)). Place
the story in a milestone (`milestone:` in its frontmatter), regenerate the
derived files — the milestone tables (`sanchin roadmap --write`), and
whatever the project's own commands in the adapter's `generate` list
produce — and set the story **ready**. A project that generates its roadmap
with its own script keeps the milestone layer off and lists the script in
`generate`.
A milestone's state — planned, in progress, closed — is the product
owner's call; only one is in progress at a time, and it closes when all its
stories are implemented. Technical stories from the architect enter the
roadmap the same way. Write the story's **Retro** section — what the
refinement taught. *Why:* one roadmap is one queue: functional and
technical work compete for the same time, and the order is decided in one
place.

Stop: the story is ready for `/sanchin:tech-lead`.
