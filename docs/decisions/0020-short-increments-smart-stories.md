# 0020 — Short increments, SMART stories

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-11-01)

## Decision
A story is the smallest change that gives the user something they can see
working, and it goes from ready to merged in one short increment, whose
length the project sets in its adapter (`stories.increment`). Every story
is SMART before it goes ready — specific, measurable, achievable, relevant,
time-bound — each letter with a concrete test
([process.md](../process.md#13-stories-from-a-narrative)). The product
owner checks all five while grilling; the tech-lead re-checks *achievable*
and *time-bound* against the plans, and sends back a story that doesn't fit.
A story too big is split into stories that each still work on their own,
never into technical layers.

## Alternatives considered
- **No size rule**: stories grow to whatever a feature needs; review,
  scenarios and context all degrade with the size of the change.
- **Story points or estimates**: a number to argue about, not a test; the
  increment is a single limit each story either fits or doesn't.
- **INVEST**: overlaps with SMART on independent, small and testable; SMART
  adds *relevant* (traced to the mission) and an explicit time limit, and
  the process's own rules already cover negotiable and valuable.
- **A validator rule**: size and specificity aren't checkable from the
  text; the parts that are (measurable: every criterion cited by a
  scenario; achievable: no doubt marker left) already are.

## Why
With an agent, writing the code stops being the bottleneck; verifying it is
what's left — the tests, the review, the user seeing it work. An agent's
mistakes are plausible and compound: the code compiles, its own tests pass,
and each step builds on the last, so an early misunderstanding is carried
through everything after it. Short increments match what the agent
generates to what can be verified: a red-then-green scenario that pins one
behaviour is the agent's own feedback, the user seeing it work within days
is the feedback the agent doesn't have, and the whole story fits one
session's context instead of being rebuilt from summaries. The same small
change is also where the grills reach every case and the review reads every
module whole. SMART turns "small and clear" into five tests a role can
answer yes or no.
