# 0022 — Distribute the shared process in Claude Code and Codex

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-11-25)

## Context

The process started as a Claude Code plugin. Codex can use the same roles,
artifacts and validator. It has its own discovery, commands and runtime.

## Decision

Keep the process, role instructions, templates and validator in one versioned
source. Claude Code loads the plugin. The [Codex installer](../codex.md)
generates project-local role entries that load the same source at the
project's chosen version. Both clients read `.claude/sanchin.yaml`.

This extends [0001](0001-plugin-and-adapter.md). The plugin dependency
from [0018](0018-depend-on-mattpocock-skills.md) is specific to Claude Code.
Both clients run the two reviews from [0012](0012-two-reviews-measured.md).
The [working rules](../process/working-rules.md) specify how each client
runs interviews, delegation and generic review.

## Consequences

Git hooks and CI can call the same validator. The Claude Code package adds
automation for edit checks, cycle isolation and protection of the adapter's
approval settings. The Codex distribution uses explicit checks, session
hand-offs and the client's permissions. The existing skill eval runner
covers the Claude Code plugin.
