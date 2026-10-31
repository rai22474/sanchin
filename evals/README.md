# Evals

[README](../README.md) · [Docs](../docs/index.md)

One case per critical skill rule, in the `claude plugin eval` format
(`<case>/prompt.md`, `case.yaml`, `graders/`). Cases that need a project on
disk seed it with `fixture.sh`, which only runs with `--scaffold`.

```bash
claude plugin eval . --scaffold            # every case, with a no-plugin baseline
claude plugin eval . --scaffold --tag init # one tag
```

A skill change starts here: add the case that fails today, change the
skill, and keep every case green ([improvement.md](../docs/improvement.md)).

| Case | Rule it guards |
|---|---|
| developer-stops-on-doubt | A doubt marker is asked, not guessed; no plan before it is resolved. |
| developer-without-adapter-offers-init | No adapter → offer init, don't guess a layout. |
| architect-quotes-the-vision | Principles come from the project's vision, not the skill. |
| product-owner-writes-only-after-confirming | Advisory skills write drafts only after confirmation. |
| init-maps-existing-names | init maps the project's names into the adapter and renames nothing. |
| maintainer-escalates-behaviour-change | A fix that changes what the user sees goes to the full loop, not the short lane. |
| reviewer-skips-what-gates-enforce | The reviewer reports what only the project's standards tell, with its source label, and skips what a gate enforces. |
| coach-waits-for-the-rule-of-two | The coach proposes a change only for a signal seen twice, and changes nothing without the user. |
