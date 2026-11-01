#!/usr/bin/env bash
# Seeds a small sanchin project: a todo app with one component, a logging
# standard as its constitution, and a ready story whose scenarios are @pending.
set -euo pipefail
git init -q -b main
git config user.name eval && git config user.email eval@example.com
mkdir -p .claude docs/stories docs/plans docs/standards docs/decisions app/features src/app
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  mission_vision: docs/vision.md
  constitution: docs/standards/index.md
  decisions: docs/decisions/
docs: {root: docs, navigation_line: '^\[Docs\]\(', unindexed_catalogs: [stories, plans, decisions]}
stories: {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-01-01'}
scenarios: {globs: ['app/features/**/*.feature']}
plans:
  directory: docs/plans
  rules_since: '2026-01-01'
  required_sections:
    in_progress: [Current state, Design, Steps]
    implemented: [Current state, Design, Steps, Implementation, Review]
  constitution: {globs: [docs/standards/logging.md]}
YAML
cat > docs/index.md <<'MD'
# Docs

[vision](vision.md) · [standards](standards/index.md)
MD
cat > docs/vision.md <<'MD'
# Vision

[Docs](index.md)

A todo app for people who forget things.
MD
cat > docs/standards/index.md <<'MD'
# Standards

[Docs](../index.md)

| Standard | When |
|---|---|
| [logging](logging.md) | Any change under `src/`. |
MD
cat > docs/standards/logging.md <<'MD'
# Logging

[Docs](../index.md)

Application code never writes to stdout with `print`: it logs through the
module's logger. *Why:* stdout is the CLI's output channel.
MD
cat > src/app/todos.py <<'PY'
from dataclasses import dataclass, field


@dataclass
class Todo:
    id: int
    title: str
    owner: str


@dataclass
class TodoList:
    id: int
    owner: str
    todos: list[Todo] = field(default_factory=list)


def visible(todo_list: TodoList) -> list[Todo]:
    return list(todo_list.todos)


def delete_list(todo_list: TodoList, user: str) -> None:
    if user != todo_list.owner:
        raise PermissionError("only the owner can delete a list")
PY
cat > docs/stories/st-02-share.md <<'MD'
---
id: ST-02
state: ready
scenarios: app/features/share.feature
---
# ST-02 — Share a list with a friend

[Docs](../index.md)

As a user, I want to share a list with a friend, so that we can keep track of the same todos.

## Acceptance criteria

1. I can share one of my lists with a friend by their email.
2. The friend sees the shared list among their lists.
MD
cat > app/features/share.feature <<'FEATURE'
Feature: share

  # ST-02: AC 1, 2
  @pending
  Scenario: a shared list shows up for the friend
    Given I own the list "groceries"
    When I share it with "ana@example.com"
    Then Ana sees "groceries" among her lists
FEATURE
git add -A && git commit -q -m "ST-02 ready"
