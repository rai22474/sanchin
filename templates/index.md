# Templates

[README](../README.md) · [Docs](../docs/index.md)

Starting points `/sanchin:init` copies into a project that has none,
translated to the project's language and terms. Formats and rules:
[artifacts/index.md](../docs/artifacts/index.md).

| Template | What it contains | When to use it |
|---|---|---|
| [story.md](story.md) | Frontmatter, criteria with a doubt marker, supersedes line, scenario delta, out of scope. | Every new story. |
| [plan.md](plan.md) | The eleven plan sections, constitution checklist and retro included. | Every plan, one per component a story touches. |
| [issue.md](issue.md) | Symptom, root cause, workaround, goal, retro. | Every bug, in the bug lane. |
| [epic.md](epic.md) | Epic with its ordered narratives; generated state. | With the epic layer on. |
| [narrative.md](narrative.md) | One vertical slice and its stories; generated state. | With the narrative layer on. |
| [milestone.md](milestone.md) | Objective, state line and the generated stories table. | With the milestone layer on: the roadmap. |
| [sanchin.yaml](sanchin.yaml) | The minimal adapter: no layers, one component. | A new project without docs; init fills it in. |
