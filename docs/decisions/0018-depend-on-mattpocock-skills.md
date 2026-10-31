# 0018 — Depend on mattpocock-skills for grills and the generic review

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
sanchin declares `mattpocock-skills` (from `claude-plugins-official`) as a
plugin dependency, so installing sanchin installs it. The grills use
`/mattpocock-skills:grilling` and the first review uses
`/mattpocock-skills:code-review`; sanchin doesn't ship its own versions of
either. The marketplace allows that one cross-marketplace dependency.

## Why
A step that runs "if some plugin happens to be installed" runs differently
on each machine, which defeats a reproducible process. Grilling and a
generic review are well served by a maintained plugin; copying them would
leave sanchin with a fork to keep in step.
