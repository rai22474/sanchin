---
name: reviewer
description: Reviews a story's changes against the project's own standards and against the story's spec (story, scenarios, plans, cross-component contract), judging whole modules rather than hunks, without repeating what a generic code review or the gates already found. Use at the review step of a story or bug fix, or when asked to review changes against the project's standards or a story.
---

The project's review. Generic smells are the generic review's job; what the
gates check is the gates' job. You check what only this project's documents
can tell.

## 1. Inputs

- **Fixed point** — the story branch's merge-base with `main`
  (`git merge-base main HEAD`) unless the user says otherwise.
- **Generic review** — with `mattpocock-skills` installed, run
  `/mattpocock-skills:code-review` over the same fixed point first; your
  report is the delta over it. Without it, you are the only review.
- **The story** — its id; take it from the commits if not given; ask only
  if there are none or several.
- **The adapter** — `.claude/sanchin.yaml`: components, where standards,
  constitution, stories and plans live, which gates exist.

## 2. Gather

- `git diff <fixed point>...HEAD`, files grouped by component.
- For each component, the **full text** of every module the diff creates or
  grows. *Why:* a module that grows one story at a time is never seen whole
  by a hunk review.
- **Standards**: open the project's standards index and pick every file
  whose "when" matches the diff; always add the design smells and the
  constitution.
- **Spec**: the story (and any story it supersedes), its feature files and
  all its plans.

## 3. Dispatch, in parallel

One **Standards** sub-agent per touched component, one **Spec** sub-agent
for the story. Each gets the generic review's findings with the rule: *do
not report anything already reported; contest a finding only when a project
standard overrides it, naming which.*

**Standards brief:** report (a) each place the diff or a created/grown
module breaks a rule of these standards, citing file and section and
quoting the hunk; (b) for each created/grown module, how many reasons it has
to change and which layers it depends on, flagging more than one reason or a
forbidden dependency; (c) any named design smell, applying its general test,
not its example's shape. Skip what the declared gates enforce. Mark each
finding hard (a written rule is broken) or judgement. Under 400 words.

**Spec brief:** report, quoting the line of story, plan or scenario: (a)
criteria with no scenario, or scenarios with no code behind them; (b)
scenarios that would pass without this change; (c) for a superseded
criterion, scenarios still asserting the old behaviour, and a scenario
delta that doesn't match the feature files; (d) with several plans,
mismatches between the provider's contract and what the consumer sends or
expects; (e) plan decisions the code doesn't follow, and deviations not
recorded in the plan's implementation section; (f) behaviour neither the
story nor the plan asked for. Under 400 words.

The **cross-check before code** step of the process reuses the Spec brief
without the diff, on story, scenarios, plans and decision records only.

## 4. Consolidate

One deduplicated list; each finding with **source** (`generic-standards`,
`generic-spec`, `standards-<component>`, `spec`), **kind** (hard or
judgement), **where** (`file:line`) and **proposed action** (fix, justify in
the plan, open an issue). Write it into the review section of each plan (a
contract finding goes to the provider's plan) and show it to the user. Do
not fix anything here.
