#!/usr/bin/env bash
# Seeds three closed stories whose retros carry one signal seen twice (ruff
# failing on import order) and one seen once (a correction about mocks).
set -euo pipefail
git init -q -b main
mkdir -p .claude docs/stories docs/plans
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  process_log: docs/process-log.md
docs: {root: docs, navigation_line: '^\[Docs\]\(', unindexed_catalogs: [stories, plans]}
stories: {directory: docs/stories, glob: 'st-*.md', rules_since: '2026-01-01'}
scenarios: {globs: ['app/features/**/*.feature']}
plans: {directory: docs/plans, rules_since: '2026-01-01'}
gates:
  - {name: ruff, glob: '*.py', run: 'uv run ruff check {file}', level: pre-commit}
YAML
cat > docs/index.md <<'MD'
# Docs

[process log](process-log.md)
MD
cat > docs/process-log.md <<'MD'
# Process log

[Docs](index.md)

- 2026-01-01 — coach: first run, nothing to report.
MD
retro() {  # id, slug, retro body
  cat > "docs/stories/st-$1-$2.md" <<MD
---
id: ST-$1
state: implemented
date: 2026-02-0$1
plan: docs/plans/$2.md
kind: technical
---
# ST-$1 — $2

[Docs](../index.md)

## Acceptance criteria

1. (no scenario: technical) $2 works.
MD
  cat > "docs/plans/$2.md" <<MD
# Plan — $2 (ST-$1)

[Docs](../index.md)

## Current state
x
## Design
y
## Steps
- [x] done
## Implementation
as planned
## Review
- none
## Retro
$3
MD
}
retro 1 export "- Gates: ruff failed twice on import order (isort rules) before commit.
- Friction: none."
retro 2 search "- Corrections: the user asked not to mock the database in acceptance tests (project).
- Gates: none."
retro 3 sync "- Gates: ruff failed on import order again; fixed by hand each time.
- Friction: none."
git add -A && git commit -q -m init
