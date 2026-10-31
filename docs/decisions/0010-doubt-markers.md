# 0010 — Doubts are marked, and block the story

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
A draft story marks what isn't clear with a doubt marker. The functional
grill starts from them; the validator refuses a story leaving `pending`
with one left.

## Why
An agent asked to fill a gap invents something plausible. A marker turns
each gap into a question the grill must answer. (Spec Kit's
`[NEEDS CLARIFICATION]` is the same idea.)
