"""Command line: `sanchin check`, `sanchin superseded`, `sanchin gates`, `sanchin hook`.

Run it through `scripts/sanchin`, which finds a Python with PyYAML.
Reference: docs/validator.md.
"""

import argparse
import json
import sys
from pathlib import Path

from .config import AdapterError, Config, load_config
from .docs import check_docs
from .gates import run_gates
from .plans import check_plans
from .scenarios import citations, feature_files
from .stories import SUPERSEDED_END, SUPERSEDED_START, check_stories, load_stories, render_superseded_block

CHECKS = ("docs", "stories", "plans")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    project_root = Path(arguments.project).resolve()
    try:
        config = load_config(project_root, Path(arguments.adapter).resolve() if arguments.adapter else None)
    except AdapterError as error:
        if arguments.handler is run_hook:
            return 0
        print(f"sanchin: {error}", file=sys.stderr)
        return 2
    return arguments.handler(config, arguments)


def run_check(config: Config, arguments) -> int:
    selected = arguments.only or list(CHECKS)
    errors = collect_errors(config, selected, Path(arguments.file).resolve() if arguments.file else None)
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print(f"sanchin: {', '.join(selected)} OK")
    return 1 if errors else 0


def collect_errors(config: Config, selected: list[str], target: Path | None = None) -> list[str]:
    errors = []
    if "docs" in selected:
        errors.extend(check_docs(config, target))
    if target is not None:
        return errors
    if "stories" in selected or "plans" in selected:
        stories, load_errors = load_stories(config)
        errors.extend(load_errors)
        if "stories" in selected:
            errors.extend(check_stories(config, stories, citations(config, feature_files(config))))
            errors.extend(_superseded_index_problems(config, stories))
        if "plans" in selected:
            errors.extend(check_plans(config, stories))
    return errors


def run_superseded(config: Config, arguments) -> int:
    stories, _ = load_stories(config)
    block = render_superseded_block(config, stories)
    index = config.stories.superseded_index
    if not arguments.write or index is None:
        print(block)
        return 0
    text = index.read_text(encoding="utf-8")
    start, end = SUPERSEDED_START, SUPERSEDED_END
    if start not in text or end not in text:
        print(f"sanchin: {index} has no {start} … {end} block", file=sys.stderr)
        return 1
    index.write_text(text[: text.index(start)] + block + text[text.index(end) + len(end) :], encoding="utf-8")
    print(f"sanchin: wrote superseded-by table to {index}")
    return 0


def run_gates_command(config: Config, arguments) -> int:
    failures = [failure for file in arguments.files for failure in run_gates(config, file, arguments.level)]
    for failure in failures:
        print(f"{failure.file}: gate {failure.gate} failed\n{failure.output}", file=sys.stderr)
    return 1 if failures else 0


def run_hook(config: Config, _arguments) -> int:
    """PostToolUse hook: doc rules on edited docs, then the edit-level gates."""
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path") or payload.get("tool_response", {}).get("filePath")
    if not file_path:
        return 0
    absolute = Path(file_path).resolve()
    if not absolute.is_relative_to(config.project_root):
        return 0
    relative = absolute.relative_to(config.project_root).as_posix()
    problems = []
    if absolute.suffix == ".md" and absolute.is_relative_to(config.docs.root.resolve()) and absolute.is_file():
        problems.extend(check_docs(config, absolute))
    problems.extend(f"gate {failure.gate} failed:\n{failure.output}" for failure in run_gates(config, relative, "edit"))
    if problems:
        print(json.dumps({"decision": "block", "reason": f"sanchin found problems in {relative}:\n" + "\n".join(problems)}))
    return 0


def _superseded_index_problems(config: Config, stories) -> list[str]:
    index = config.stories.superseded_index
    if index is None:
        return []
    if not index.is_file():
        return [f"{index}: superseded index does not exist"]
    text = index.read_text(encoding="utf-8")
    if render_superseded_block(config, stories) not in text:
        return [f"{index}: superseded-by table is stale; run `sanchin superseded --write`"]
    return []


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sanchin", description="Validate a project's process artifacts against its sanchin adapter.")
    parser.add_argument("--project", default=".", help="project root holding .claude/sanchin.yaml (default: current directory)")
    parser.add_argument("--adapter", help="adapter file to use instead of <project>/.claude/sanchin.yaml")
    commands = parser.add_subparsers(required=True)

    check = commands.add_parser("check", help="run the process rules")
    check.add_argument("--only", action="append", choices=CHECKS, help="limit to one group of rules (repeatable)")
    check.add_argument("--file", help="check a single markdown file (per-file doc rules only)")
    check.set_defaults(handler=run_check)

    superseded = commands.add_parser("superseded", help="print or write the generated superseded-by table")
    superseded.add_argument("--write", action="store_true", help="rewrite the block in stories.superseded_index")
    superseded.set_defaults(handler=run_superseded)

    gates = commands.add_parser("gates", help="run the project's gates of one level over some files")
    gates.add_argument("--level", default="pre-commit", choices=("edit", "pre-commit", "pre-push", "ci"))
    gates.add_argument("files", nargs="+")
    gates.set_defaults(handler=run_gates_command)

    hook = commands.add_parser("hook", help="PostToolUse hook entry point (reads the hook payload on stdin)")
    hook.set_defaults(handler=run_hook)
    return parser
