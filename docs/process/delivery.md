# 3. Delivery cycle

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

`/sanchin:developer`, on a planned story.

## 3.1 Start

Set the story **in progress** on `main` and commit just that, with the
user's approval; then create the story's branch and worktree from it.
Everything below happens in the worktree. *Why:* `main` says who holds
which story — a story that still reads planned there gets picked up twice;
and several sessions can work in one repository at once, so a shared
working tree would mix their changes into each other's commits.

## 3.2 Scenarios red

Write the steps behind the story's scenarios and apply the delta's changes
(~) and removals (−). Run the story's scenarios — including the
`@pending` ones — once, red.

- A scenario must fail because nothing implements the behaviour yet, not
  because a step is missing or doesn't parse. **A scenario that passes in
  red is not a guard**: strengthen it until it fails for the right reason.
  *Why:* a scenario that passes without the change can't tell before from
  after; negative outcomes ("nothing is created") are the ones that most
  easily pass empty.
- A scenario that can't be made to fail for the right reason is a spec
  problem: back to the product owner.

## 3.3 Green

With several plans, each goes to its own sub-agent, in parallel, in a
worktree branched from the story's branch, touching only its component;
the main session merges them into the story's branch and runs the
acceptance scenarios there, since they cross components.

- **Load the standards first**, through the project's index of standards
  ([context.md](../context.md)). A sub-agent gets the list of files that
  apply in its prompt. *Why:* nothing loads them automatically.
- **Mirror the leanest existing sibling** implementation, and check every
  module the change creates or grows against the project's design smells
  yourself, applying each smell's general test, not the shape of its
  example. *Why:* copying a sibling copies its smells, and gates don't see
  design smells; the review is the second net, not the first.
- **Follow the plan; record every deviation** in its Implementation
  section. A deviation that changes the design goes back to the tech-lead.
- **Run every local gate before calling it green** ([gates.md](../gates.md)).
  *Why:* CI is the last net, not the first place a failure is seen.
- **On any gate failure, diagnose before patching**: find the root cause
  and state it (what failed, the real cause, the proposed fix) before
  touching code. A mechanical, unambiguous fix (a typo, a name collision)
  can be stated and applied in one step, flagged as such; anything touching
  business logic waits for confirmation. If a fix doesn't resolve the
  failure, go back to diagnosis. *Why:* patches layered on an unconfirmed
  diagnosis spiral away from the cause.

## 3.4 Reviews

Right after committing on the story's branch, `/sanchin:reviewer` over the
diff from the branch point. `/mattpocock-skills:code-review` runs first as
the generic outside view and the reviewer reports only what that review
didn't. Every finding is written into the plan's review section with its
**source** label.

*Why the label:* it is the only way to know later what each review adds,
and whether both are worth their cost ([improvement.md](../improvement.md)).

**Fixing a finding:** restate it in one sentence and check the diff against
that sentence — not "does it still pass" but "has this stopped being true".
*Why:* a fix can touch a symptom next to the finding and leave every test
green.

## 3.5 Close, retro and merge

Address real findings, re-run the gates and the scenarios the fix touches,
and commit on the story's branch. In that same commit:

- drop the `@pending` tag from the story's scenarios;
- set the story to implemented, with its date (and close any issue it
  resolves);
- regenerate the milestone tables and the superseded-by table;
- write the delivery retro in the plan's **Retro** section (*Delivery*,
  [improvement.md](../improvement.md)).

Then, with the user's approval, integrate the story's branch the way the
adapter's `merge` says ([adapter.md](../adapter.md)):

- **`local`** (the default): merge it into `main`, push, check that CI
  actually passed, and remove the worktree.
- **`pr`**: push the branch and open a pull request whose body is the
  story, its plans and the review findings with their outcome; check that
  CI actually passed on it, and stop — merging is the team's step. Remove
  the worktree once it is merged. A finding raised on the pull request is
  fixed on the branch the same way as in 3.4, and counts as an escaped
  finding in the retro. *Why:* where `main` is protected or others review,
  the pull request is the team's gate; the local reviews feed it instead of
  replacing it.

Stop. The next planned story, or the roadmap, is the user's choice.
