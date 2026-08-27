---
name: build-feature
description: Use when implementing a feature plan file that is split into phases with task checkboxes. Builds one phase per branch, opens a PR against a feature-wide integration branch, reviews it twice in a subagent, fixes only what is worth fixing, then merges before starting the next phase. After the last phase it demos the whole feature the way the user asks, and leaves the final merge to main to them.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

Turn a phased plan into merged code. One phase is one PR, reviewed twice and fixed twice before it merges — because a plan built in one giant branch cannot be tested by the user, and code merged after a single review pass merges the fixes unreviewed. Every phase merges into one feature-wide integration branch, and only the user merges that branch into `main`.

```
main
 └─ integrate/<plan>                         cut once, before the first phase
     ├─ <plan>-phase-1 ──PR──▶ integrate     build, verify, review x2, fix, merge
     ├─ <plan>-phase-2 ──PR──▶ integrate
     ├─ <plan>-phase-N ──PR──▶ integrate
     └──────────────────PR──▶ main           demo the feature, then the user merges this one
```

```
for each phase in the plan:

  branch off integrate  →  build it here  →  verification passes  →  push  →  PR
                                                                        |
                   review #1 (subagent)  →  fix worth-fixing            |
                                                                        |
                   review #2 (subagent)  →  fix worth-fixing            |
                                                                        v
                   merge (merge commit)  →  back to integrate  →  next phase

after the last phase:  ask the user how to demo  →  run it  →  PR to main

you write the code; the reviews happen elsewhere and come back as reports
```

## Rules

1. **Start from the plan file, never from memory.** Take the path from the argument; otherwise look under `plans/` and ask which one if more than one matches. Re-read it at the start of every phase — it may have changed. If any decision is still `_open_`, stop and send the user back to planning: code written around an open decision is code they will throw away.

   Read every phase's verification line before you start phase 1. If a phase names no way to prove it works and no deferral, raise it now rather than when its PR is due — that is a planning bug, and it is cheapest to fix before any code exists.

2. **One feature, one integration branch; one phase, one branch, one PR.** Before the first phase, cut `integrate/<plan-name>` from an up-to-date `main` and push it — reuse it if it already exists. Every phase branches from it and every phase PR targets it, so `main` never holds half a feature. Build the first phase that still has unchecked boxes. Never pull work forward from a later phase, even when it is three lines and "right there" — the phase boundary is what makes the PR reviewable and its verification meaningful, and batching phases means the user cannot try phase 1 until phase 4 is written. Branch from an up-to-date integration branch, naming the branch after the plan and phase number.

3. **Write the code yourself; delegate only the reviews.** Cut the branch, then build the phase in this session — the plan, the code, and the verification stay in one head, which is what keeps a phase coherent. The review is the one thing that goes out to a subagent (rule 7), because a second reader who did not write the code is the point of a review.

   Apply the review fixes yourself too, in this session. You already have the diff in context; handing the findings to a subagent that has to re-read the phase from scratch buys nothing.

   Keep a phase to a small number of turns: batch independent reads and edits into one message instead of one call per file, and run long checks in the background and wait once rather than polling.

4. **Do the phase's tasks and nothing else.** Unrelated bugs, stale code, and tempting refactors go under `## Notes` in the plan as one line each — not into this PR. Tick each task box and update the `## Progress` line as the work lands, in the same commit as the work, so an interrupted session knows exactly where it stopped.

5. **Verify the phase before opening the PR — a demo is one way, not the only one.** Not every phase can be clicked through, and none has to be: what every phase owes is proof that it does what it promised, plus the repo's own checks — `make build` / `make test` / `make lint` when a Makefile has those targets, otherwise the project's native commands. The proof is the command, URL, or click path when the phase names one; otherwise a test that fails without this phase's code, a script run against a local fixture, or a request against a dev server. "It compiles" is not proof. If the proof does not show what the phase promised, the phase is not done. Save the demo for the finished feature (rule 13).

   Set the verification environment up in as few turns as possible: batch the independent commands, and free the ports it needs before starting anything on them rather than diagnosing the collision afterwards.

   **Prove it locally, and stop before anything shared.** Verification runs against a local or disposable environment — a dev server, a test database, a scratch account. If it needs a host, database, or account nobody can throw away — a deployed URL, a shared or production database, an admin login — stop and ask the user first, naming what it would change. Never open a credential file (`.env*`, `prod.env`, a secrets store) to make it runnable: an unset `DATABASE_URL` is a stop sign, not a puzzle, and sourcing production config turns a pre-review proof into an unreviewed production change. The plan's rollout steps are the user's to run after merge, not yours to run as proof.

   **Deferred is not proof to invent.** When the phase's `**Verify:**` (older plans say `**Demo:**`) says `deferred`, run the repo's checks, report that this phase's proof is deferred to the feature's end-to-end demo, and move on. If a phase names no verification and no deferral — and rule 1 did not already catch it — say plainly that it is a planning bug and ask the user how they want that phase verified, before opening its PR.

