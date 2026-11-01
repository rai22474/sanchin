"""Story rules: the spec is immutable, incremental and traced to scenarios.

- frontmatter has a unique id and a known state; an implemented story has
  its date (YYYY-MM-DD), so it can't slip past `rules_since`, unless
  `stories.legacy` lists it (implemented before the rules, left as it is);
- states, in order: pending → ready → planned → in progress → implemented
  (docs/process/states.md); each adds what the role that hands it over owes:
  - ready (product owner): no doubt marker, its scenarios (technical
    stories excepted) with every criterion cited, and — with the milestone
    layer — its milestone;
  - planned / in progress (tech-lead): its plans (held to the plan rules);
  - implemented since `rules_since` (developer): plans and scenarios;
- `plan` and `scenarios` paths exist;
- every scenario citation names an existing story and criterion;
- a scenario whose stories are all unimplemented carries the pending tag
  (`@pending`), one covering an implemented story doesn't;
- a `Supersedes` link points to an existing story;
- the scenario delta matches the feature files: pending, the scenarios it
  changes or removes exist; ready on, the ones it adds too; implemented,
  added and changed exist and removed are gone.

Reference: docs/artifacts/story.md.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .config import STORY_STATES, Config
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
    errors.extend(_delta_trace_problems(config, stories, citations))
    return errors


def _delta_lines(config: Config, story: Story):
    """(operation, feature path as written, scenario name, exempt from the trace rule)."""
    body = section(story.text, config.stories.delta_heading)
    if body is None:
        return
    exemption = config.stories.delta_trace_exemption
    for match in _DELTA_LINE.finditer(body):
        scenario = match.group("scenario")
        exempt = bool(exemption) and exemption in scenario
        if exempt:
            scenario = scenario[: scenario.index(exemption)].rstrip()
        yield match.group("op"), match.group("feature"), scenario, exempt


def _delta_trace_problems(config: Config, stories: list[Story], citations: list[Citation]) -> list[str]:
    """A scenario a story adds (+, once ready) or changes (~, once
    implemented) asserts that story's criteria, so it carries its trace."""
    keys = config.stories
    cited = {(citation.story_id, citation.feature.resolve(), citation.scenario.name) for citation in citations}
    problems = []
    for story in stories:
        if is_legacy(config, story):
            continue
        story_id = story.get(keys.id_key)
        implemented = state_name(config, story) == "implemented"
        for operation, feature, scenario, exempt in _delta_lines(config, story):
            due = (operation == "+" and at_least(config, story, "ready")) or (operation == "~" and implemented)
            if not due or exempt:
                continue
            if (story_id, (config.project_root / feature).resolve(), scenario) not in cited:
                problems.append(
                    f"{story.path}: scenario delta {operation} {feature}: {scenario!r} has no {story_id} trace comment "
                    f"(a changed scenario that only renames can say {keys.delta_trace_exemption!r} on its delta line)"
                )
    return problems


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
    """Listed in `stories.legacy`: closed, or in flight, before the rules — left as it is."""
    return story.path.relative_to(config.project_root).as_posix() in config.stories.legacy


def implemented_under_rules(config: Config, story: Story) -> bool:
    keys = config.stories
    return (
        story.get(keys.state_key) == keys.states["implemented"]
        and not is_legacy(config, story)
        and (story.get(keys.date_key) or "") >= keys.rules_since
    )


def state_name(config: Config, story: Story) -> str | None:
    """The story's state as sanchin names it (`ready`, `in_progress`…), or None if unknown."""
    value = story.get(config.stories.state_key)
    return next((name for name, project_value in config.stories.states.items() if project_value == value), None)


def at_least(config: Config, story: Story, name: str) -> bool:
    """Whether the story has reached `name` in the order of STORY_STATES."""
    current = state_name(config, story)
    return current is not None and STORY_STATES.index(current) >= STORY_STATES.index(name)


def _technical(config: Config, story: Story) -> bool:
    return story.get(config.stories.kind_key) == config.stories.technical_kind


def _needs_scenarios(config: Config, story: Story) -> bool:
    """Refined and not yet closed, or closed under the rules: its scenarios are its spec.

    A legacy story — closed, or already in flight, when the project adopted
    sanchin — was refined before scenarios were part of refining."""
    if _technical(config, story) or is_legacy(config, story):
        return False
    return (at_least(config, story, "ready") and state_name(config, story) != "implemented") or implemented_under_rules(config, story)


