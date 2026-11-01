# 0005 — Functional grill first, red once, cross-check before code

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
Per story: functional grill → scenarios red → one plan per component →
technical grill → cross-check of story, scenarios, plans and decision
records → green → reviews → close, retro, merge → prepare the next story
and stop.

## Why
- Scenarios written before the "what" is settled get rewritten, and the red
  run repeats; after the grill it runs once.
- The two grills stay apart: behaviour with the user, design with the code.
- An inconsistency between spec artifacts is cheapest before code depends
  on it.
- The stop before the next functional grill keeps a human deciding the "what".

## Revision — 2026-11-01: split across roles

The order holds, split across the roles of [0019](0019-roles-per-cycle.md):
the product owner closes the "what" and writes the scenarios, tagged
`@pending`, without running them; the tech-lead writes and grills the plans
and runs the cross-check; the developer makes the scenarios red, then green,
reviews, closes and merges. Delivery no longer drafts the next story: the
roadmap says what comes next. *Why:* the scenarios are the executable form
of the "what", so they belong with it; running them red needs the steps,
which are delivery's.
