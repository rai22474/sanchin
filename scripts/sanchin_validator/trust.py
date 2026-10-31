"""Trust for the gates a repository declares.

Gates are shell commands taken from the repository's adapter, and the hook
runs the edit-level ones on every file Claude writes. A repository nobody
has looked at must not get to run commands that way, so the hook runs the
gates only when the user has approved this exact `gates:` list for this
repository with `sanchin trust`. Approvals live outside every repository,
in the user's state directory, keyed by the repository's git common
directory (shared by all its worktrees) and the hash of the list.

`sanchin gates` is not affected: running it is already an explicit choice,
from a git hook or CI the project set up.
Reference: docs/gates.md#trust.
"""

import hashlib
import json
import os
import subprocess
from dataclasses import asdict
from pathlib import Path

from .config import Config


def trust_file() -> Path:
    if os.environ.get("SANCHIN_TRUST_FILE"):
        return Path(os.environ["SANCHIN_TRUST_FILE"])
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state) / "sanchin" / "trusted-gates.json"


def gates_hash(config: Config) -> str:
    canonical = json.dumps([asdict(gate) for gate in config.gates], sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def repository_key(project_root: Path) -> str:
    """The git common directory, so every worktree of a repository shares one approval."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return str(project_root.resolve())
    if completed.returncode != 0 or not completed.stdout.strip():
        return str(project_root.resolve())
    return str((project_root / completed.stdout.strip()).resolve())


def is_trusted(config: Config) -> bool:
    if not config.gates:
        return True
    return _load().get(repository_key(config.project_root)) == gates_hash(config)


def trust(config: Config) -> Path:
    approvals = _load()
    approvals[repository_key(config.project_root)] = gates_hash(config)
    path = trust_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(approvals, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _load() -> dict[str, str]:
    path = trust_file()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}
