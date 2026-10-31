"""Progressive-context rules: references, links, navigation and indexes.

- `file.ext:NNN` citations point to an existing source file with that line;
- relative markdown links resolve;
- every document under the docs root except its entry index has a
  navigation line below its title;
- every directory with more than one document has an `index.md` that links
  each of its documents and child indexes (catalogs the adapter lists as
  generated elsewhere are exempt).

Reference: docs/context.md and docs/validator.md.
"""

import re
from pathlib import Path

from .config import Config
from .markdown import line_number, relative_links, strip_frontmatter

_REFERENCE_PATTERN = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?`")
_NAVIGATION_SEARCH_LINES = 15


def check_docs(config: Config, target: Path | None = None) -> list[str]:
    """All doc rules over the docs root, or only the per-file ones over `target`."""
    markdown_files = [target] if target is not None else sorted(config.docs.root.rglob("*.md"))
    source_files = find_source_files(config)
    errors = [error for path in markdown_files for error in check_markdown_file(config, path, source_files)]
    if target is None:
        errors.extend(check_indexes(config))
    return errors


def find_source_files(config: Config) -> list[Path]:
    files: set[Path] = set()
    for pattern in config.docs.code_reference_globs:
        files.update(
            path
            for path in config.project_root.glob(pattern)
            if path.is_file() and not {"__pycache__", ".venv", "node_modules"} & set(path.parts)
        )
    return sorted(files)


def check_markdown_file(config: Config, markdown_path: Path, source_files: list[Path]) -> list[str]:
    text = markdown_path.read_text(encoding="utf-8")
    return (
        _check_code_references(markdown_path, text, source_files)
        + _check_links(markdown_path, text)
        + _check_navigation(config, markdown_path, text)
    )


def check_indexes(config: Config) -> list[str]:
    root = config.docs.root
    directories = sorted({path.parent for path in root.rglob("*.md")} | {root})
    return [error for directory in directories for error in _check_directory_index(config, directory)]


def _check_code_references(markdown_path: Path, text: str, source_files: list[Path]) -> list[str]:
    checked_suffixes = {path.suffix for path in source_files}
    errors = []
    for match in _REFERENCE_PATTERN.finditer(text):
        reference_path = match.group(1)
        if Path(reference_path).suffix not in checked_suffixes:
            continue
        last_line = int(match.group(3) or match.group(2))
        matching_files = [path for path in source_files if _same_file(path, reference_path)]
        problem = _reference_problem(reference_path, last_line, matching_files)
        if problem is not None:
            errors.append(f"{markdown_path}:{line_number(text, match.start())}: {problem}")
    return errors


def _same_file(path: Path, reference_path: str) -> bool:
    """`a.py` names `src/a.py` but not `src/data.py`: match whole path segments."""
    full = path.as_posix()
    reference = reference_path.removeprefix("./")
    return full == reference or full.endswith("/" + reference)


def _reference_problem(reference_path: str, last_line: int, matching_files: list[Path]) -> str | None:
    if not matching_files:
        return f"path not found: {reference_path}"
    if all(last_line > len(path.read_text(encoding="utf-8").splitlines()) for path in matching_files):
        return f"line {last_line} out of range for {reference_path} (checked {len(matching_files)} match(es))"
    return None


def _check_links(markdown_path: Path, text: str) -> list[str]:
    return [
        f"{markdown_path}:{line_number(text, offset)}: broken link {target}"
        for target, offset in relative_links(markdown_path, text)
        if not (markdown_path.parent / target.split("#", 1)[0]).exists()
    ]


def _check_navigation(config: Config, markdown_path: Path, text: str) -> list[str]:
    resolved = markdown_path.resolve()
    if not resolved.is_relative_to(config.docs.root.resolve()) or resolved == config.docs.index.resolve():
        return []
    navigation = re.compile(config.docs.navigation_line)
    first_lines = strip_frontmatter(text).splitlines()[:_NAVIGATION_SEARCH_LINES]
    if any(navigation.match(line) for line in first_lines):
        return []
    return [f"{markdown_path}:1: missing navigation line below the title"]


def _check_directory_index(config: Config, directory: Path) -> list[str]:
    documents = sorted(path for path in directory.glob("*.md") if path.name != "index.md")
    child_indexes = sorted(child / "index.md" for child in directory.iterdir() if (child / "index.md").is_file())
    index_path = directory / "index.md"
    if not index_path.is_file():
        if len(documents) > 1 and directory.name not in config.docs.unindexed_catalogs:
            return [f"{directory}: {len(documents)} documents and no index.md"]
        return []
    text = index_path.read_text(encoding="utf-8")
    linked = {(index_path.parent / target.split("#", 1)[0]).resolve() for target, _ in relative_links(index_path, text)}
    return [
        f"{index_path}: does not link {entry.relative_to(directory)}"
        for entry in documents + child_indexes
        if entry.resolve() not in linked
    ]
