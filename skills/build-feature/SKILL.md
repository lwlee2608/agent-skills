---
name: build-feature
description: Use when implementing a feature plan file that is split into phases with task checkboxes. Builds one phase per branch, opens a PR against a feature-wide integration branch, reviews it twice in a subagent, fixes only what is worth fixing, then merges before starting the next phase and leaves the final merge to main to the user.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

Turn a phased plan into merged code. One phase is one PR, reviewed twice and fixed twice before it merges — because a plan built in one giant branch cannot be tested by the user, and code merged after a single review pass merges the fixes unreviewed. Every phase merges into one feature-wide integration branch, and only the user merges that branch into `main`.

```
main
 └─ integrate/<plan>                         cut once, before the first phase
     ├─ <plan>-phase-1 ──PR──▶ integrate     build, demo, review x2, fix, merge
     ├─ <plan>-phase-2 ──PR──▶ integrate
     ├─ <plan>-phase-N ──PR──▶ integrate
     └──────────────────PR──▶ main           the user verifies and merges this one
```

```
for each phase in the plan:

  branch off integrate  →  a subagent builds it  →  demo passes  →  push  →  PR
                                                                             |
                        review #1 (subagent)  →  fix worth-fixing            |
                                                                             |
                        review #2 (subagent)  →  fix worth-fixing            |
                                                                             v
                        merge (merge commit)  →  back to integrate  →  next phase

this session holds the plan and the reports — never the diff
```

## Rules

1. **Start from the plan file, never from memory.** Take the path from the argument; otherwise look under `plans/` and ask which one if more than one matches. Re-read it at the start of every phase — it may have changed. If any decision is still `_open_`, stop and send the user back to planning: code written around an open decision is code they will throw away.

2. **One feature, one integration branch; one phase, one branch, one PR.** Before the first phase, cut `integrate/<plan-name>` from an up-to-date `main` and push it — reuse it if it already exists. Every phase branches from it and every phase PR targets it, so `main` never holds half a feature. Build the first phase that still has unchecked boxes. Never pull work forward from a later phase, even when it is three lines and "right there" — the phase boundary is what makes the PR reviewable and the demo meaningful, and batching phases means the user cannot try phase 1 until phase 4 is written. Branch from an up-to-date integration branch, naming the branch after the plan and phase number.

3. **Every code change goes to a subagent — the build and the review fixes alike.** Cut the branch yourself, then hand the whole phase to one subagent and keep its diff out of this session. Give it the plan path, the phase number, its task list, its Demo line, and the repo's check commands, and tell it to follow rules 4 and 5. It returns only:

   - the commit sha and the files it touched
   - what it ran for the Demo and what it saw
   - the build, test, and lint results
   - anything it could not do, and why

   Delegate the fixes after each review the same way, handing the findings over verbatim, and the fix subagent re-runs the Demo before it reports.

   **A subagent has nobody to ask, so it must never ask.** On an open decision, a Demo it cannot run locally, or a locked decision the code disproves, it stops and says so in its report — you raise that with the user (rules 1, 5, 12).

   Do not read the diff any of them produced. The PR body comes from the build report; correctness comes from the two reviews. If you find yourself opening the changed files, the delegation has failed and this session is carrying the phase after all — which costs the next phase its context.

4. **Do the phase's tasks and nothing else.** Unrelated bugs, stale code, and tempting refactors go under `## Notes` in the plan as one line each — not into this PR. Tick each task box and update the `## Progress` line as the work lands, in the same commit as the work, so an interrupted session knows exactly where it stopped.

5. **Prove the Demo line before opening the PR.** The subagent runs the exact command, URL, or click path the phase names, plus the repo's own checks — `make build` / `make test` / `make lint` when a Makefile has those targets, otherwise the project's native commands. If the Demo does not do what the phase promised, the phase is not done.

   **Prove it locally, and stop before anything shared.** The demo runs against a local or disposable environment — a dev server, a test database, a scratch account. If it needs a host, database, or account nobody can throw away — a deployed URL, a shared or production database, an admin login — stop and ask the user first, naming what it would change. Never open a credential file (`.env*`, `prod.env`, a secrets store) to make a demo runnable: an unset `DATABASE_URL` is a stop sign, not a puzzle, and sourcing production config turns a pre-review proof into an unreviewed production change. The plan's rollout steps are the user's to run after merge, not yours to run as proof.

   **A deferred Demo is not a demo to invent.** When the phase says `**Demo:** deferred`, run the repo's checks, report that this phase's verification is deferred to the feature's end-to-end check, and move on. After the last phase merges, hand the user the plan's `## Rollout` steps and that check to run themselves. If a phase names no Demo at all and no deferral, ask the user how they want it verified before opening the PR — a demo that cannot run locally is a planning bug, so say so instead of working around it.

