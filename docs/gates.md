# Deterministic gates

[README](../README.md) · [Docs](index.md)

What can be checked by code is checked by code — not by a prompt, not by a
reviewer. This page is the model; the tools are each project's own,
declared in its adapter.

## Four levels

| Level | Runs | Gets | Put here |
|---|---|---|---|
| **edit** | The plugin's PostToolUse hook, on each file Claude writes | Feedback while the change is still in front of the agent | Fast, per-file checks: lint, format, type check of one file, doc references |
| **pre-commit** | The project's git hook | A clean commit | Secrets scan, formatters over staged files |
| **pre-push** | The project's git hook | Nothing broken leaves the machine | Unit tests, `sanchin check`, architecture boundaries, duplication |
| **CI** | The pipeline | The last net | Everything above plus what needs the full environment |

Put each check at the **earliest level where it is cheap**. *Why:* the later
a failure is seen, the further it is from the change that caused it, and the
more it costs to find.

## Rules

- **Run the local gates before calling a change green.** *Why:* CI is the
  last net, not the first place a failure is seen.
- **Diagnose before patching** a gate failure ([process.md](process.md#33-green)).
- **Reviewers skip what gates enforce**, and their brief says which gates
  exist. *Why:* a reviewer repeating a linter spends attention a linter
  doesn't need.
- **Broken twice and checkable by code → propose a gate.** When a rule is
  broken a second time and a script could have caught it, the retro proposes
  the gate ([improvement.md](improvement.md)). *Why:* a rule enforced by a
  prompt is enforced only as well as the prompt is read.

## Declaring gates

```yaml
gates:
  - {name: ruff,     glob: '*.py',        run: 'uv run ruff check {file}',  level: edit}
  - {name: hadolint, glob: 'Dockerfile*', run: 'hadolint {file}',           level: edit}
  - {name: unit,     glob: '*.py',        run: 'uv run pytest -q',          level: pre-push, timeout: 600}
```

`glob` matches the path relative to the project root or the file name;
`{file}` is replaced by the quoted relative path. A gate with `{file}` runs
once per matching file; a gate without it (a test suite) runs once when any
file matches. `timeout` (seconds, default 120) bounds each run; a gate that
exceeds it fails. The hook runs the `edit` gates;
`scripts/sanchin gates --level <level> FILE…` runs any level from a git
hook or CI.

## Git hooks

`sanchin git-hook <level>` is the whole body of a git hook: it works out
the files the hook concerns, runs that level's gates over them, and at
`pre-push` also runs `sanchin check`. A non-zero exit blocks the commit or
the push.

| Level | Files |
|---|---|
| `pre-commit` | The staged files (added, copied, modified, renamed). |
| `pre-push` | The files of every commit being pushed that no remote has yet (from the refs git passes on stdin; `HEAD` when run by hand). |

Gates read the files from the working tree, not the index. The hooks are
one line each, written by `/sanchin:init` after confirmation:

```sh
#!/bin/sh
# .git/hooks/pre-push (or a husky / pre-commit framework step)
exec "/path/to/sanchin/scripts/sanchin" git-hook pre-push
```

The path is the plugin's copy, which moves when the plugin upgrades;
re-running `/sanchin:init` as a doctor checks it. A project that pins
sanchin in CI can point the hook at that copy instead
([validator.md](validator.md#where-it-runs)).

## Trust

Gates are shell commands that come from the repository, and the hook runs
them on every file Claude writes. So the hook runs a repository's gates only
after the user has approved that exact `gates:` list:

```bash
"${CLAUDE_PLUGIN_ROOT}"/scripts/sanchin trust   # prints the gates, records the approval
```

The approval lives outside the repository (`$XDG_STATE_HOME/sanchin/`,
by default `~/.local/state/sanchin/`), is shared by all the repository's
worktrees, and lapses when the `gates:` list changes. Until then the hook
still checks the docs, skips the gates and tells the user why.
`sanchin gates`, from a git hook or CI, is not affected: running it is
already an explicit choice. *Why:* a repository nobody has read must not get
to run commands just because a file was saved in it — and approving
commands is the user's decision, never the agent's.

## What sanchin ships

- The **validator** ([validator.md](validator.md)): process rules and doc
  references, independent of the stack.
- The **hook**: one dispatcher for every `edit` gate, instead of one script
  per tool.
- `/sanchin:init` **detects** the gates a project already has (git hooks,
  CI, linters) and **proposes** the ones its stack is missing. It never
  installs anything without confirmation.
