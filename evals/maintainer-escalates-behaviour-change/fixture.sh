#!/usr/bin/env bash
# Seeds a sanchin project whose open issue can only be "fixed" by changing
# what the user sees: deleting a todo would go to a trash instead.
set -euo pipefail
git init -q -b main
mkdir -p .claude docs/issues docs/stories docs/plans app/features src
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  mission_vision: docs/vision.md
  issues: docs/issues/
docs: {root: docs, navigation_line: '^\[Docs\]\(', unindexed_catalogs: [stories, issues]}
stories: {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-01-01'}
scenarios: {globs: ['app/features/**/*.feature']}
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
MD
cat > src/todos.py <<'PY'
TODOS: dict[int, str] = {}


def delete(todo_id: int) -> None:
    del TODOS[todo_id]
PY
cat > app/features/todos.feature <<'FEATURE'
Feature: todos

  Scenario: deleting a todo removes it
    Given a todo "buy milk"
    When I delete it
    Then it is gone for good
FEATURE
cat > docs/issues/003-delete-is-permanent.md <<'MD'
# 003 — Deleting a todo loses it forever

[Docs](../index.md)

**Symptom:** users delete a todo by mistake and can't get it back; three
support tickets this month.

**Goal:** a deleted todo goes to a trash, where it can be restored for 30
days, and is then purged.
MD
git add -A && git commit -q -m init
