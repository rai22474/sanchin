# 0015 — Retro per story, rule of two, eval-driven skill changes

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
Each story ends with a short retro in its plan. A signal seen twice becomes
a change (a gate when checkable). Skill changes are made test-first against
`claude plugin eval` cases; every real correction becomes a regression case.
`/sanchin:coach` aggregates retros and proposes changes.

## Why
Corrections kept in an agent's private memory are invisible to other
sessions and never reach the process. Skills drift like code unless tested
like code.
