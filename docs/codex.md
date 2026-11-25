# Using Sanchin with Codex

[README](../README.md) · [Docs](index.md)

Sanchin shares its skills, process, templates and validator across Claude
Code and Codex. This guide covers the Codex installation and the parts of
the workflow that depend on the client.

## Install from a checkout

You need a Sanchin checkout at the tag or commit you want to use, an existing
project directory, and the [validator requirements](validator.md).

```bash
/path/to/sanchin/scripts/install-codex-skills /path/to/project
```

The installer links the checkout at `.agents/sanchin` and writes small
entry points under `.agents/skills/sanchin-*/`. They load the shared
instructions from that checkout. You can leave the project's `AGENTS.md`
as it is. Keep the checkout at the same path and treat these generated
files and the link as local to each developer's checkout.

Start a Codex session in the target project and invoke `$sanchin-init`.
It maps what the project has into `.claude/sanchin.yaml` and sets up
the project wrapper `scripts/sanchin`. When adopting a project that
already uses Sanchin, run the same skill as a doctor and update the wrapper
if it predates Codex support. See [the adoption guide](adopting.md).

## Run a cycle

Use `$sanchin-product-owner` to refine a story, `$sanchin-tech-lead` to
plan it, and `$sanchin-developer` to deliver it. Start each cycle in a
fresh session. The skill for each cycle reads the previous role's
artifacts from the repository. See the [full list of roles](../README.md#roles).

| Feature | Codex distribution |
|---|---|
| Interviews and reviews | Follow the shared [grill](process/working-rules.md#grills) and [generic review](process/working-rules.md#generic-review) rules. The marketplace dependency belongs to the Claude Code plugin. |
| Models and session enforcement | Select the model in Codex and start a fresh session at hand-off. `models` and `session.fresh_per_cycle` configure Claude Code behavior. |
| Approvals | The adapter expresses the user's Sanchin approvals. Codex and the workspace still enforce their own permissions. |
| Validation | Use `scripts/sanchin check` at hand-offs and configure Git hooks or CI as needed. Run edit gates explicitly as described in [Gates](gates.md). The Codex installation does not register edit, prompt or adapter guard hooks. |
| Gate trust | The `trust` skill and its approval record are for the Claude Code edit hook. Git hooks, CI and explicit gate commands work independently. |

## Skill runtime

In Codex, resolve `.agents/sanchin` from the target project root to its
absolute checkout path. Read the named shared skill from that checkout.
Resolve Sanchin's `docs/`, `templates/`, skill references and validator
from the checkout. Resolve the adapter and project artifacts from the
active project or story worktree. A role named `<role>` in the shared
instructions is exposed as `$sanchin-<role>`. For an in-cycle review,
read the shared reviewer instructions and follow them in the current
session.

Keep the checkout path when moving into a story worktree. The wrapper
looks for the local installation link first and then for the link in
the primary Git worktree. If neither has the link, install in the story
worktree or set `SANCHIN` to the absolute path of the checkout's
`scripts/sanchin`. To open a fresh Codex session in that worktree with
the roles available, run the installer there as well.

## Update

Check out the new tag or commit in the same Sanchin checkout and rerun the
installer to refresh the generated entries and descriptions. Start a
fresh Codex session and use `$sanchin-init` to check the adapter and wrapper.
The installer replaces its own generated entries and refuses to overwrite
unrelated files at those destinations. Keep the generated entry points
and the checkout at the same version when switching versions.
