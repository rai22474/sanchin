# The validator

[README](../README.md) · [Docs](index.md)

`scripts/sanchin` checks a project's process artifacts against the rules in
[artifacts/index.md](artifacts/index.md) and [context.md](context.md), with the values
from the project's adapter. It is plain Python (standard library, PyYAML
for the adapter and the official Gherkin parser, `gherkin-official`, for
feature files in any Gherkin language); the wrapper runs it through `uv`,
pinned, when available.

*Why built-in rules with configurable values:* the rules are the process —
every project gets the same guarantees — while names, paths and cut-off
dates differ. Project-specific checks stay project scripts, declared as
gates ([gates.md](gates.md)).

## Commands

```bash
scripts/sanchin check                    # every rule
scripts/sanchin check --only docs        # docs | stories | plans (repeatable)
scripts/sanchin check --file docs/x.md   # per-file doc rules on one file
scripts/sanchin superseded [--write]     # print / rewrite the superseded-by table
scripts/sanchin gates --level pre-push FILE…   # run the project's gates of one level
scripts/sanchin git-hook pre-commit|pre-push   # body of a git hook (gates.md#git-hooks)
scripts/sanchin trust                    # approve the adapter's gates for the hook (gates.md#trust)
scripts/sanchin hook                     # PostToolUse entry point (stdin payload)
scripts/sanchin prompt-hook              # UserPromptSubmit entry point: one session per role cycle
```

Global options: `--project DIR` (default: current directory) and
`--adapter FILE` (default: `DIR/.claude/sanchin.yaml`). Exit code 0 means
clean, 1 means rule violations (printed on stderr, one per line, as
`path[:line]: problem`), 2 means the adapter is missing or invalid.

**Where it runs from.** In a project, `scripts/sanchin` is a thin wrapper
`/sanchin:init` writes from `templates/sanchin`: it finds the installed
plugin — `$SANCHIN` if set, then `$CLAUDE_PLUGIN_ROOT` inside Claude Code,
then Claude Code's plugin registry (`~/.claude/plugins/installed_plugins.json`),
then the newest copy in the plugin cache — and runs it with `--project` set
to the repository. Its path never changes, so git hooks and scripts can
call it; the plugin's own copy moves on every upgrade. Inside Claude Code
the skills call the plugin's copy directly, at
`${CLAUDE_PLUGIN_ROOT}/scripts/sanchin`. In this repository,
`scripts/sanchin` is the validator itself.

## Rules

| Group | Rule |
|---|---|
| docs | `file.ext:NNN` citations point to an existing source file and line (only extensions present in `code_reference_globs` are checked). |
| docs | Relative links resolve. |
| docs | Every document under `docs.root` except its index has a navigation line in its first lines. |
| docs | Every directory with more than one document has an `index.md` linking each document and child index, except `unindexed_catalogs`. |
| stories | Frontmatter: unique id and known state; an implemented story has its `date` (YYYY-MM-DD); `plan`/`scenarios` paths exist; in progress needs plan; implemented since `rules_since` needs plan and scenarios (technical stories excepted). Frontmatter is flat `key: value`; ` # comments` are ignored. |
| stories | No doubt marker after `pending`. |
| stories | Citations name existing stories and criteria; a trace comment counts only above a scenario (tags and comments may sit between); implemented-since-`rules_since` stories have every criterion cited unless exempted. |
| stories | Supersedes links resolve; the superseded-by table is current. |
| stories | Scenario delta matches the feature files for the story's state. |
| stories | An implemented story and its plans are unchanged since the first commit where the story reads implemented (needs git and that commit in the history; `stories.legacy` skipped). |
| plans | Required sections per state; open questions closed; constitution checklist complete, exceptions justified; `legacy` plans skipped. |

## Where it runs

| Level | How |
|---|---|
| edit | The plugin's PostToolUse hook runs the doc rules on every edited markdown file under `docs.root`, plus the project's `edit` gates. The project is the git working tree that holds the edited file — a story's worktree uses its own adapter, docs and cwd, wherever the worktree lives. Silent in a project without an adapter (it exits before starting Python); with an invalid adapter it reports a non-blocking error on each edit, since its gates are off until the adapter is fixed. |
| pre-commit / pre-push | The project's git hook is one line, `scripts/sanchin git-hook <level>`: it runs that level's gates over the staged or pushed files, plus `check` at pre-push ([gates.md](gates.md#git-hooks)). Point it at the plugin's copy, or vendor a pinned copy (see below). |
| CI | Check out sanchin at the version the project pins and run its `scripts/sanchin check`. |

A CI step, pinned to a release tag:

```yaml
- uses: actions/checkout@v4
  with: {repository: rai22474/sanchin, ref: v0.1.0, path: .sanchin}
- run: .sanchin/scripts/sanchin check
```

## Tests

```bash
PYTHONPATH=scripts:tests uv run --no-project --with pyyaml --with gherkin-official==42.0.1 python3 -m unittest discover -s tests
```
