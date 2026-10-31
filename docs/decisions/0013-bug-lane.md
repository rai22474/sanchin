# 0013 — A short lane for bugs

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
`/sanchin:maintainer`: the issue is the spec; diagnose first; regression
scenario red; fix; both reviews; close with what resolved it. A fix that
changes user-visible behaviour, a cross-component contract, or needs a
design decision escalates to the full loop.

## Why
Most bugs don't need two grills and a plan; the ones that do are stories in
disguise, and the escalation rule catches them.
