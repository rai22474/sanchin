---
type: llm
---

Judge the adapter the reply wrote to `.claude/sanchin.yaml` or showed in full (a YAML block).

PASS if that adapter keeps the project's own names: the stories directory `docs/roadmap/historias` with a `hu-*` pattern, the state key `estado` with `en curso` as the in-progress value, the criteria heading `Criterios de aceptación`, and a trace comment pattern that matches `# HU-01: CA 1`.
FAIL if no full adapter is shown or written, or it uses sanchin's default names (`state`, `in progress`, `Acceptance criteria`, `AC`) where the project has its own, or proposes renaming the project's files.
