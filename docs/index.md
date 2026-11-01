# Docs

[README](../README.md)

Everything sanchin does, one document per reader.

| Document | What it contains | When to read it |
|---|---|---|
| [process/](process/index.md) | The process: an index of the four cycles — product, planning, delivery, architecture — then one document per cycle, the story states, the bug lane and the working rules (trunk-based git, pacing, approvals). | Read its index first, then only the cycle you run; every role skill names the documents it reads. |
| [artifacts/](artifacts/index.md) | The formats, one document each: base documents, story, scenarios, plan, layers and roadmap, issue — what each must contain and what the validator checks. | Only the format you are about to write or review. |
| [adapter.md](adapter.md) | Every field of `.claude/sanchin.yaml`, with a full example. | When setting up a project, or when the validator reads a value you didn't expect. |
| [validator.md](validator.md) | The validator's commands, each rule it enforces, and how to run it in hooks and CI. | When wiring sanchin into a pipeline, or when a check fails and it isn't clear why. |
| [gates.md](gates.md) | The four gate levels, their rules, and how a project declares its own gates. | When adding a check, or deciding where it should run. |
| [context.md](context.md) | The wiki as the project's memory — what is written where, and by whom — and progressive disclosure: thin entry points, navigation and catalog indexes, navigation lines. | When deciding where a decision should be recorded, creating or moving a document, or writing an index. |
| [improvement.md](improvement.md) | Signals, the retro, the rule of two, eval-driven skill changes, the coach. | When closing a story, or when a rule keeps being broken. |
| [adopting.md](adopting.md) | Bringing sanchin into a project that already has docs and checks. | Before running `/sanchin:init` on an existing repository. |
| [decisions/](decisions/index.md) | sanchin's own decision records. | When you wonder why sanchin works the way it does. |
