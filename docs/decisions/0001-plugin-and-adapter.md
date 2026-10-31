# 0001 — A plugin for the process, an adapter per project

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Context
The process grew inside one project: its skills named that project's paths,
services and anecdotes. Reusing it meant copying and editing it, and every
copy drifted.

## Decision
The generic process lives in a versioned Claude Code plugin. Each project
describes itself in one file, `.claude/sanchin.yaml`. Skills, validator and
hook read the adapter and know nothing else about the project. Project-only
skills (benchmarks, deploys) stay in the project.

## Why
A reproducible process needs one seam between what is the same everywhere
and what differs. A template copied per project can't receive improvements;
a plugin pinned per project can.

## Alternatives
- **User-level skills** — no versioning, a change hits every project at once.
- **Template repository** — each project ends with its own copy.
