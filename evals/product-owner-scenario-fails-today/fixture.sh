#!/usr/bin/env bash
# Seeds a sanchin project with a refined-in-all-but-name story whose second
# criterion is negative, about a page the code doesn't produce yet.
set -euo pipefail
git init -q -b main
mkdir -p .claude docs/stories docs/plans docs/decisions tests/features
cat > .claude/sanchin.yaml <<'YAML'
version: 1
language: en
components: [app]
base_docs:
  mission_vision: docs/vision.md
  decisions: docs/decisions/
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

A wiki for a gardening club: shared pages by topic, and a private area per member.
Today the wiki has topic folders and member folders under `private/`, but no home page:
opening `/` shows "create this page".
MD
cat > tests/features/pages.feature <<'FEATURE'
Feature: wiki pages

  # ST-01: AC 1
  Scenario: a member writes a topic page
    Given a member "ana"
    When "ana" writes the page "roses/pruning.md"
    Then the wiki has the page "roses/pruning.md"
FEATURE
git add -A && git commit -q -m init
cat > docs/stories/st-02-home.md <<'MD'
---
id: ST-02
state: pending
---
# ST-02 — Home page with the wiki's topics

[Docs](../index.md)

As a club member opening the wiki, I want a home page listing its topics.

## Acceptance criteria

1. The wiki root has `Home.md`, with one section per topic folder that has at least one page.
2. Pages of the private area (`private/`) are not listed on the home page.

## Out of scope

- Topic index pages.
MD
