"""Plan rules: the minimum a plan needs at each state of its story.

For every plan a story links, when the story is in progress, or implemented
on or after `plans.rules_since` (plans listed in `plans.legacy` predate the
rules and are skipped):

- the sections `required_sections[<state>]` lists are present;
- the open-questions section has no open item left;
- with a constitution configured, the checklist section answers every
  constitution item with one of the allowed verdicts, and every exception
  (the last verdict in the list) names the plan decision that justifies it.

Reference: docs/artifacts.md#plan.
"""

import re
from pathlib import Path

from .config import Config
from .markdown import has_section, section
from .stories import Story

_OPEN_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\S", re.MULTILINE)
_DECISION_REFERENCE = re.compile(r"\bD-?\d+\b")


def check_plans(config: Config, stories: list[Story]) -> list[str]:
    constitution = constitution_items(config)
    errors = []
    for story in stories:
        state_name = _state_name(config, story)
        if state_name is None:
            continue
        for plan_path in _plan_paths(config, story):
            if plan_path.is_file():
                text = plan_path.read_text(encoding="utf-8")
                errors.extend(f"{plan_path}: {problem}" for problem in _plan_problems(config, text, state_name, constitution))
    return errors


def constitution_items(config: Config) -> list[str]:
    items: set[str] = set()
    for pattern in config.plans.constitution_globs:
        items.update(path.stem for path in config.project_root.glob(pattern) if path.is_file() and path.name != "index.md")
    return sorted(items)


def _state_name(config: Config, story: Story) -> str | None:
    keys = config.stories
    state = story.get(keys.state_key)
    if state == keys.states["in_progress"]:
        return "in_progress"
    if state == keys.states["implemented"] and (story.get(keys.date_key) or "") >= config.plans.rules_since:
        return "implemented"
    return None


def _plan_paths(config: Config, story: Story) -> list[Path]:
    raw = story.get(config.stories.plan_key) or ""
    return [
        config.project_root / path
        for path in raw.split(config.stories.path_separator)
        if path and path not in config.plans.legacy
    ]


def _plan_problems(config: Config, text: str, state_name: str, constitution: list[str]) -> list[str]:
    plans = config.plans
    problems = [
        f"missing section {name!r}, required while the story is {state_name.replace('_', ' ')}"
        for name in plans.required_sections.get(state_name, ())
        if not has_section(text, name)
    ]
    open_questions = section(text, plans.open_questions_section)
    if open_questions is not None and _OPEN_ITEM.search(open_questions):
        problems.append(f"{plans.open_questions_section!r} still has open items; close them in the technical grill")
    if constitution:
        problems.extend(_constitution_problems(config, text, constitution))
    return problems


def _constitution_problems(config: Config, text: str, constitution: list[str]) -> list[str]:
    plans = config.plans
    checklist = section(text, plans.constitution_section)
    if checklist is None:
        return [f"missing section {plans.constitution_section!r}"]
    problems = []
    for item in constitution:
        line = re.search(rf"^\s*[-*]\s+`?{re.escape(item)}`?\s*:\s*(?P<verdict>.+)$", checklist, re.MULTILINE)
        if line is None:
            problems.append(f"{plans.constitution_section!r} does not answer {item!r}")
            continue
        verdict = line.group("verdict").strip()
        if not verdict.lower().startswith(tuple(plans.constitution_verdicts)):
            problems.append(f"{item!r}: verdict {verdict!r} is not one of {list(plans.constitution_verdicts)}")
        elif verdict.lower().startswith(plans.constitution_verdicts[-1]) and not _DECISION_REFERENCE.search(verdict):
            problems.append(f"{item!r}: an exception must name the decision that justifies it (D-n)")
    return problems
