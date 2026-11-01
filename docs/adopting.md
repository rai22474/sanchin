# Adopting sanchin in an existing project

[README](../README.md) · [Docs](index.md)

A project with years of docs, its own templates and its own words doesn't
start over. `/sanchin:init` maps what exists and only adds what is missing;
the rules switch on from a cut-off date so history is never rewritten.

## 1. Map, don't move

Run `/sanchin:init`. It looks for:

- the docs root and its entry index, and the navigation line its pages use;
- stories (or user stories, `HU-*`, tickets as markdown): directory, file
  pattern, frontmatter keys and state values, the heading of the
  acceptance criteria;
- feature files and how scenarios cite criteria;
- plans or technical specs, and the headings they use;
- decision records, standards and design smells (the constitution);
- mission, vision, stack and glossary;
- existing gates: git hooks, CI jobs, linters.

It writes `.claude/sanchin.yaml` with what it found and asks only what it
can't infer. Nothing is renamed or moved: the adapter takes the project's
names (`historia`, `estado: en curso`, `Criterios de aceptación`).

## 2. Cut over, don't backfill

Set `stories.rules_since` and `plans.rules_since` to the day you adopt.
Stories implemented before it, and plans listed in `plans.legacy`, are
left alone. An implemented story needs its date to be placed before or
after the cut-off; old stories without one go in `stories.legacy` instead
of getting a date added. *Why:* rewriting history to satisfy a new rule produces fake
records; the rules apply from the day they exist.

Run `scripts/sanchin check`. On a healthy project the first run reports
only things that are really wrong today — broken links, a story in
progress without its plan — and plans written before the rules, which go to
`legacy`.

## 3. Replace, one by one

Where the project already had its own checks, replace them with the
plugin's in separate, small changes:

- per-tool edit hooks → one `gates:` list in the adapter;
- a doc-references script → `sanchin check --only docs`;
- traceability checks in a roadmap script → `sanchin check --only stories`,
  leaving the script only what is the project's own (generated tables,
  milestone states).

Each replacement keeps the same gate green before and after.

## 4. Thin the entry points

Move every process rule out of `CLAUDE.md` and project skills into either
the plugin (if it is generic) or the project's standards (if it isn't), and
leave pointers behind ([context.md](context.md)). Rules that lived only in
an agent's memory move the same way.

## 5. Use it on the next story

The real test is the next story taken through the cycles:
`/sanchin:product-owner` to ready, `/sanchin:tech-lead` to planned,
`/sanchin:developer` to implemented. A project adopting mid-flight can
start where its story already is — a story with closed plans is planned.
Its retro is the first signal for both the project's adapter and sanchin
itself.
