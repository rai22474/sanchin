# 0006 — One plan per component, one worktree per story, local merge

[README](../../README.md) · [Decisions](index.md)

**Status:** accepted (2026-10-31)

## Decision
A story touching several components has one plan per component; the
contract between them lives in the provider's plan only. Each story runs in
its own branch and worktree; each plan is implemented by a sub-agent in a
child worktree and merged into the story branch, where the acceptance
scenarios run. The story merges into `main` locally, with the user's
approval — no pull request required.

## Why
A contract written twice diverges. Parallel sessions on one working tree
mix their changes into each other's commits. A pull request is optional
ceremony for a single maintainer; the reviews already happened.
