"""Read executable scenarios: their names and the criteria each one cites.

Feature files are read with the official Gherkin parser, so every language
Gherkin supports (`# language: fr`, …), rules, outlines and backgrounds are
understood the way the test runner understands them. A feature file that
doesn't parse is an error: a scenario that can't parse can't be red for the
right reason.
"""

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .config import AdapterError, Config


@dataclass(frozen=True)
class Citation:
    story_id: str
    criterion: int
    feature: Path
    scenario: "Scenario"


@dataclass(frozen=True)
class Scenario:
    name: str
    line: int
    tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ParsedFeature:
    scenarios: tuple[Scenario, ...]
    error: str | None


def feature_files(config: Config) -> list[Path]:
    files: set[Path] = set()
    for pattern in config.scenarios.globs:
        files.update(path for path in config.project_root.glob(pattern) if path.is_file())
    return sorted(files)


def citations(config: Config, features: list[Path]) -> tuple[list[Citation], list[str]]:
    """Trace comments in the feature files, and the problems found reading them.

    A trace comment counts only when the next line that isn't blank, a
    comment or a tag is a scenario: a loose comment covers nothing.
    """
    comment = re.compile(config.scenarios.trace_comment)
    found, problems = [], []
    for feature in features:
        parsed = parse_feature(feature)
        if parsed.error is not None:
            problems.append(f"{feature}: does not parse as Gherkin: {parsed.error}")
            continue
        by_line = {scenario.line: scenario for scenario in parsed.scenarios}
        lines = feature.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            match = comment.match(line)
            if match is None:
                continue
            scenario = by_line.get(_next_content_line(lines, index + 1))
            if scenario is None:
                problems.append(f"{feature}:{index + 1}: trace comment is not above a scenario")
                continue
            for number in re.split(r",\s*", match.group("criteria").strip()):
                found.append(Citation(match.group("story"), int(number), feature, scenario))
    return found, problems


def scenario_names(feature: Path) -> set[str]:
    if not feature.is_file():
        return set()
    return {scenario.name for scenario in parse_feature(feature).scenarios}


def parse_feature(feature: Path) -> ParsedFeature:
    return _parse(feature.resolve(), feature.stat().st_mtime_ns)


@lru_cache(maxsize=None)
def _parse(feature: Path, _mtime: int) -> ParsedFeature:
    try:
        from gherkin.parser import Parser
        from gherkin.token_scanner import TokenScanner
    except ImportError as error:
        raise AdapterError(
            "the Gherkin parser (gherkin-official) is not available; run the validator through scripts/sanchin, which provides it"
        ) from error
    try:
        document = Parser().parse(TokenScanner(feature.read_text(encoding="utf-8")))
    except Exception as error:  # the parser raises its own composite exception types
        return ParsedFeature((), " ".join(str(error).split()))
    return ParsedFeature(tuple(_scenarios(document.get("feature") or {}, frozenset())), None)


def _scenarios(node: dict, inherited: frozenset[str]):
    """Scenarios under a feature or rule, each with the tags it inherits."""
    tags = inherited | {tag["name"] for tag in node.get("tags", [])}
    for child in node.get("children", []):
        if "scenario" in child:
            scenario = child["scenario"]
            own = {tag["name"] for tag in scenario.get("tags", [])}
            yield Scenario(scenario["name"], scenario["location"]["line"], frozenset(tags | own))
        elif "rule" in child:
            yield from _scenarios(child["rule"], tags)


def _next_content_line(lines: list[str], start: int) -> int | None:
    """1-based number of the first line from `start` that isn't blank, a comment or a tag."""
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith(("#", "@")):
            return index + 1
    return None
