#!/usr/bin/env bash
# Seeds a story branch whose diff breaks a project standard (print instead
# of the logger) and has a line too long — which a declared gate enforces.
set -euo pipefail
git init -q -b main
git config user.name eval && git config user.email eval@example.com
mkdir -p .claude docs/stories docs/plans docs/standards app/features src/app
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  constitution: docs/standards/index.md
docs: {root: docs, navigation_line: '^\[Docs\]\(', unindexed_catalogs: [stories, plans]}
stories: {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-01-01'}
scenarios: {globs: ['app/features/**/*.feature']}
plans:
  directory: docs/plans
  rules_since: '2026-01-01'
  constitution: {globs: [docs/standards/logging.md]}
gates:
  - {name: line-length, glob: '*.py', run: 'uv run ruff check --select E501 {file}', level: edit}
YAML
cat > docs/index.md <<'MD'
# Docs

[standards](standards/index.md)
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
module's logger (`logger = logging.getLogger(__name__)`). *Why:* stdout is
the CLI's output channel; diagnostics in it break every consumer that
parses it.
MD
cat > docs/stories/st-01-export.md <<'MD'
---
id: ST-01
state: in progress
plan: docs/plans/export.md
scenarios: app/features/export.feature
---
# ST-01 — Export todos as CSV

[Docs](../index.md)

As a user, I want to export my todos as CSV, so that I can open them in a spreadsheet.

## Acceptance criteria

1. Exporting writes one CSV line per todo, title first.
MD
cat > docs/plans/export.md <<'MD'
# Plan — CSV export (ST-01)

[Docs](../index.md)

## Current state
No export.
## Design
`src/app/export.py` with `export_csv(todos) -> str`.
## Constitution checklist
- logging: ok
## Steps
- [x] export_csv
## Open questions
## Decisions
## Implementation
## Review
MD
cat > app/features/export.feature <<'FEATURE'
Feature: export

  # ST-01: AC 1
  Scenario: one line per todo
    Given todos "milk" and "eggs"
    When I export them
    Then the CSV has the lines "milk" and "eggs"
FEATURE
git add -A && git commit -q -m "ST-01: story and plan"
git checkout -q -b story/st-01
cat > src/app/export.py <<'PY'
def export_csv(todos: list[dict]) -> str:
    print("exporting", len(todos), "todos")
    lines = [f"{todo['title']},{todo.get('due', '')},{todo.get('done', False)},{todo.get('notes', '')},{todo.get('tags', '')}" for todo in todos]
    return "\n".join(lines)
PY
git add -A && git commit -q -m "ST-01: export_csv"
