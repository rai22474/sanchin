# The validator

[README](../README.md) · [Docs](index.md)

`scripts/sanchin` checks a project's process artifacts against the rules in
[artifacts.md](artifacts.md) and [context.md](context.md), with the values
from the project's adapter. It is plain Python (standard library plus
PyYAML for the adapter); the wrapper runs it through `uv` when available.

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
scripts/sanchin hook                     # PostToolUse entry point (stdin payload)
```

Global options: `--project DIR` (default: current directory) and
`--adapter FILE` (default: `DIR/.claude/sanchin.yaml`). Exit code 0 means
clean, 1 means rule violations (printed on stderr, one per line, as
`path[:line]: problem`), 2 means the adapter is missing or invalid.

Inside Claude Code the plugin's copy lives at
`${CLAUDE_PLUGIN_ROOT}/scripts/sanchin`; the skills reference it that way.

## Rules

| Group | Rule |
|---|---|
| docs | `file.ext:NNN` citations point to an existing source file and line (only extensions present in `code_reference_globs` are checked). |
| docs | Relative links resolve. |
| docs | Every document under `docs.root` except its index has a navigation line in its first lines. |
| docs | Every directory with more than one document has an `index.md` linking each document and child index, except `unindexed_catalogs`. |
| stories | Frontmatter: id and known state; `plan`/`scenarios` paths exist; in progress needs plan; implemented since `rules_since` needs plan and scenarios (technical stories excepted). |
| stories | No doubt marker after `pending`. |
| stories | Citations name existing stories and criteria; implemented-since-`rules_since` stories have every criterion cited unless exempted. |
| stories | Supersedes links resolve; the superseded-by table is current. |
| stories | Scenario delta matches the feature files for the story's state. |
| plans | Required sections per state; open questions closed; constitution checklist complete, exceptions justified; `legacy` plans skipped. |

## Where it runs

| Level | How |
|---|---|
| edit | The plugin's PostToolUse hook runs the doc rules on every edited markdown file under `docs.root`, plus the project's `edit` gates. Silent in a project without an adapter. |
| pre-commit / pre-push | Call `scripts/sanchin check` from the project's hook. Point it at the plugin's copy, or vendor a pinned copy (see below). |
| CI | Check out sanchin at the version the project pins and run its `scripts/sanchin check`. |

A CI step, pinned to a release tag:

```yaml
- uses: actions/checkout@v4
  with: {repository: rai22474/sanchin, ref: v0.1.0, path: .sanchin}
- run: .sanchin/scripts/sanchin check
```

## Tests

```bash
PYTHONPATH=scripts:tests uv run --no-project --with pyyaml python3 -m unittest discover -s tests
```