6. **Open the PR against the integration branch, with a short, feature-focused body.** Base it explicitly (`gh pr create --base integrate/<plan-name>`) — a phase PR never targets `main`. Imperative title, a `## Summary` of what this phase gives the user with bullets proportional to what the subagent reported, and a line naming the phase number and plan file. No test plan, no checklist, no co-author line. If `gh` or a GitHub remote is unavailable, stop at the pushed branch, say so, and skip to rule 11 — do not fake a review cycle.

7. **Review the PR in a subagent.** Use the repo's review skill if one is installed, invoked as `review-code` with target `pr <number> --sub`; otherwise spawn a subagent to review that PR's diff for correctness, security, resource, and performance defects and to rate each finding by severity, likelihood, and whether it is worth fixing. Relay its report as-is. Do not re-review its findings yourself — reading the whole diff back into this session is what the subagent exists to avoid.

8. **Fix only what is worth fixing.** Not everything a review prints deserves a commit:

   | Verdict in the report                | Action                                                                                                                  |
   | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
   | Worth fixing: Yes                    | Fix it in this PR                                                                                                       |
   | Judgment call                        | Fix if the effort is Trivial or Small **and** it lives in this phase's scope; otherwise log it in the plan's `## Notes` |
   | Worth fixing: No / Low severity nits | Leave it — say you left it                                                                                              |

   Fixes land as their own commits so the second review can see what changed. Then say in one line which findings you skipped and why; a silently dropped finding reads as a finding that never existed.

9. **Always run the second review, even when the first was clean.** Fixes are new, unreviewed code, and that is exactly where the next bug is. Point round 2 at the same PR after the fix commits land, and apply rule 8 to its findings the same way. Stop at two rounds — if round 2 still surfaces must-fix findings after fixing, the phase is too big; say so and let the user decide rather than looping a third time.

10. **Merge only when all four hold:** the demo passes, both review rounds ran, no `Yes` finding is left unfixed, and CI is green. Merge it into the integration branch with a merge commit — never squash, because the per-phase history is the record of how the feature was built — then delete the phase branch and return to an up-to-date integration branch before the next phase.

11. **Report the phase in one short block, then start the next one.** PR link, tasks completed, findings fixed, findings deliberately skipped, and the demo the user can run themselves. Continue to the next phase without asking, unless the user said to stop or rule 12 fired. After the last phase, go to rule 13.

12. **When the build proves a locked decision wrong, stop and say so.** Name the decision, what the code showed, and which later phases it invalidates. The user amends the plan; you do not quietly re-plan around their choice.

13. **The last merge is the user's.** When every phase has merged into the integration branch, open one PR from it to `main` — a summary of the feature, the phase PRs it contains, and the exact commands or click paths the user can run to verify it, ending with the plan's `## Rollout` steps. If `main` has moved since the integration branch was cut, merge `main` into the integration branch (merge commit, never squash) and re-run the repo's checks before handing it over. Then stop: do not review it, do not merge it. The user verifies the feature end to end and merges that PR themselves.

## Verification procedure

Before merging any phase's PR, check:

1. **Every task box for this phase is ticked** and the `## Progress` line matches the real count.
2. **The demo was actually run** after the last fix commit — not just before the first review — or the phase's Demo says `deferred` and you said so in the report.
3. **Two review rounds happened on this PR**, both in a subagent, the second after the fix commits.
4. **No `Yes` finding is unfixed**, and every skipped `Judgment call` has a one-line reason recorded.
5. **Every code change was made in a subagent** and this session never read the diff — only the subagent reports.
6. **The PR targeted the integration branch**, not `main` — the only PR into `main` is the final one, and the user merges that.
7. **Nothing shared was touched** — the demo ran locally, and no production database, deployed host, or credential file was read or written without the user saying yes first.
