# 0002 — Executable scenarios are the living spec

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Context
Spec-driven tools keep the spec as prose (WHEN/THEN in markdown) and merge
changes into it by hand. Nothing checks the prose against the system, so it
drifts.

## Decision
Every acceptance criterion has an executable scenario that cites it, red for
the right reason before the code exists. Feature files, organized by
capability, are the description of how the system behaves today. Gherkin is
the default format; the adapter names the runner.

## Why
A spec the tests run can't silently become false. The trace comment ties
each criterion to its scenario in both directions, and the validator fails
an uncited criterion.

## Alternatives
- **Prose spec merged from deltas** (OpenSpec) — readable, but nothing keeps it true.
- **Gherkin mandatory** — excludes stacks without a BDD runner.
