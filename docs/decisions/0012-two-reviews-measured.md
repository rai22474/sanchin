# 0012 — Two reviews, measured

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
`/mattpocock-skills:code-review` runs first as the generic review and
`/sanchin:reviewer` reports only what it missed: the project's standards,
whole modules, and the story's spec. Every finding carries its source label.
After a few stories the coach counts unique findings per source and the
pair is kept or cut on that data.

## Why
Two reviews cost twice; whether the second earns its cost is a question for
data, not taste.
