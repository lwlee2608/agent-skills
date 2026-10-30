---
name: build-feature
description: Use when the user asks to build a feature end to end from a description, without a plan file. A worker subagent builds it and opens a PR to main, fresh reviewers check it in rounds, the worker fixes, and you merge.
argument-hint: "<feature description>"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature

A fresh worker builds the feature and fixes review findings; you run the reviews and merge. Fixes need their own review, so reviews run in rounds.

```
worker W ── spawned once: feat/<slug> off main, build, verify, PR ──▶ main
   │  round 1  reviewer R1 (new) ──report──▶ you ──relay──▶ W fixes, commits
   │  round 2  reviewer R2 (new) ──report──▶ you ──relay──▶ W fixes, commits
   │  round 3  only if round 2 had fixes
   ▼
merge ── W stopped
```

## Rules

1. **Check for the old plan flow.** Phased plans moved to `implement-plan-feature`. If the argument is an existing file, or is empty while `plans/` holds a plan, ask if the user meant that. If yes, read its SKILL.md and follow it; if it isn't installed, say so and stop.

2. **Take the spec from the argument, never memory.** Nothing stops for the user before merge, so ask before spawning if the spec is missing or leaves open a choice that changes the code. If it needs phases or several design decisions, point to `plan-feature` and stop.

3. **Start from a clean, up-to-date `main`.** Stop if the working tree is dirty: the worker builds in this checkout.

4. **Ask in one `AskUserQuestion` call** which model and effort the worker and the reviewer use. Recommend your model, your effort for the reviewer, and one step lower for the worker. Read your effort from the environment; never guess it.

5. **Spawn one worker and keep it for every fix round.** It holds the diff, so message it (e.g. `SendMessage`) instead of spawning another. No subagent tool? Tell the user to install one; never build your own. **On Pi,** read `pi.md` beside this file first. Brief the worker with:
   - The spec verbatim and the branch `feat/<slug>` off `main`.
   - Scope: only what the spec asks. Unrelated bugs and refactors go in its report.
   - Verify: rule 6. "It compiles" is not proof. If proof needs a deployed host, shared database, or credentials, stop and ask.
   - PR to `main` via `gh-create-pr` if installed, else an imperative title and a `## Summary` only. Without `gh` or a GitHub remote, stop at the pushed branch.
   - Report: PR number, what it ran, what it couldn't prove or run, and unrelated issues noted.

6. **Run slow checks only where the change is.** Fast checks run after the build and every fix commit. Slow ones (E2E, Playwright, integration tests that boot services or sleep) run only the cases covering what changed, new ones included: before the PR, and after each fix touching them. Before merge, run the full slow suite once if CI doesn't. A slow check skipped for missing env or services is not a pass; report it. Reviewers don't run slow checks.

7. **Review in a new subagent every round,** never reused and never the worker. Use `review-code` with `pr <number>` and no `--sub`, since the subagent is already fresh. Without it, have the subagent review for correctness, security, resource, and performance defects, rating severity, likelihood, and worth-fixing. Block on the runtime's wait, never poll.

8. **Run two or three rounds.** Round 2 always runs, since a fresh reviewer catches what the first missed. Round 3 runs only if round 2 produced fixes. If round 3 leaves a worth-fixing High or Critical finding, stop before merge and ask the user.

9. **Relay every report with findings to the worker; a clean round sends nothing.** The worker fixes every worth-fixing finding, and a judgment call only if small and in scope. It leaves nits and commits each fix separately. Name every skipped finding in one line.

10. **Merge only when** rule 6's checks pass after the last fix, the rounds ran, no worth-fixing finding is left, and CI is green; wait on CI with one blocking call. Use a merge commit, never squash. Delete the branch only after GitHub reports the PR merged; a chained delete once ran after a hung merge and closed the PR. Then stop the worker and return to an up-to-date `main`.

11. **Report in one block:** PR link, what ran and what was skipped, findings fixed and skipped per round, noted issues, and the merge result, or why it didn't merge.
