# Layers and roadmap

[README](../../README.md) · [Docs](../index.md) · [Artifacts](index.md)

## Optional layers

With `layers` in the adapter a project adds **epics**, **narratives** and
**milestones** above stories; the product owner walks them in that order
(mission → epics → narratives → stories) and skips the ones that are off.
Narratives are vertical slices ordered from less to more functionality.
Their states, and the epics', are derived from their stories and generated,
never written by hand — by the project's own script; sanchin's validator
generates and checks the milestone tables.

## Roadmap

With the `milestone` layer, the roadmap is a set of **milestones**, one file
each under `roadmap.directory`: an objective in prose, the product owner's
state line, and a generated table of the stories that deliver it.

```markdown
# Milestone 2 — Export my data

[Docs](../../index.md) · [Roadmap](../index.md)

**State:** in progress.

## Objective

Why these stories ship together, and what is true when they have.

## Stories

<!-- sanchin:milestone-stories:start -->
| Story | State |
|---|---|
| [ST-12 — Export my data as CSV](../../stories/st-12-export.md) | ready |
<!-- sanchin:milestone-stories:end -->
```

A story joins a milestone through `milestone:` in its frontmatter; the
table is regenerated with `sanchin roadmap --write`.

| Rule | Enforced by |
|---|---|
| A story ready, planned or in progress names its milestone; every named milestone exists. | validator |
| The state is planned, in progress or closed; at most one milestone is in progress. | validator |
| A milestone reads closed exactly when it has stories and all are implemented. | validator |
| The stories table is up to date. | validator |
| The order of milestones, and which stories go in each, is the product owner's decision. | review |
