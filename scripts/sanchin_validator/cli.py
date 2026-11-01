"""Command line: `sanchin check`, `roadmap`, `superseded`, `gates`, `git-hook`, `trust`, `hook`, `prompt-hook`.

Run it through `scripts/sanchin`, which finds a Python with PyYAML.
Reference: docs/validator.md.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

from .config import AdapterError, Config, MissingAdapterError, load_config
from .docs import check_docs
from .gates import gates_for, run_gates
from .trust import is_trusted, repository_key, trust

TRUST_COMMAND = shlex.quote(str(Path(__file__).resolve().parents[1] / "sanchin"))
from .immutability import immutability_problems
from .plans import check_plans
from .roadmap import roadmap_problems, write_blocks
from .scenarios import citations, feature_files
from .stories import SUPERSEDED_END, SUPERSEDED_START, check_stories, load_stories, render_superseded_block

CHECKS = ("docs", "stories", "plans")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    if arguments.handler in (run_hook, run_prompt_hook):
        return arguments.handler(arguments)
    project_root = Path(arguments.project).resolve()
    try:
        config = load_config(project_root, Path(arguments.adapter).resolve() if arguments.adapter else None)
    except AdapterError as error:
        print(f"sanchin: {error}", file=sys.stderr)
        return 2
    try:
        return arguments.handler(config, arguments)
    except AdapterError as error:  # e.g. a parser the run needs is missing
        print(f"sanchin: {error}", file=sys.stderr)
        return 2


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
            found, trace_problems = citations(config, feature_files(config))
            errors.extend(trace_problems)
            errors.extend(check_stories(config, stories, found))
            errors.extend(immutability_problems(config, stories))
            errors.extend(roadmap_problems(config, stories))
            errors.extend(_superseded_index_problems(config, stories))
        if "plans" in selected:
            errors.extend(check_plans(config, stories))
    return errors


def run_roadmap(config: Config, arguments) -> int:
    if config.roadmap is None:
        print("sanchin: the milestone layer is off (add `milestone` to `layers` and a `roadmap` section)", file=sys.stderr)
        return 2
    stories, _ = load_stories(config)
    if arguments.write:
        problems = write_blocks(config, stories)
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems:
            return 1
    problems = roadmap_problems(config, stories)
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print("sanchin: roadmap OK")
    return 1 if problems else 0


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
    relative_files = [_relative_to_project(config, file) for file in arguments.files]
    failures = run_gates(config, relative_files, arguments.level)
    for failure in failures:
        print(f"{failure.file}: gate {failure.gate} failed\n{failure.output}", file=sys.stderr)
    return 1 if failures else 0


def run_hook(arguments) -> int:
    """PostToolUse hook: doc rules on edited docs, then the edit-level gates.

    The project is the git working tree that holds the edited file, not the
    directory the session started in: a story runs in its own worktree, and
    that worktree's adapter, docs and cwd are the ones that apply.
    """
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path") or payload.get("tool_response", {}).get("filePath")
    if not file_path:
        return 0
    absolute = Path(file_path).resolve()
    project_root = _working_tree(absolute) or Path(arguments.project).resolve()
    if not absolute.is_relative_to(project_root):
        return 0
    try:
        config = load_config(project_root)
    except MissingAdapterError:
        return 0  # a project, or a branch, that doesn't use sanchin
    except AdapterError as error:
        # Exit 1 is a non-blocking error the user sees: the gates are off
        # until the adapter is fixed, and that must not be silent.
        print(f"sanchin: {error}", file=sys.stderr)
        return 1
    relative = absolute.relative_to(config.project_root).as_posix()
    problems = []
    if absolute.suffix == ".md" and absolute.is_relative_to(config.docs.root.resolve()) and absolute.is_file():
        problems.extend(check_docs(config, absolute))
    output = {}
    has_gates = bool(gates_for(config, relative, "edit"))
    if has_gates and is_trusted(config):
        problems.extend(f"gate {failure.gate} failed:\n{failure.output}" for failure in run_gates(config, [relative], "edit"))
    elif has_gates:
        # Shown to the user, not to Claude: approving commands is the user's call.
        output["systemMessage"] = (
            "sanchin: this repository's gates are not trusted, so they did not run. "
            "To review and approve them, run /sanchin:trust in Claude Code "
            f"(or, from a shell, `scripts/sanchin trust` — or `{TRUST_COMMAND} --project "
            f"{shlex.quote(str(config.project_root))} trust` if the project has no wrapper)."
        )
    if problems:
        output.update(decision="block", reason=f"sanchin found problems in {relative}:\n" + "\n".join(problems))
    if output:
        print(json.dumps(output))
    return 0


# The roles that run a cycle of their own (docs/process/working-rules.md#one-session-per-cycle).
CYCLE_ROLES = ("product-owner", "tech-lead", "developer", "architect", "maintainer", "coach")
ROLE_COMMAND = re.compile(r"^\s*/sanchin:(?P<role>[a-z-]+)\b")
RAN_ROLE = re.compile(r"<command-name>/sanchin:(?P<role>[a-z-]+)</command-name>")


def run_prompt_hook(arguments) -> int:
    """UserPromptSubmit hook: a role's cycle starts in a session no other role has used.

    Roles hand over through artifacts, not the chat; a session that carries
    an earlier cycle re-reads it on every call. The adapter's
    `session.fresh_per_cycle` says whether to block the prompt, warn, or
    stay silent.
    """
    payload = json.load(sys.stdin)
    match = ROLE_COMMAND.match(payload.get("prompt") or "")
    if not match or match.group("role") not in CYCLE_ROLES:
        return 0
    role = match.group("role")
    earlier = _roles_in_transcript(payload.get("transcript_path"))
    others = sorted(set(earlier) - {role})
    if not others:
        return 0
    cwd = Path(payload.get("cwd") or arguments.project).resolve()
    project_root = _working_tree(cwd / "prompt") or Path(arguments.project).resolve()
    try:
        mode = load_config(project_root).fresh_per_cycle
    except AdapterError:
        return 0
    message = (
        f"sanchin: this session already ran /sanchin:{', /sanchin:'.join(others)}. "
        f"Start /sanchin:{role} in a fresh session — run /clear, then the command again. "
        "Roles hand over through the artifacts on main, not the chat, and a session "
        "that carries earlier cycles pays for them on every call "
        "(session.fresh_per_cycle in .claude/sanchin.yaml: block | warn | off)."
    )
    if mode == "block":
        print(json.dumps({"decision": "block", "reason": message}))
    elif mode == "warn":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "Before anything else, tell the user, in one line: " + message,
        }}))
    return 0


def _roles_in_transcript(transcript_path: str | None) -> list[str]:
    """The /sanchin: roles the user invoked earlier in this session."""
    if not transcript_path or not Path(transcript_path).is_file():
        return []
    roles = []
    for line in Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "user":
            continue
        content = (entry.get("message") or {}).get("content")
        texts = [content] if isinstance(content, str) else [part.get("text", "") for part in content or [] if isinstance(part, dict)]
        for text in texts:
            roles.extend(found.group("role") for found in RAN_ROLE.finditer(text or "") if found.group("role") in CYCLE_ROLES)
    return roles


ZERO_SHA = "0" * 40


def run_git_hook(config: Config, arguments) -> int:
    """Entry point for a git hook: the gates of its level over the files it concerns.

    pre-commit: the staged files. pre-push: the files of every commit being
    pushed that no remote has yet (from the refs git passes on stdin, or
    HEAD), then the full `check`. Files are read from the working tree.
    """
    if arguments.level == "pre-commit":
        files = _git_lines(config, "diff", "--cached", "--relative", "--name-only", "--diff-filter=ACMR")
    else:
        tips = [line.split()[1] for line in _stdin_lines() if len(line.split()) == 4 and line.split()[1] != ZERO_SHA]
        files = _git_lines(config, "log", "--format=", "--relative", "--name-only", "--diff-filter=ACMR", *(tips or ["HEAD"]), "--not", "--remotes")
    if files is None:
        print("sanchin: git-hook needs a git repository", file=sys.stderr)
        return 2
    existing = sorted({file for file in files if (config.project_root / file).is_file()})
    failures = run_gates(config, existing, arguments.level) if existing else []
    for failure in failures:
        print(f"{failure.file}: gate {failure.gate} failed\n{failure.output}", file=sys.stderr)
    errors = collect_errors(config, list(CHECKS)) if arguments.level == "pre-push" else []
    for error in errors:
        print(error, file=sys.stderr)
    if failures or errors:
        print(f"sanchin: {arguments.level} blocked", file=sys.stderr)
        return 1
    return 0


def _stdin_lines() -> list[str]:
    if sys.stdin is None or sys.stdin.isatty():
        return []
    return [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]


def _git_lines(config: Config, *arguments: str) -> list[str] | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(config.project_root), "-c", "core.quotepath=off", *arguments],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return [line for line in completed.stdout.splitlines() if line.strip()]


def run_trust(config: Config, _arguments) -> int:
    if not config.gates:
        print("sanchin: the adapter declares no gates; nothing to trust")
        return 0
    for gate in config.gates:
        print(f"  {gate.level:<10} {gate.name}: {gate.run}")
    path = trust(config)
    print(f"sanchin: trusted these {len(config.gates)} gate(s) for {repository_key(config.project_root)} (recorded in {path})")
    return 0


def _working_tree(file: Path) -> Path | None:
    """Top of the git working tree (main checkout or worktree) holding `file`."""
    directory = file.parent
    while not directory.is_dir() and directory != directory.parent:
        directory = directory.parent
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    return Path(completed.stdout.strip()).resolve()


def _relative_to_project(config: Config, file: str) -> str:
    absolute = Path(file).resolve()
    if absolute.is_relative_to(config.project_root):
        return absolute.relative_to(config.project_root).as_posix()
    return file


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

    roadmap = commands.add_parser("roadmap", help="check the milestones, or rewrite their generated story tables")
    roadmap.add_argument("--write", action="store_true", help="regenerate each milestone's stories table first")
    roadmap.set_defaults(handler=run_roadmap)

    superseded = commands.add_parser("superseded", help="print or write the generated superseded-by table")
    superseded.add_argument("--write", action="store_true", help="rewrite the block in stories.superseded_index")
    superseded.set_defaults(handler=run_superseded)

    gates = commands.add_parser("gates", help="run the project's gates of one level over some files")
    gates.add_argument("--level", default="pre-commit", choices=("edit", "pre-commit", "pre-push", "ci"))
    gates.add_argument("files", nargs="+")
    gates.set_defaults(handler=run_gates_command)

    git_hook = commands.add_parser("git-hook", help="run from a git hook: the gates of its level over the files it concerns")
    git_hook.add_argument("level", choices=("pre-commit", "pre-push"))
    git_hook.set_defaults(handler=run_git_hook)

    trust_command = commands.add_parser("trust", help="approve the adapter's current gates, so the hook may run them")
    trust_command.set_defaults(handler=run_trust)

    hook = commands.add_parser("hook", help="PostToolUse hook entry point (reads the hook payload on stdin)")
    hook.set_defaults(handler=run_hook)

    prompt_hook = commands.add_parser("prompt-hook", help="UserPromptSubmit hook entry point: one session per role cycle")
    prompt_hook.set_defaults(handler=run_prompt_hook)
    return parser
