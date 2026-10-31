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
