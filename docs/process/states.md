# States

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

A story moves through five states, in order. Each state is what the role
that sets it owes the next one, and the validator checks it.

| State | Set by | Means | The validator requires |
|---|---|---|---|
| **pending** | product owner, architect, maintainer | A draft: doubts allowed. | an id |
| **ready** | product owner | Refined: the "what" is closed. | no doubt marker; its scenarios, every criterion cited, tagged `@pending`; its milestone (with that layer on) |
| **planned** | tech-lead | The "how" is closed. | its plans: required sections, no open question, constitution checklist |
| **in progress** | developer | Code is being written. | as planned |
| **implemented** | developer | Done and merged. | its date; scenarios without `@pending`; plans with Implementation and Review |

A role that finds its input isn't really closed sends the story **back**,
on `main`, where the owner works: the tech-lead who hits a functional
question writes it as a doubt marker and returns the story to pending; the
developer who hits a design question writes it as an open question in the
plan and returns the story to ready, leaving the worktree paused — once the
story is planned again, the developer rebases onto `main` and goes on.
*Why:* a question answered by the wrong role is a decision taken without its
owner.

Nothing a role decides lives only in the chat: it is written in the wiki —
story, scenarios, plan, decision record, issue — in the same commit as the
work, once the user confirms it ([context.md](../context.md)). *Why:* the next
session and the next role start knowing nothing; they can only build on
what they can read.

Every cycle ends with a short **retro** where its artifact lives — the
story, the plan, the decision record, the issue — in the five fields of
[improvement.md](../improvement.md#the-retro). *Why:* the coach can only
improve the cycles it can read; a correction made while refining is lost if
only delivery writes one.