6. **Open the PR against the integration branch, with a short, feature-focused body.** Base it explicitly (`gh pr create --base integrate/<plan-name>`) — a phase PR never targets `main`. Title it `Phase <n>: <imperative title>` so the phase is readable from the PR list alone, then a `## Summary` of what this phase gives the user with bullets proportional to what the phase actually changed, and a line naming the plan file. No test plan, no checklist, no co-author line. If `gh` or a GitHub remote is unavailable, stop at the pushed branch, say so, and skip to rule 11 — do not fake a review cycle.

7. **Review the PR in a subagent — always, both rounds.** Use the repo's review skill if one is installed, invoked as `review-code` with target `pr <number> --sub`; otherwise spawn a subagent to review that PR's diff for correctness, security, resource, and performance defects and to rate each finding by severity, likelihood, and whether it is worth fixing. The reviewer must be a fresh subagent, not you: you wrote this code, so you are the last one who will spot what you assumed.

   **Hand off, then wait once — never poll.** Spawn the reviewer and block on the runtime's own wait or yield until it settles. A loop of waits that each come back "still running" learns nothing and re-sends this entire session on every turn. Ask for the report as plain prose; do not attach an output schema to the spawn — a malformed one fails the task before any review starts.

   Relay its report as-is, then apply rule 8.

8. **Fix only what is worth fixing.** Not everything a review prints deserves a commit:

   | Verdict in the report                | Action                                                                                                                  |
   | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
   | Worth fixing: Yes                    | Fix it in this PR                                                                                                       |
   | Judgment call                        | Fix if the effort is Trivial or Small **and** it lives in this phase's scope; otherwise log it in the plan's `## Notes` |
   | Worth fixing: No / Low severity nits | Leave it — say you left it                                                                                              |

   Fixes land as their own commits so the second review can see what changed. Then say in one line which findings you skipped and why; a silently dropped finding reads as a finding that never existed.

9. **Always run the second review, even when the first was clean.** Fixes are new, unreviewed code, and that is exactly where the next bug is. Point round 2 at the same PR after the fix commits land, and apply rule 8 to its findings the same way. Stop at two rounds — if round 2 still surfaces must-fix findings after fixing, the phase is too big; say so and let the user decide rather than looping a third time.

10. **Merge only when all four hold:** the phase's verification passes, both review rounds ran, no `Yes` finding is left unfixed, and CI is green. Merge it into the integration branch with a merge commit — never squash, because the per-phase history is the record of how the feature was built — then delete the phase branch and return to an up-to-date integration branch before the next phase.

11. **Report the phase in one short block, then start the next one.** PR link, tasks completed, findings fixed, findings deliberately skipped, and what was run to verify the phase. Continue to the next phase without asking, unless the user said to stop or rule 12 fired. After the last phase, go to rule 13.

12. **When the build proves a locked decision wrong, stop and say so.** Name the decision, what the code showed, and which later phases it invalidates. The user amends the plan; you do not quietly re-plan around their choice.

13. **Demo the finished feature, then hand the last merge to the user.** The demo happens once, when every phase has merged into the integration branch — that is the first point where there is a whole feature to show. Ask the user how they want it demonstrated with `AskUserQuestion`, offering concrete options drawn from the plan: a local run they drive themselves while you give them the steps, a scripted walkthrough you run and report, or the plan's end-to-end check. Do not pick for them. Whatever they choose must also cover every phase whose verification was deferred.

    Run what they picked and report what you saw. If it breaks, the fix belongs to the phase that owns it — same branch-review-merge cycle, not a patch straight onto the integration branch.

    Then open one PR from the integration branch to `main` — a summary of the feature, the phase PRs it contains, the demo you ran and its result, and the exact commands or click paths the user can run themselves, ending with the plan's `## Rollout` steps. If `main` has moved since the integration branch was cut, merge `main` into the integration branch (merge commit, never squash) and re-run the repo's checks before handing it over. Then stop: do not review it, do not merge it. The user merges that PR themselves.

## Verification procedure

Before merging any phase's PR, check:

1. **Every task box for this phase is ticked** and the `## Progress` line matches the real count.
2. **The phase was verified** after the last fix commit — not just before the first review — or its verification says `deferred` and you said so in the report.
3. **Two review rounds happened on this PR**, both in a fresh subagent, the second after the fix commits — you never stood in for the reviewer.
4. **No `Yes` finding is unfixed**, and every skipped `Judgment call` has a one-line reason recorded.
5. **The PR targeted the integration branch**, not `main` — the only PR into `main` is the final one, and the user merges that.
6. **Nothing shared was touched** — verification ran locally, and no production database, deployed host, or credential file was read or written without the user saying yes first.

Before opening the final PR to `main`, check one more:

7. **The feature was demoed the way the user chose**, covering every phase whose verification was deferred, and the PR body says what you ran and what happened.
