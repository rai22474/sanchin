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
- **Diagnose before patching** a gate failure ([process.md](process.md#36-green)).
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
  - {name: unit,     glob: '*.py',        run: 'uv run pytest -q',          level: pre-push}
```

`glob` matches the path relative to the project root or the file name;
`{file}` is replaced by the quoted relative path. The hook runs the `edit`
gates; `scripts/sanchin gates --level <level> FILE…` runs any level from a
git hook or CI.

## What sanchin ships

- The **validator** ([validator.md](validator.md)): process rules and doc
  references, independent of the stack.
- The **hook**: one dispatcher for every `edit` gate, instead of one script
  per tool.
- `/sanchin:init` **detects** the gates a project already has (git hooks,
  CI, linters) and **proposes** the ones its stack is missing. It never
  installs anything without confirmation.
