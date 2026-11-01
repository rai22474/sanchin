# 0021 — The wiki is the project's memory

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-11-01)

## Decision
Everything a project decides is written in its wiki — the docs in its
repository — by the role that decided it, in the same commit as the work:
mission and vision, epics to stories and milestones, feature files, plans
with their decisions and reviews, decision records and standards, issues,
and every cycle's retro. Nothing decided lives only in a chat or in an
agent's memory. Records are added to, never rewritten. Progressive
disclosure ([0009](0009-progressive-context.md)) is how an agent finds the
right part: thin entry points, indexes with what and when, a navigation line
on every page.

## Alternatives considered
- **The agent's own memory** (memory files, long-lived sessions): private
  to one agent and one machine; a sub-agent, the next session or a teammate
  doesn't see it, and nobody reviews it.
- **An external tool** (tracker, wiki service): outside the repository, so
  not versioned with the code, not reviewed with the change, and not
  checkable by the validator.
- **A single large context file**: loaded whole on every task, and goes
  stale as a block.

## Why
An agent starts every session cold, and sanchin splits work across roles
that never share a conversation: the tech-lead builds on what the product
owner wrote, the developer on what the tech-lead wrote. The only memory they
share is what is written where all of them read — versioned with the code
and kept navigable by the validator, so it is found and can be trusted.