def _story_problems(config: Config, story: Story) -> list[str]:
    keys = config.stories
    states = keys.states
    problems = []
    if not story.get(keys.id_key):
        problems.append(f"frontmatter has no {keys.id_key!r}")
    state = story.get(keys.state_key)
    name = state_name(config, story)
    if name is None:
        problems.append(f"{keys.state_key} {state!r} is not one of {list(states.values())}")
    legacy = is_legacy(config, story)
    if name == "implemented" and not legacy and not _ISO_DATE.fullmatch(story.get(keys.date_key) or ""):
        problems.append(f"a story {state!r} needs its {keys.date_key!r} as YYYY-MM-DD (or list it in stories.legacy)")
    problems.extend(_path_problems(config, story))
    if name in ("planned", "in_progress") or implemented_under_rules(config, story):
        if not story.get(keys.plan_key):
            problems.append(f"a story {state!r} needs its {keys.plan_key!r}; the tech-lead writes the plans")
    if _needs_scenarios(config, story) and not story.get(keys.scenarios_key):
        problems.append(f"a story {state!r} needs its {keys.scenarios_key!r}; refining it writes its scenarios")
    if at_least(config, story, "ready") and keys.doubt_marker in story.text:
        problems.append(f"unresolved {keys.doubt_marker!r} marker in a story {state!r}; resolve it in the functional grill")
    problems.extend(_milestone_problems(config, story))
    problems.extend(_supersedes_problems(config, story))
    problems.extend(_delta_problems(config, story))
    return problems


def _milestone_problems(config: Config, story: Story) -> list[str]:
    roadmap = config.roadmap
    milestone = story.get(config.stories.milestone_key)
    if roadmap is None:
        return []
    if milestone is None:
        if state_name(config, story) in ("ready", "planned", "in_progress"):
            return [f"a story {story.get(config.stories.state_key)!r} needs its {config.stories.milestone_key!r}: the roadmap places it"]
        return []
    if not (roadmap.directory / f"{milestone}.md").is_file():
        return [f"{config.stories.milestone_key} {milestone!r} names no milestone in {roadmap.directory}"]
    return []


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


def _delta_problems(config: Config, story: Story) -> list[str]:
    """Pending: what it changes or removes exists. Refined: what it adds is
    written too (tagged pending). Implemented: added and changed exist,
    removed are gone."""
    implemented = state_name(config, story) == "implemented"
    refined = at_least(config, story, "ready")
    problems = []
    for operation, written_feature, scenario, _exempt in _delta_lines(config, story):
        feature = config.project_root / written_feature
        present = scenario in scenario_names(feature)
        if implemented:
            expected_present = operation in "+~"
        elif operation == "+" and not refined:
            continue
        else:
            expected_present = True
        if present != expected_present:
            state = "should exist" if expected_present else "should be gone"
            problems.append(f"scenario delta {operation} {written_feature}: {scenario!r} {state}")
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
        if not _needs_scenarios(config, story) or not story.get(keys.scenarios_key):
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
    problems.extend(_pending_tag_problems(config, by_id, citations))
    return problems


def _pending_tag_problems(config: Config, by_id: dict, citations: list[Citation]) -> list[str]:
    """A scenario whose stories are all unimplemented is tagged pending, so CI
    doesn't run it before the code exists; one that covers an implemented
    story isn't, so CI does."""
    tag = config.scenarios.pending_tag
    if not tag:
        return []
    stories_of: dict[tuple, set[str]] = {}
    scenario_of = {}
    for citation in citations:
        key = (citation.feature, citation.scenario.line)
        stories_of.setdefault(key, set()).add(citation.story_id)
        scenario_of[key] = citation.scenario
    problems = []
    for key, story_ids in sorted(stories_of.items(), key=lambda item: (str(item[0][0]), item[0][1])):
        cited = [by_id[story_id] for story_id in sorted(story_ids) if story_id in by_id]
        if not cited:
            continue
        scenario = scenario_of[key]
        tagged = tag in scenario.tags
        implemented = [story.get(config.stories.id_key) for story in cited if state_name(config, story) == "implemented"]
        where = f"{key[0]}:{key[1]}: scenario {scenario.name!r}"
        if implemented and tagged:
            problems.append(f"{where} covers implemented {', '.join(implemented)} but is still tagged {tag}; drop the tag when its story closes")
        elif not implemented and not tagged:
            problems.append(f"{where} covers only unimplemented stories; tag it {tag} until they're implemented")
    return problems


def _paths(config: Config, story: Story, key: str) -> list[str]:
    return [path for path in (story.get(key) or "").split(config.stories.path_separator) if path]
