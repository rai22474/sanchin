# 0008 — Deterministic gates at four levels

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
Checks run at edit (plugin hook), pre-commit, pre-push and CI; each at the
earliest level where it is cheap. Gates run locally before green; reviewers
skip what gates enforce; a rule broken twice and checkable by code becomes
a gate. One hook dispatches every edit-level gate from the adapter.

## Why
A rule enforced by a prompt is enforced only as well as the prompt is read.
A failure seen at edit time is seen next to its cause.
