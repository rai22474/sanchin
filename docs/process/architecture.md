# 4. Architecture cycle

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

`/sanchin:architect`, on a technical idea: a refactor of the architecture,
a new tool or dependency, a change to how components talk, or a design the
tech-lead couldn't fit in the decisions in force.

## 4.1 Technical grill

Grill the idea with the user — starting by invoking
`mattpocock-skills:grilling` ([working-rules.md](working-rules.md#grills)) —
technical side: the problem it solves, the
decisions in force it touches, the alternatives and their trade-offs.
Research first — read the decision records, the constitution, and the code
only to check whether reality matches them.

## 4.2 Decision record

Write the decision as a draft record in the project's decisions directory,
following an existing record's structure: context, decision, alternatives
considered, consequences. A change to a decision in force is a new record
that supersedes it, or a dated revision in it — the original is never
rewritten. The user accepts it. *Why:* the decision record is the
constitution's history; a decision left in the chat is lost to the next
session, and one rewritten in place loses why it changed.

## 4.3 Technical stories

Break the work the decision implies into **technical stories**
(`kind: technical`): what must be true when each is done, as numbered
criteria, linking the decision. They need no scenarios and no narrative.
Leave them pending, for the product owner to place in the roadmap and set
ready. *Why:* technical work competes with features for the same time; one
roadmap decides the order of both.

Write the cycle's retro in the decision record's **Retro** section, and
stop: the product owner places the stories.
