"""An implemented story, and its plans, are never edited.

The baseline is the first commit where the story's state line reads
implemented — the close commit, which also carries the plans' Review and
Retro. Any later difference in the story or its plans, committed or not, is
an edit of a closed record. A change of behaviour is a new story that
supersedes it ([process/product.md](../../docs/process/product.md#13-stories-from-a-narrative)).

Skipped without git, for stories in `stories.legacy`, and for a story whose
implemented state isn't committed yet or whose baseline commit isn't in
the history (a shallow clone).
Reference: docs/artifacts/story.md.
"""

import re
import subprocess
from pathlib import Path

from .config import Config
from .stories import Story, is_legacy

_BRE_SPECIAL = re.compile(r"([.\[\]\\*^$])")


def immutability_problems(config: Config, stories: list[Story]) -> list[str]:
    if _git(config, "rev-parse", "--is-inside-work-tree") is None:
        return []
    keys = config.stories
    pattern = f"^{_bre(keys.state_key)}:[[:space:]]*{_bre(keys.states['implemented'])}"
    problems = []
    for story in stories:
        if story.get(keys.state_key) != keys.states["implemented"] or is_legacy(config, story):
            continue
        story_path = story.path.relative_to(config.project_root).as_posix()
        log = _git(config, "log", "--reverse", "--format=%H", "-G", pattern, "--", story_path)
        if not log:
            continue
        baseline = log.split()[0]
        paths = [story_path, *_plan_paths(config, story)]
        changed = _git(config, "diff", "--name-only", baseline, "--", *paths)
        if changed:
            problems.append(
                f"{story.path}: edited after it was implemented in {baseline[:8]} "
                f"({', '.join(changed.split())}); a change of behaviour is a new story that supersedes it"
            )
    return problems


def _plan_paths(config: Config, story: Story) -> list[str]:
    raw = story.get(config.stories.plan_key) or ""
    return [path for path in raw.split(config.stories.path_separator) if path and path not in config.plans.legacy]


def _bre(text: str) -> str:
    return _BRE_SPECIAL.sub(r"\\\1", text)


def _git(config: Config, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(config.project_root), *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None
