"""Read executable scenarios: their names and the criteria each one cites."""

import re
from dataclasses import dataclass
from pathlib import Path

from .config import Config

_SCENARIO_LINE = re.compile(
    r"^\s*(?:Scenario Outline|Scenario Template|Scenario|Example|Escenario|Esquema del escenario|Ejemplo):\s*(?P<name>.+?)\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Citation:
    story_id: str
    criterion: int
    feature: Path


def feature_files(config: Config) -> list[Path]:
    files: set[Path] = set()
    for pattern in config.scenarios.globs:
        files.update(path for path in config.project_root.glob(pattern) if path.is_file())
    return sorted(files)


def citations(config: Config, features: list[Path]) -> list[Citation]:
    comment = re.compile(config.scenarios.trace_comment, re.MULTILINE)
    found = []
    for feature in features:
        for match in comment.finditer(feature.read_text(encoding="utf-8")):
            for number in re.split(r",\s*", match.group("criteria").strip()):
                found.append(Citation(match.group("story"), int(number), feature))
    return found


def scenario_names(feature: Path) -> set[str]:
    if not feature.is_file():
        return set()
    return {match.group("name") for match in _SCENARIO_LINE.finditer(feature.read_text(encoding="utf-8"))}
