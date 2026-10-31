"""Story rules: the spec is immutable, incremental and traced to scenarios.

- frontmatter has a unique id and a known state; an implemented story has
  its date (YYYY-MM-DD), so it can't slip past `rules_since`, unless
  `stories.legacy` lists it (implemented before the rules, left as it is);
- `plan` and `scenarios` paths exist; an in-progress story has its plan,
  and a story implemented since `rules_since` has its plan and scenarios
  (technical stories need no scenarios);
- no doubt marker survives once the story leaves pending;
- every scenario citation names an existing story and criterion, and every
  criterion of a story implemented since `rules_since` is cited;
- a `Supersedes` link points to an existing story;
- the scenario delta matches the feature files: before implementation the
  scenarios it changes or removes exist, after it the added and changed
  ones exist and the removed ones are gone.

Reference: docs/artifacts.md#story.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .markdown import parse_frontmatter, section
from .scenarios import Citation, scenario_names

_CRITERION_LINE = re.compile(r"^(\d+)\.\s+(.*)$", re.MULTILINE)
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DELTA_LINE = re.compile(r"^\s*[-*]\s+(?P<op>[+~\-−])\s+`?(?P<feature>[^`:\s]+\.feature)`?\s*:\s*(?P<scenario>.+?)\s*$", re.MULTILINE)
SUPERSEDED_START = "<!-- sanchin:superseded-by:start -->"
SUPERSEDED_END = "<!-- sanchin:superseded-by:end -->"


@dataclass(frozen=True)
class Story:
    path: Path
    text: str
    fields: dict[str, str]

    def get(self, key: str) -> str | None:
        return self.fields.get(key)


def load_stories(config: Config) -> tuple[list[Story], list[str]]:
    stories, errors = [], []
    for path in sorted(config.stories.directory.glob(config.stories.glob)):
        text = path.read_text(encoding="utf-8")
        fields, problems = parse_frontmatter(text)
        errors.extend(f"{path}: {problem}" for problem in problems)
        if fields is not None:
            stories.append(Story(path, text, fields))
    return stories, errors


def check_stories(config: Config, stories: list[Story], citations: list[Citation]) -> list[str]:
    errors = []
    for story in stories:
        errors.extend(f"{story.path}: {problem}" for problem in _story_problems(config, story))
    errors.extend(_duplicate_id_problems(config, stories))
    errors.extend(_citation_problems(config, stories, citations))
    return errors


def _duplicate_id_problems(config: Config, stories: list[Story]) -> list[str]:
    by_id: dict[str, list[Story]] = {}
    for story in stories:
        if story.get(config.stories.id_key):
            by_id.setdefault(story.get(config.stories.id_key), []).append(story)
    return [
        f"{same[0].path}: id {story_id} is also used by {', '.join(str(other.path) for other in same[1:])}"
        for story_id, same in sorted(by_id.items())
        if len(same) > 1
    ]


def criteria(config: Config, story: Story) -> dict[int, str]:
    body = section(story.text, config.stories.criteria_heading)
    if body is None:
        return {}
    return {int(match.group(1)): match.group(2) for match in _CRITERION_LINE.finditer(body)}


def superseded_by(config: Config, stories: list[Story]) -> dict[Path, list[Path]]:
    reverse: dict[Path, list[Path]] = {}
    pattern = re.compile(config.stories.supersedes_pattern)
    for story in stories:
        for target in pattern.findall(story.text):
            resolved = (story.path.parent / target.split("#", 1)[0]).resolve()
            reverse.setdefault(resolved, []).append(story.path)
    return reverse


def render_superseded_block(config: Config, stories: list[Story]) -> str:
    rows = []
    for old, new_paths in sorted(superseded_by(config, stories).items()):
        newer = ", ".join(f"[{path.stem}]({_relative(config, path)})" for path in sorted(new_paths))
        rows.append(f"| [{old.stem}]({_relative(config, old)}) | {newer} |")
    table = "\n".join(["| Story | Superseded by |", "|---|---|", *rows]) if rows else "_No story has been superseded yet._"
    return f"{SUPERSEDED_START}\n{table}\n{SUPERSEDED_END}"


def _relative(config: Config, path: Path) -> str:
    index = config.stories.superseded_index
    base = index.parent if index is not None else config.stories.directory
    return Path(os.path.relpath(path.resolve(), base.resolve())).as_posix()


def is_legacy(config: Config, story: Story) -> bool:
    """Listed in `stories.legacy`: implemented before the rules, left as it is."""
    return story.path.relative_to(config.project_root).as_posix() in config.stories.legacy


def implemented_under_rules(config: Config, story: Story) -> bool:
    keys = config.stories
    return (
        story.get(keys.state_key) == keys.states["implemented"]
        and not is_legacy(config, story)
        and (story.get(keys.date_key) or "") >= keys.rules_since
    )


def _story_problems(config: Config, story: Story) -> list[str]:
    keys = config.stories
    states = keys.states
    problems = []
    if not story.get(keys.id_key):
        problems.append(f"frontmatter has no {keys.id_key!r}")
    state = story.get(keys.state_key)
    if state not in states.values():
        problems.append(f"{keys.state_key} {state!r} is not one of {sorted(states.values())}")
    legacy = is_legacy(config, story)
    if state == states["implemented"] and not legacy and not _ISO_DATE.fullmatch(story.get(keys.date_key) or ""):
        problems.append(f"a story {state!r} needs its {keys.date_key!r} as YYYY-MM-DD (or list it in stories.legacy)")
    problems.extend(_path_problems(config, story))
    under_rules = implemented_under_rules(config, story)
    if (state == states["in_progress"] or under_rules) and not story.get(keys.plan_key):
        problems.append(f"a story {state!r} needs its {keys.plan_key!r}")
    if under_rules and not story.get(keys.scenarios_key) and story.get(keys.kind_key) != keys.technical_kind:
        problems.append(f"a story {state!r} needs its {keys.scenarios_key!r}")
    if state in (states["in_progress"], states["implemented"]) and keys.doubt_marker in story.text:
        problems.append(f"unresolved {keys.doubt_marker!r} marker in a story {state!r}; resolve it in the functional grill")
    problems.extend(_supersedes_problems(config, story))
    problems.extend(_delta_problems(config, story, implemented=state == states["implemented"]))
    return problems


def _path_problems(config: Config, story: Story) -> list[str]:
    problems = []
    for key, suffix in ((config.stories.plan_key, ".md"), (config.stories.scenarios_key, ".feature")):
        for path in _paths(config, story, key):
            if not path.endswith(suffix):
                problems.append(f"{key} {path!r} is not a {suffix} file")
            elif not (config.project_root / path).is_file():
                problems.append(f"{key} {path!r} does not exist")
    return problems


def _supersedes_problems(config: Config, story: Story) -> list[str]:
    return [
        f"supersedes {target!r}, which does not exist"
        for target in re.findall(config.stories.supersedes_pattern, story.text)
        if not (story.path.parent / target.split("#", 1)[0]).is_file()
    ]


def _delta_problems(config: Config, story: Story, implemented: bool) -> list[str]:
    body = section(story.text, config.stories.delta_heading)
    if body is None:
        return []
    problems = []
    for match in _DELTA_LINE.finditer(body):
        operation, scenario = match.group("op"), match.group("scenario")
        feature = config.project_root / match.group("feature")
        present = scenario in scenario_names(feature)
        if implemented:
            expected_present = operation in "+~"
        elif operation == "+":
            continue
        else:
            expected_present = True
        if present != expected_present:
            state = "should exist" if expected_present else "should be gone"
            problems.append(f"scenario delta {operation} {match.group('feature')}: {scenario!r} {state}")
    return problems


def _citation_problems(config: Config, stories: list[Story], citations: list[Citation]) -> list[str]:
    keys = config.stories
    by_id = {story.get(keys.id_key): story for story in stories}
    problems = []
    for citation in citations:
        story = by_id.get(citation.story_id)
        if story is None:
            problems.append(f"{citation.feature}: cites unknown story {citation.story_id}")
        elif citation.criterion not in criteria(config, story):
            problems.append(f"{citation.feature}: cites criterion {citation.criterion} of {citation.story_id}, which does not exist")
    cited = {(citation.story_id, citation.criterion) for citation in citations}
    for story in stories:
        if not implemented_under_rules(config, story):
            continue
        if not story.get(keys.scenarios_key):
            continue
        story_criteria = criteria(config, story)
        if not story_criteria:
            problems.append(f"{story.path}: no numbered criteria under {keys.criteria_heading!r}")
        uncovered = [
            str(number)
            for number, text in story_criteria.items()
            if (story.get(keys.id_key), number) not in cited and keys.criterion_exemption not in text
        ]
        if uncovered:
            problems.append(f"{story.path}: criteria {', '.join(uncovered)} not cited by any scenario")
    return problems


def _paths(config: Config, story: Story, key: str) -> list[str]:
    return [path for path in (story.get(key) or "").split(config.stories.path_separator) if path]
