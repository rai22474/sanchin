"""Load and check the project adapter, `.claude/sanchin.yaml`.

The adapter is the only place a project says where its artifacts live and
how it names them. Every rule in the validator reads its values from here,
so nothing in the validator knows about a particular project.
Reference: docs/adapter.md.
"""

from dataclasses import dataclass, field
from pathlib import Path

ADAPTER_PATH = Path(".claude") / "sanchin.yaml"
SUPPORTED_VERSION = 1


class AdapterError(Exception):
    pass


class MissingAdapterError(AdapterError):
    """The project has no adapter: it doesn't use sanchin."""


@dataclass(frozen=True)
class DocsConfig:
    root: Path
    index: Path
    navigation_line: str
    unindexed_catalogs: tuple[str, ...]
    code_reference_globs: tuple[str, ...]


@dataclass(frozen=True)
class StoriesConfig:
    directory: Path
    glob: str
    id_key: str
    state_key: str
    date_key: str
    plan_key: str
    scenarios_key: str
    kind_key: str
    milestone_key: str
    technical_kind: str
    path_separator: str
    states: dict[str, str]
    criteria_heading: str
    criterion_exemption: str
    doubt_marker: str
    supersedes_pattern: str
    superseded_index: Path | None
    delta_heading: str
    rules_since: str
    legacy: tuple[str, ...]


@dataclass(frozen=True)
class ScenariosConfig:
    globs: tuple[str, ...]
    trace_comment: str
    pending_tag: str


@dataclass(frozen=True)
class PlansConfig:
    directory: Path
    required_sections: dict[str, tuple[str, ...]]
    open_questions_section: str
    constitution_section: str
    constitution_globs: tuple[str, ...]
    constitution_verdicts: tuple[str, ...]
    rules_since: str
    legacy: tuple[str, ...]


@dataclass(frozen=True)
class RoadmapConfig:
    """The milestone layer: the roadmap is a set of milestones holding stories."""

    directory: Path
    glob: str
    state_pattern: str
    states: dict[str, str]


@dataclass(frozen=True)
class Gate:
    name: str
    glob: str
    run: str
    level: str
    timeout: int = 120


GATE_LEVELS = ("edit", "pre-commit", "pre-push", "ci")
MERGE_MODES = ("local", "pr")


@dataclass(frozen=True)
class Config:
    project_root: Path
    language: str
    terms: dict[str, str]
    layers: tuple[str, ...]
    components: tuple[str, ...]
    docs: DocsConfig
    stories: StoriesConfig
    scenarios: ScenariosConfig
    plans: PlansConfig
    roadmap: "RoadmapConfig | None" = None
    gates: tuple[Gate, ...] = field(default_factory=tuple)


def load_config(project_root: Path, adapter_file: Path | None = None) -> Config:
    adapter_file = adapter_file or project_root / ADAPTER_PATH
    if not adapter_file.is_file():
        raise MissingAdapterError(f"{adapter_file}: no adapter; run /sanchin:init to create one")
    raw = _parse_yaml(adapter_file)
    return build_config(project_root, raw)


def build_config(project_root: Path, raw: dict) -> Config:
    if raw.get("version") != SUPPORTED_VERSION:
        raise AdapterError(f"adapter version {raw.get('version')!r} is not supported (expected {SUPPORTED_VERSION})")
    components = tuple(raw.get("components", []))
    if raw.get("merge", "local") not in MERGE_MODES:
        raise AdapterError(f"merge {raw.get('merge')!r} is not one of {list(MERGE_MODES)}")
    return Config(
        project_root=project_root,
        language=raw.get("language", "en"),
        terms=dict(raw.get("terms", {})),
        layers=tuple(raw.get("layers", [])),
        components=components,
        docs=_docs_config(project_root, _section(raw, "docs"), components),
        stories=_stories_config(project_root, _section(raw, "stories")),
        scenarios=_scenarios_config(_section(raw, "scenarios"), components),
        plans=_plans_config(project_root, _section(raw, "plans"), components),
        roadmap=_roadmap_config(project_root, raw),
        gates=tuple(_gate(entry) for entry in raw.get("gates", [])),
    )


def expand_components(patterns, components: tuple[str, ...]) -> tuple[str, ...]:
    expanded = []
    for pattern in patterns:
        if "{component}" in pattern:
            expanded.extend(pattern.replace("{component}", component) for component in components)
        else:
            expanded.append(pattern)
    return tuple(expanded)


def _docs_config(project_root: Path, raw: dict, components: tuple[str, ...]) -> DocsConfig:
    root = project_root / _required(raw, "docs", "root")
    return DocsConfig(
        root=root,
        index=project_root / raw.get("index", f"{_required(raw, 'docs', 'root')}/index.md"),
        navigation_line=raw.get("navigation_line", r"^\[[^\]]+\]\("),
        unindexed_catalogs=tuple(raw.get("unindexed_catalogs", [])),
        code_reference_globs=expand_components(raw.get("code_reference_globs", []), components),
    )


