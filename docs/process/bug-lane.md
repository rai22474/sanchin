# Bug lane

[README](../../README.md) · [Docs](../index.md) · [Process](index.md)

`/sanchin:maintainer` handles a known bug without the full ceremony:

1. **The issue is the spec**: symptom, root cause once known, goal.
2. **Diagnose first**: reproduce, find the root cause, write it in the
   issue before touching code.
3. **Regression scenario red**: a test that fails because of the bug.
4. **Fix** to green, with the local gates.
5. **Both reviews**, as in 3.4.
6. **Close**: the issue is marked resolved with what resolved it, in the
   same commit; retro in the issue. Then integrate the branch as in 3.5
   (`merge: local` or `pr`).

**Escalate** when the fix changes behaviour the user sees, touches a
cross-component contract, or needs a design decision: write a pending story
linking the issue, and hand it to the product owner. *Why:* at that point
the bug is a story in disguise, and skipping the cycles skips the user.
