# 2. Planning cycle

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

`/sanchin:tech-lead`, on a ready story.

## 2.1 Plans

One plan per component the story touches (components come from the
adapter), from the plan template: the technical "how" — current state of
the code it touches, target design, constitution checklist, risks, ordered
steps. The story links its plans.

- **The contract between components** (endpoint, payload, ids) is written
  once, in the plan of the component that provides it; the consumer's plan
  links it. *Why:* a contract written twice diverges.
- **Constitution checklist.** The plan answers every rule of the project's
  constitution that applies to it: `n/a`, `ok`, or `exception → D-n`,
  where `D-n` is the plan decision that justifies it. *Why:* a free-text
  "layers and ADRs" section records only the rules the author thought of;
  a checklist records that every rule was looked at.
- Where a design choice has more than one reasonable answer, write it as an
  open question with a recommendation instead of silently picking one.
- A plan is the record of one change: it is never updated after its story
  is implemented. *Why:* the current state is the code and its tests; a
  plan kept "up to date" becomes a second, drifting description.
- **Size it against the increment.** If the plans' steps don't fit one
  short increment (`stories.increment`), the story isn't *time-bound*: it
  goes back to the product owner to be split, with the split the plans
  suggest. *Why:* only the "how" shows a story's real size, and a story
  that outgrows its increment loses every benefit of being small.
- A design that contradicts a decision record in force, or needs a new
  one, stops here and goes to `/sanchin:architect`. *Why:* a story plan is
  the wrong place to change the architecture — its scope is one story.

## 2.2 Technical grill

Grill the plans, technical side only. Research first — a fact found in the
code routinely resolves what looked like a judgement call. With several
plans, grill them together: the cross-component contract must be closed
before any of them is implemented. Answers go to each plan's decisions
section; the open-questions section ends empty. A functional question that
shows up goes back to the product owner (see [States](states.md#states)).

## 2.3 Cross-check

Dispatch one read-only sub-agent with the story, its feature files, all its
plans and the decisions they cite, briefed with the reviewer's spec brief
minus the code: criteria with no scenario, scenarios that would pass on
today's code (above all negative ones whose subject doesn't exist yet),
superseded criteria whose scenarios still assert the old behaviour, an
implemented scenario that contradicts the story and isn't in its delta,
contract mismatches between
plans, plan decisions that contradict a decision record in force. Findings
go back to the plan, or to the story through the product owner. *Why:* an
inconsistency between spec artifacts is cheapest to fix before code
depends on it.

Write the planning retro in the plan's **Retro** section (*Planning*), set
the story **planned**, and stop: it is ready for `/sanchin:developer`.
