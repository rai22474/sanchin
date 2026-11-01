"""The roadmap: a set of milestones, each holding the stories it delivers.

With the `milestone` layer on, a story names its milestone in its
frontmatter (`milestone: <file name without .md>`), and each milestone file
carries a table of its stories and their states between two markers. The
table is generated — `sanchin roadmap --write` — never written by hand. The
milestone's own state (planned, in progress, closed) is the product owner's
decision, written in its state line, and checked:

- every story's milestone exists;
- every milestone's state is one of the configured values, at most one is
  in progress, and it reads closed exactly when it has stories and all of
  them are implemented;
- the generated tables are up to date.

Reference: docs/artifacts/layers-and-roadmap.md#roadmap.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .markdown import strip_frontmatter
from .stories import Story, state_name

START = "<!-- sanchin:milestone-stories:start -->"
END = "<!-- sanchin:milestone-stories:end -->"


@dataclass(frozen=True)
class Milestone:
    path: Path
    text: str

    @property
    def name(self) -> str:
        return self.path.stem


def load_milestones(config: Config) -> list[Milestone]:
    if config.roadmap is None or not config.roadmap.directory.is_dir():
        return []
    return [
        Milestone(path, path.read_text(encoding="utf-8"))
        for path in sorted(config.roadmap.directory.glob(config.roadmap.glob))
        if path.name != "index.md"
    ]


def stories_of(config: Config, milestone: Milestone, stories: list[Story]) -> list[Story]:
    return [story for story in stories if story.get(config.stories.milestone_key) == milestone.name]


def render_block(config: Config, milestone: Milestone, stories: list[Story]) -> str:
    rows = [
        f"| [{_title(story)}]({_relative(milestone, story)}) | {story.get(config.stories.state_key)} |"
        for story in stories_of(config, milestone, stories)
    ]
    table = "\n".join(["| Story | State |", "|---|---|", *rows]) if rows else "_No story in this milestone yet._"
    return f"{START}\n{table}\n{END}"


def write_blocks(config: Config, stories: list[Story]) -> list[str]:
    """Rewrite every milestone's generated table; returns the problems that prevented it."""
    problems = []
    for milestone in load_milestones(config):
        if START not in milestone.text or END not in milestone.text:
            problems.append(f"{milestone.path}: has no {START} … {END} block")
            continue
        text = milestone.text
        updated = text[: text.index(START)] + render_block(config, milestone, stories) + text[text.index(END) + len(END) :]
        if updated != text:
            milestone.path.write_text(updated, encoding="utf-8")
    return problems


def roadmap_problems(config: Config, stories: list[Story]) -> list[str]:
    roadmap = config.roadmap
    if roadmap is None:
        return []
    milestones = load_milestones(config)
    if not milestones and any(story.get(config.stories.milestone_key) for story in stories):
        return [f"{roadmap.directory}: no milestones, but stories name one"]
    problems = []
    in_progress = []
    pattern = re.compile(roadmap.state_pattern, re.MULTILINE)
    for milestone in milestones:
        match = pattern.search(strip_frontmatter(milestone.text))
        if match is None:
            problems.append(f"{milestone.path}: no state line matching {roadmap.state_pattern!r}")
        else:
            problems.extend(_state_problems(config, milestone, match.group("state").strip(), stories, in_progress))
        if START not in milestone.text or END not in milestone.text:
            problems.append(f"{milestone.path}: has no {START} … {END} block for its stories")
        elif render_block(config, milestone, stories) not in milestone.text:
            problems.append(f"{milestone.path}: the stories table is stale; run `sanchin roadmap --write`")
    if len(in_progress) > 1:
        problems.append(f"{roadmap.directory}: {len(in_progress)} milestones in progress ({', '.join(in_progress)}); only one at a time")
    return problems


def _state_problems(config: Config, milestone: Milestone, state: str, stories: list[Story], in_progress: list[str]) -> list[str]:
    states = config.roadmap.states
    if state not in states.values():
        return [f"{milestone.path}: state {state!r} is not one of {list(states.values())}"]
    if state == states["in_progress"]:
        in_progress.append(milestone.name)
    held = stories_of(config, milestone, stories)
    open_stories = [story.get(config.stories.id_key) for story in held if state_name(config, story) != "implemented"]
    if state == states["closed"] and (not held or open_stories):
        missing = ", ".join(open_stories) if open_stories else "it has no stories"
        return [f"{milestone.path}: reads {state!r} but isn't done ({missing})"]
    if state != states["closed"] and held and not open_stories:
        return [f"{milestone.path}: every story is implemented; set its state to {states['closed']!r}"]
    return []


def _title(story: Story) -> str:
    for line in strip_frontmatter(story.text).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return story.path.stem


def _relative(milestone: Milestone, story: Story) -> str:
    return Path(os.path.relpath(story.path.resolve(), milestone.path.parent.resolve())).as_posix()
