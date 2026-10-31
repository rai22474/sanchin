---
type: llm
---

PASS if the review reports the `print` in `src/app/export.py` as breaking the project's logging standard (citing it), labels that finding with its source (such as `standards-app`), and does not report the over-long line as its own finding — the declared `line-length` gate enforces it.
FAIL if the review misses the `print`, reports the line length as a finding of its own, or lists findings without a source label.
