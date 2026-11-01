# Plan

[README](../../README.md) · [Docs](../index.md) · [Artifacts](index.md)

The "how" of one story for one component, written by the tech-lead.
Frozen once the story is implemented.

```markdown
# Plan — <what changes> (ST-12)

**Story:** [ST-12 — …](../…) · **Other plans:** [api](../…)

## 1. Current state        what the code does today, with file:line citations
## 2. Design               modules, contract, why this shape
## 3. Constitution checklist
- tramp-data: n/a
- layered-architecture: ok
- god-module: exception → D2
## 4. Risks
## 5. Tests                scenarios that cover it, new unit tests
## 6. Steps                ordered, each green before the next
## 7. Open questions       empty before code
## 8. Decisions            D1, D2 … from the technical grill
## 9. Implementation       what changed against the plan, and why
## 10. Review              findings with their source label and outcome
## 11. Retro               Planning (tech-lead) and Delivery (developer); see improvement.md
```

| Rule | Enforced by |
|---|---|
| Planned and in progress: Current state, Design and Steps exist (`required_sections.in_progress`). Implemented: also Implementation and Review. | validator (`required_sections`) |
| Open questions empty once the story is planned — the tech-lead sets it planned only after the technical grill closes them. | validator |
| Constitution checklist answers every constitution item that applies to the plan (global rules plus its component's) with an allowed verdict; every exception names a `D-n`. | validator |
| Plans that predate the rules are listed in `plans.legacy` and skipped. | validator |
| The plan doesn't restate the story; the contract lives in the provider's plan only. | review |
