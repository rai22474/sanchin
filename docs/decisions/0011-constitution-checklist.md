# 0011 — Plans answer the constitution as a checklist

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
A plan answers every rule of the project's constitution with `n/a`, `ok`
or `exception → D-n`. The validator checks that no rule is missing and that
every exception names its decision; the technical grill and the review judge
the answers.

## Why
Free text records the rules the author thought of; a checklist records that
each one was looked at, and turns exceptions into explicit, justified
decisions. (Spec Kit's constitution gates and complexity tracking.)
