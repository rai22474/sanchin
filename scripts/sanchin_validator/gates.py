"""Run the project's own gates, as the adapter declares them.

A gate is a command bound to a file glob and a level (`edit`, `pre-commit`,
`pre-push`, `ci`). The edit-level gates run from the PostToolUse hook on
every file Claude writes, so the agent gets the failure while it still has
the change in front of it. Reference: docs/gates.md.
"""

import fnmatch
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Config, Gate

GATE_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class GateFailure:
    gate: str
    file: str
    output: str


def gates_for(config: Config, relative_file: str, level: str) -> list[Gate]:
    return [
        gate
        for gate in config.gates
        if gate.level == level and (fnmatch.fnmatch(relative_file, gate.glob) or fnmatch.fnmatch(Path(relative_file).name, gate.glob))
    ]


def run_gates(config: Config, relative_file: str, level: str) -> list[GateFailure]:
    failures = []
    for gate in gates_for(config, relative_file, level):
        command = gate.run.replace("{file}", shlex.quote(relative_file))
        completed = subprocess.run(
            command,
            shell=True,
            cwd=config.project_root,
            capture_output=True,
            text=True,
            timeout=GATE_TIMEOUT_SECONDS,
            check=False,
        )
        if completed.returncode != 0:
            failures.append(GateFailure(gate.name, relative_file, (completed.stdout + completed.stderr).strip()))
    return failures
