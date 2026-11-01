# Evals

[README](../README.md) · [Docs](../docs/index.md)

One case per critical skill rule, in the `claude plugin eval` format
(`<case>/prompt.md`, `case.yaml`, `graders/`). Cases that need a project on
disk seed it with `fixture.sh`, which only runs with `--scaffold`.

```bash
evals/run.sh --scaffold --allow-tools Bash Write Edit             # every case, with a no-plugin baseline
evals/run.sh --scaffold --allow-tools Bash Write Edit --tag init  # one tag
```

Run them through `evals/run.sh`, never `claude plugin eval .` directly: the
eval sandbox can't resolve sanchin's plugin dependency, and without the
wrapper sanchin silently doesn't load, so every case measures Claude alone.
The script runs the suite on a copy without the dependency (its header says
why) and writes results to `evals/results/` (ignored by git).

**Requirements:** granting `Bash` needs Claude Code's sandbox — on Linux,
`bubblewrap` and `socat` installed. Without it every run is refused before
it starts, and the cases fail with a sandbox error, not a verdict.

**Reading the results:** each case also runs without the plugin. A case
that scores the same both ways (Δ = 0) guards a rule Claude already follows
from the fixture's context: a regression net, not evidence of what the
plugin adds. The cases that show the plugin's worth are the ones with Δ > 0.
One run per case (`--runs 1`) finds clear failures; the default of three
shows whether a pass is stable.

A skill change starts here: add the case that fails today, change the
skill, and keep every case green ([improvement.md](../docs/improvement.md)).

| Case | Rule it guards |
|---|---|
| product-owner-asks-the-doubt | Refining asks a doubt marker, doesn't guess it, and keeps the story pending until it's answered. |
| developer-without-adapter-offers-init | No adapter → offer init, don't guess a layout. |
| architect-quotes-the-vision | Principles come from the project's vision, not the skill. |
| product-owner-writes-only-after-confirming | Advisory skills write drafts only after confirmation. |
| init-maps-existing-names | init maps the project's names into the adapter and renames nothing. |
| maintainer-escalates-behaviour-change | A fix that changes what the user sees goes to the product owner as a story, not the short lane. |
| reviewer-skips-what-gates-enforce | The reviewer reports what only the project's standards tell, with its source label, and skips what a gate enforces. |
| coach-waits-for-the-rule-of-two | The coach proposes a change only for a signal seen twice, and changes nothing without the user. |
| tech-lead-plans-a-ready-story | A ready story gets its plans, closed, and is handed over planned — no code. |
| tech-lead-returns-a-functional-question | A functional gap found while planning goes back to the product owner as a doubt marker, even when told to decide technical questions alone. |
| developer-waits-for-a-plan | A ready but unplanned story isn't implemented; the developer points to the tech-lead. |
| architect-turns-an-idea-into-a-decision | A technical idea becomes a decision record superseding the one in force, plus technical stories for the roadmap — no code. |
