---
type: llm
---

PASS if the review reports the `print` in `src/app/export.py` as breaking the project's logging standard (`docs/standards/logging.md`), and every finding it lists carries a source label (such as `standards-app`, `spec`, `generic-spec`).
FAIL if it misses the `print`, or lists any finding without a source label.
