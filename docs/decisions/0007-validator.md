# 0007 — A validator with built-in rules and configurable values

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
The plugin ships a validator (Python standard library plus PyYAML, run
through `uv` when present). Its rules are the process's and are the same in
every project; the adapter only sets names, paths and cut-off dates.
Project-specific checks stay project scripts, declared as gates.

## Why
Every project gets the same guarantees without writing its own checker.
A declarative rule language would be one more thing to design and maintain.

## Alternatives
- **Each project writes its validator** — rewritten in every project.
- **YAML-declared rules** — flexible, but a small language to maintain.
