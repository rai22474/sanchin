"""Run the project's own gates, as the adapter declares them.

A gate is a command bound to a file glob and a level (`edit`, `pre-commit`,
`pre-push`, `ci`). The edit-level gates run from the PostToolUse hook on
every file Claude writes, so the agent gets the failure while it still has
the change in front of it. A gate whose command has `{file}` runs once per
matching file; one without it (a test suite) runs once for all of them.
Reference: docs/gates.md.
"""

import fnmatch
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Config, Gate

FILE_PLACEHOLDER = "{file}"


@dataclass(frozen=True)
class GateFailure:
    gate: str
    file: str
    output: str


def gates_for(config: Config, relative_file: str, level: str) -> list[Gate]:
    return [gate for gate in config.gates if gate.level == level and _matches(gate, relative_file)]


def run_gates(config: Config, relative_files: list[str], level: str) -> list[GateFailure]:
    failures = []
    for gate in config.gates:
        if gate.level != level:
            continue
        matching = [file for file in relative_files if _matches(gate, file)]
        if not matching:
            continue
        if FILE_PLACEHOLDER in gate.run:
            for file in matching:
                failure = _run(config, gate, gate.run.replace(FILE_PLACEHOLDER, shlex.quote(file)), file)
                if failure is not None:
                    failures.append(failure)
        else:
            failure = _run(config, gate, gate.run, ", ".join(matching))
            if failure is not None:
                failures.append(failure)
    return failures


def _matches(gate: Gate, relative_file: str) -> bool:
    return fnmatch.fnmatch(relative_file, gate.glob) or fnmatch.fnmatch(Path(relative_file).name, gate.glob)


def _run(config: Config, gate: Gate, command: str, files: str) -> GateFailure | None:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=config.project_root,
            capture_output=True,
            text=True,
            timeout=gate.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return GateFailure(gate.name, files, f"timed out after {gate.timeout}s (set `timeout:` on the gate to allow longer)")
    if completed.returncode != 0:
        return GateFailure(gate.name, files, (completed.stdout + completed.stderr).strip())
    return None