def _stories_config(project_root: Path, raw: dict) -> StoriesConfig:
    keys = raw.get("keys", {})
    superseded_index = raw.get("superseded_index")
    return StoriesConfig(
        directory=project_root / _required(raw, "stories", "directory"),
        glob=raw.get("glob", "*.md"),
        id_key=keys.get("id", "id"),
        state_key=keys.get("state", "state"),
        date_key=keys.get("date", "date"),
        plan_key=keys.get("plan", "plan"),
        scenarios_key=keys.get("scenarios", "scenarios"),
        kind_key=keys.get("kind", "kind"),
        milestone_key=keys.get("milestone", "milestone"),
        technical_kind=raw.get("technical_kind", "technical"),
        path_separator=raw.get("path_separator", ", "),
        states=_states(raw.get("states", {})),
        criteria_heading=raw.get("criteria_heading", "Acceptance criteria"),
        criterion_exemption=raw.get("criterion_exemption", "(no scenario:"),
        doubt_marker=raw.get("doubt_marker", "[DOUBT:"),
        supersedes_pattern=raw.get("supersedes_pattern", r"\*\*Supersedes:\*\*[^\n]*?\]\(([^)\s]+)\)"),
        superseded_index=project_root / superseded_index if superseded_index else None,
        delta_heading=raw.get("delta_heading", "Scenario delta"),
        rules_since=str(raw.get("rules_since", "0000-00-00")),
        legacy=tuple(raw.get("legacy", [])),
    )


def _scenarios_config(raw: dict, components: tuple[str, ...]) -> ScenariosConfig:
    return ScenariosConfig(
        globs=expand_components(raw.get("globs", ["**/*.feature"]), components),
        trace_comment=raw.get(
            "trace_comment",
            r"^\s*#\s*(?P<story>[A-Z]+-[A-Z0-9]+):\s*(?:AC|CA)\s+(?P<criteria>\d+(?:,\s*\d+)*)\s*$",
        ),
        # '' turns the rule off, for a project whose runner can't exclude a tag.
        pending_tag=str(raw.get("pending_tag", "@pending")),
    )


def _plans_config(project_root: Path, raw: dict, components: tuple[str, ...]) -> PlansConfig:
    required = raw.get("required_sections", {})
    constitution = raw.get("constitution", {})
    return PlansConfig(
        directory=project_root / _required(raw, "plans", "directory"),
        required_sections={state: tuple(sections) for state, sections in required.items()},
        open_questions_section=raw.get("open_questions_section", "Open questions"),
        constitution_section=constitution.get("section", "Constitution checklist"),
        # Kept unexpanded: `{component}` resolves per plan (see plans.py).
        constitution_globs=tuple(constitution.get("globs", [])),
        constitution_verdicts=tuple(verdict.lower() for verdict in constitution.get("verdicts", ["n/a", "ok", "exception"])),
        rules_since=str(raw.get("rules_since", "0000-00-00")),
        legacy=tuple(raw.get("legacy", [])),
    )


def _gate(entry: dict) -> Gate:
    for key in ("name", "glob", "run"):
        if key not in entry:
            raise AdapterError(f"gate {entry!r} has no {key!r}")
    level = entry.get("level", "edit")
    if level not in GATE_LEVELS:
        raise AdapterError(f"gate {entry['name']!r} has level {level!r}; allowed: {list(GATE_LEVELS)}")
    timeout = entry.get("timeout", 120)
    if not isinstance(timeout, int) or timeout <= 0:
        raise AdapterError(f"gate {entry['name']!r} has timeout {timeout!r}; it must be a positive number of seconds")
    return Gate(name=entry["name"], glob=entry["glob"], run=entry["run"], level=level, timeout=timeout)


STORY_STATES = ("pending", "ready", "planned", "in_progress", "implemented")
MILESTONE_STATES = ("planned", "in_progress", "closed")


def _states(raw: dict) -> dict[str, str]:
    """Story states in the order a story goes through them (docs/process/states.md)."""
    return _named_values("stories.states", raw, STORY_STATES)


def _named_values(where: str, raw: dict, names: tuple[str, ...]) -> dict[str, str]:
    values = {name: name.replace("_", " ") for name in names}
    unknown = set(raw) - set(values)
    if unknown:
        raise AdapterError(f"{where} has unknown keys {sorted(unknown)}; allowed: {list(names)}")
    values.update({name: str(value) for name, value in raw.items()})
    if len(set(values.values())) != len(values):
        raise AdapterError(f"{where} gives two states the same value: {values}")
    return values


def _roadmap_config(project_root: Path, raw: dict) -> RoadmapConfig | None:
    if "milestone" not in raw.get("layers", []):
        return None
    section = _section(raw, "roadmap")
    return RoadmapConfig(
        directory=project_root / _required(section, "roadmap", "directory"),
        glob=section.get("glob", "*.md"),
        state_pattern=section.get("state_pattern", r"^\*\*State:\*\*\s*(?P<state>[^.\n]+?)\s*\.?\s*$"),
        states=_named_values("roadmap.states", section.get("states", {}), MILESTONE_STATES),
    )


def _section(raw: dict, name: str) -> dict:
    section = raw.get(name)
    if not isinstance(section, dict):
        raise AdapterError(f"adapter has no {name!r} section")
    return section


def _required(raw: dict, section: str, key: str) -> str:
    if key not in raw:
        raise AdapterError(f"adapter section {section!r} has no {key!r}")
    return raw[key]


def _parse_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError as error:
        raise AdapterError("PyYAML is not available; run the validator through scripts/sanchin, which provides it") from error
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AdapterError(f"{path}: the adapter must be a YAML mapping")
    return data
