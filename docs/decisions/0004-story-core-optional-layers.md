# 0004 — The story is the core; epics, narratives and milestones are layers

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
Every project has stories with numbered criteria. Epics, narratives and
milestones are optional layers turned on in the adapter; when on, their
rules apply (narratives as vertical slices from less to more
functionality, derived states generated).

## Why
Three levels of planning are ceremony for a small project and discipline
for a large one. The rules worth keeping — vertical slices, derived states
— apply whenever the layers do.

## Revision — 2026-11-01: a fixed order, and the roadmap

The product owner walks the layers in a fixed order — mission → epics →
narratives → stories — skipping the ones that are off. The milestone layer
is the roadmap: each story names its milestone, and sanchin's validator
generates and checks the milestone tables. *Why:* no story should be
written before knowing which capability it serves, and the roadmap is where
every story's order is decided ([0019](0019-roles-per-cycle.md)).
