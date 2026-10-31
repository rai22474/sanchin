"""A tiny project on disk, built per test, with a sanchin adapter."""

import tempfile
import textwrap
from pathlib import Path

ADAPTER = """
version: 1
language: en
components: [app]
docs:
  root: docs
  navigation_line: '^\\[Docs\\]\\('
  unindexed_catalogs: [stories]
  code_reference_globs: ['{component}/**/*.py']
stories:
  directory: docs/stories
  glob: 'story-*.md'
  rules_since: '2026-01-01'
  superseded_index: docs/stories-superseded.md
scenarios:
  globs: ['{component}/features/**/*.feature']
plans:
  directory: docs/plans
  rules_since: '2026-01-01'
  required_sections:
    in_progress: [Current state, Design, Steps]
    implemented: [Current state, Design, Steps, Implementation, Review]
  constitution:
    globs: [docs/constitution/*.md]
gates:
  - name: no-todo
    glob: '*.py'
    run: '! grep -n TODO {file}'
"""


class Project:
    def __init__(self):
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name)
        self.write(".claude/sanchin.yaml", ADAPTER)

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
        return path

    def close(self):
        self._directory.cleanup()


def story(story_id: str, state: str, extra: str = "", body: str = "") -> str:
    frontmatter = f"---\nid: {story_id}\nstate: {state}\n{extra}---\n"
    criteria = "## Acceptance criteria\n\n1. The first thing.\n2. The second thing.\n"
    return frontmatter + f"# {story_id}\n\n[Docs](../index.md)\n\n" + criteria + body
