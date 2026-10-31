# 0003 — Stories are immutable and incremental

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Context
When behaviour changes, editing the story that first described it erases
what was asked then and why the code looked the way it did.

## Decision
A story is editable while pending or in progress and frozen once
implemented. A change is a new story with a *supersedes* line and a
scenario delta (+ added, ~ changed, − removed). The reverse
"superseded by" table is generated. Plans are frozen the same way.

## Why
History is added to, never rewritten. The current state needs no
hand-maintained document: it is the scenarios and the code, which the delta
updates and the tests keep true.

## Alternatives
- **Living spec documents** — one more description of the system to keep in sync.
