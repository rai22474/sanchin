# 0009 — Progressive context: format, not layout

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
sanchin imposes thin entry points, navigation indexes with "what it
contains" and "when to read it", catalog indexes, and a navigation line on
every page; the validator checks lines and index completeness. Where
directories live is the project's choice, mapped in the adapter.

## Why
An agent works well with the right documents and badly with all of them.
Imposing a layout would make adoption a migration.

## Revision — 2026-11-01: sanchin's own docs follow it

The process and the artifact formats are directories — an index with what
and when, then one document per cycle and per format — and each role skill
names the documents it reads. *Why:* the single process document had
grown to 4,200 words, read whole by every role; a plugin that asks projects
for progressive disclosure has to practise it.
