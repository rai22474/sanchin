#!/usr/bin/env bash
# Seeds a minimal sanchin project in the current (empty) workspace.
set -euo pipefail
git init -q -b main
mkdir -p .claude docs/stories docs/plans docs/proposals docs/decisions tests/features
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  mission_vision: docs/vision.md
  decisions: docs/decisions/
  proposals: docs/proposals/
docs: {root: docs, navigation_line: '^\[Docs\]\(', unindexed_catalogs: [stories]}
stories: {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-01-01'}
scenarios: {globs: ['tests/features/**/*.feature']}
plans: {directory: docs/plans, rules_since: '2026-01-01'}
YAML
cat > docs/index.md <<'MD'
# Docs

[vision](vision.md)
MD
cat > docs/vision.md <<'MD'
# Vision

[Docs](index.md)

A todo app for people who forget things.

Principle: **every action is reversible from the screen where it happened** —
we prefer undo over confirmation dialogs.
MD
git add -A && git commit -q -m init
cat > docs/stories/st-01-archive.md <<'MD'
---
id: ST-01
state: pending
---
# ST-01 — Archive a todo

[Docs](../index.md)

## Acceptance criteria

1. Archiving a todo hides it from the main list.
2. Archived todos are kept for [DOUBT: how long? forever, or purged after some days?]
MD
