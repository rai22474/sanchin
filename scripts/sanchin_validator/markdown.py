"""Small, dependency-free readers for the markdown the process produces."""

import re
from pathlib import Path

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")
_FENCE_PATTERN = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
_CODE_SPAN_PATTERN = re.compile(r"`[^`\n]*`")
_FRONTMATTER_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, list[str]]:
    """Flat `key: value` frontmatter, the shape every sanchin artifact uses."""
    if not text.startswith("---\n"):
        return None, ["missing frontmatter"]
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, ["unterminated frontmatter"]
    fields: dict[str, str] = {}
    errors = []
    for line in text[4:end].split("\n"):
        key, separator, value = line.partition(":")
        key = key.strip()
        if not separator or not _FRONTMATTER_KEY.fullmatch(key) or not value.strip():
            errors.append(f"malformed frontmatter line {line!r}")
            continue
        if key in fields:
            errors.append(f"duplicated key {key!r}")
        fields[key] = value.strip()
    return fields, errors


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    closing = text.find("\n---\n", 4)
    return text if closing == -1 else text[closing + 5 :]


def section(text: str, heading: str) -> str | None:
    """Body of the first `##`-or-deeper heading whose title starts with `heading`.

    Numbered headings (`## 3. Design`) match by their title without the number.
    """
    pattern = re.compile(
        rf"^(#{{2,6}})\s+(?:\d+(?:\.\d+)*\.?\s+)?{re.escape(heading)}\b[^\n]*\n(.*?)(?=^#{{2,6}}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(2) if match else None


def has_section(text: str, heading: str) -> bool:
    return section(text, heading) is not None


def blank_code(text: str) -> str:
    """Replace fenced blocks and code spans with spaces, keeping offsets."""
    without_fences = _FENCE_PATTERN.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), text)
    return _CODE_SPAN_PATTERN.sub(lambda match: " " * len(match.group(0)), without_fences)


def relative_links(markdown_path: Path, text: str) -> list[tuple[str, int]]:
    """Relative link targets in prose, with the offset where each starts."""
    prose = blank_code(text)
    return [
        (match.group(1), match.start())
        for match in LINK_PATTERN.finditer(prose)
        if not match.group(1).startswith(EXTERNAL_PREFIXES)
    ]


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1
