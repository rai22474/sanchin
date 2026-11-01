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
  stack: docs/stack.md
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

[vision](vision.md) · [stack](stack.md) · [standards](standards/index.md)
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


@dataclass
class TodoList:
    id: int
    todos: list[Todo] = field(default_factory=list)


def visible(todo_list: TodoList) -> list[Todo]:
    return list(todo_list.todos)
PY
cat > docs/stack.md <<'MD'
# Stack

[Docs](index.md)

Python 3.12, single user, in-process. Tests: `pytest`; acceptance scenarios
in `app/features/` run with `pytest-bdd` (`uv run pytest app/features`),
which skips `@pending` scenarios.
MD
cat > docs/stories/st-01-archive.md <<'MD'
---
id: ST-01
state: ready
scenarios: app/features/archive.feature
---
# ST-01 — Archive a todo

[Docs](../index.md)

As a user, I want to archive a todo I no longer need, so that my list shows only what is left to do.

## Acceptance criteria

1. Archiving a todo hides it from the list.
2. Archived todos of a list can be listed on their own.
MD
cat > app/features/archive.feature <<'FEATURE'
Feature: archive

  # ST-01: AC 1
  @pending
  Scenario: an archived todo leaves the list
    Given a list with the todos "milk" and "eggs"
    When I archive "milk"
    Then the list shows only "eggs"

  # ST-01: AC 2
  @pending
  Scenario: archived todos are listed on their own
    Given a list where "milk" is archived
    When I list its archived todos
    Then I see "milk"
FEATURE
git add -A && git commit -q -m "ST-01 ready"
