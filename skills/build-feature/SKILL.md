---
name: build-feature
description: Use when implementing a feature plan file that is split into phases with task checkboxes. Builds one phase per branch, opens a PR, reviews it twice in a subagent, fixes only what is worth fixing, then merges before starting the next phase.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

Turn a phased plan into merged code. One phase is one PR, reviewed twice and fixed twice before it merges — because a plan built in one giant branch cannot be tested by the user, and code merged after a single review pass merges the fixes unreviewed.

```
for each phase in the plan:

  branch  →  do the phase's tasks  →  demo passes  →  push  →  open PR
                                                                  |
                        review #1 (subagent)  →  fix worth-fixing |
                                                                  |
                        review #2 (subagent)  →  fix worth-fixing |
                                                                  v
                        merge (merge commit)  →  back to base  →  next phase
```

## Rules

1. **Start from the plan file, never from memory.** Take the path from the argument; otherwise look under `plans/` and ask which one if more than one matches. Re-read it at the start of every phase — it may have changed. If any decision is still `_open_`, stop and send the user back to planning: code written around an open decision is code they will throw away.

2. **One phase, one branch, one PR.** Build the first phase that still has unchecked boxes. Never pull work forward from a later phase, even when it is three lines and "right there" — the phase boundary is what makes the PR reviewable and the demo meaningful. Branch from an up-to-date base, naming the branch after the plan and phase number.

3. **Do the phase's tasks and nothing else.** Unrelated bugs, stale code, and tempting refactors go under `## Notes` in the plan as one line each — not into this PR. Tick each task box and update the `## Progress` line as the work lands, in the same commit as the work, so an interrupted session knows exactly where it stopped.

4. **Prove the Demo line before opening the PR.** Run the exact command, URL, or click path the phase names. If it does not do what the phase promised, the phase is not done. Run the repo's own checks too — `make build` / `make test` / `make lint` when a Makefile has those targets, otherwise the project's native commands.

   **A deferred Demo is not a demo to invent.** When the phase says `**Demo:** deferred`, run the repo's checks, report that this phase's verification is deferred to the feature's end-to-end check, and move on — do not substitute a production run for the missing proof. After the last phase merges, hand the user the plan's `## Rollout` steps and that end-to-end check to run themselves. If a phase names no Demo at all and no deferral, ask the user how they want it verified before opening the PR.

   **Prove it locally, and stop before anything shared.** The demo runs against a local or disposable environment — a dev server, a test database, a scratch account. If it needs a host, database, or account nobody can throw away — a deployed URL, a shared or production database, an admin login — stop and ask the user first, naming what it would change. Never open a credential file (`.env*`, `prod.env`, a secrets store) to make a demo runnable: a missing credential is the environment telling you this demo is not yours to run. A plan's rollout steps are the user's to run after merge, not yours to run as proof — and a demo that cannot run locally is a planning bug, so say so instead of working around it.

5. **Open the PR with a short, feature-focused body.** Imperative title, a `## Summary` of what this phase gives the user with bullets proportional to the diff, and a line naming the phase number and plan file. No test plan, no checklist, no co-author line. If `gh` or a GitHub remote is unavailable, stop at the pushed branch, say so, and skip to rule 10 — do not fake a review cycle.

6. Review the PR in a subagent, Use the repo's review skill if one is installed, invoked as `review-code` with target `pr <number> --sub`; otherwise spawn a subagent to review that PR's diff for correctness, security, resource, and performance defects and to rate each finding by severity, likelihood, and whether it is worth fixing. Relay its report as-is. Do not re-review its findings yourself — reading the whole diff back into this session is what the subagent exists to avoid.

7. **Fix only what is worth fixing.** Not everything a review prints deserves a commit:

   | Verdict in the report                | Action                                                                                                                  |
   | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
   | Worth fixing: Yes                    | Fix it in this PR                                                                                                       |
   | Judgment call                        | Fix if the effort is Trivial or Small **and** it lives in this phase's scope; otherwise log it in the plan's `## Notes` |
   | Worth fixing: No / Low severity nits | Leave it — say you left it                                                                                              |

   Push fixes as their own commits so the second review can see what changed. Then say in one line which findings you skipped and why; a silently dropped finding reads as a finding that never existed.

8. **Always run the second review, even when the first was clean.** Fixes are new, unreviewed code, and that is exactly where the next bug is. Point round 2 at the same PR after the fix commits land, and apply rule 7 to its findings the same way. Re-run the Demo line after fixing. Stop at two rounds — if round 2 still surfaces must-fix findings after fixing, the phase is too big; say so and let the user decide rather than looping a third time.

9. **Merge only when all four hold:** the demo passes, both review rounds ran, no `Yes` finding is left unfixed, and CI is green. Merge with a merge commit — never squash — delete the branch, and return to an up-to-date base before the next phase.

10. **Report the phase in one short block, then start the next one.** PR link, tasks completed, findings fixed, findings deliberately skipped, and the demo the user can run themselves. Continue to the next phase without asking, unless the user said to stop or rule 11 fired.

11. **When the build proves a locked decision wrong, stop and say so.** Name the decision, what the code showed, and which later phases it invalidates. The user amends the plan; you do not quietly re-plan around their choice.

## Verification procedure

Before merging any phase's PR, check:

1. **Every task box for this phase is ticked** and the `## Progress` line matches the real count.
2. **The demo was actually run** after the last fix commit — not just before the first review — or the phase's Demo says `deferred` and you said so in the report.
3. **Two review rounds happened on this PR**, both in a subagent, the second after the fix commits.
4. **No `Yes` finding is unfixed**, and every skipped `Judgment call` has a one-line reason recorded.
5. **Nothing shared was touched** — the demo ran locally, and no production database, deployed host, or credential file was read or written without the user saying yes first.

## Common mistakes to watch for

- **Batching phases into one PR.** It defeats the point of the plan: the user cannot try phase 1 until phase 4 is written.
- **Escalating to production to make a demo pass.** An unset `DATABASE_URL` is a stop sign, not a puzzle. Sourcing `prod.env` to finish the demo turns a pre-review proof into an unreviewed production change — the one thing the phase-per-PR loop exists to prevent.
- **Squash-merging.** The per-phase history is the record of how the feature was built.
