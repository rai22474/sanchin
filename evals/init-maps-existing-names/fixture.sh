#!/usr/bin/env bash
# An existing project with Spanish stories and its own frontmatter values.
set -euo pipefail
git init -q -b main
mkdir -p docs/roadmap/historias docs/planes app/tests/features
printf '# Wiki\n\n[historias](roadmap/historias/)\n' > docs/index.md
cat > docs/roadmap/historias/hu-01-alta.md <<'MD'
---
id: HU-01
estado: en curso
plan: docs/planes/alta.md
---
# HU-01 — Dar de alta una tarea

[Wiki](../../index.md)

## Criterios de aceptación

1. La tarea aparece en la lista.
MD
printf '# Plan\n\n[Wiki](../index.md)\n\n## Estado actual\n\nx\n' > docs/planes/alta.md
printf 'Feature: alta\n\n  # HU-01: CA 1\n  Scenario: alta simple\n    Given nada\n' > app/tests/features/alta.feature
git add -A && git commit -q -m init
