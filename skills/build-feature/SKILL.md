---
name: build-feature
description: Use when the user asks to build a feature end to end from a description, without a plan file. A worker subagent builds it and opens a PR, fresh reviewers check it in rounds, and you merge.
argument-hint: "<feature description>"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature

A worker builds and fixes; you review in rounds, since fixes need review too, and merge.

```
worker W ── spawned once: feat/<slug> off main, build, verify, PR ──▶ main
   │  round 1  reviewer R1 (new) ──report──▶ you ──relay──▶ W fixes, commits
   │  round 2  reviewer R2 (new) ──report──▶ you ──relay──▶ W fixes, commits
   │  round 3  only if round 2 had fixes
   ▼
merge ── W stopped
```

## Rules

1. **Check for the old plan flow.** Phased plans moved to `implement-plan-feature`. If the argument is an existing file, or is empty while `plans/` holds a plan, ask if the user meant that. If yes, follow its SKILL.md; if not installed, say so and stop.

2. **Take the spec from the argument, never memory.** Ask before spawning if the spec is missing or leaves open a choice that changes the code. If it needs phases or several design decisions, point to `plan-feature` and stop.

3. **Start from a clean, up-to-date `main`.** Stop if dirty: the worker builds in this checkout.

4. **Ask in one `AskUserQuestion` call** which model and effort the worker and the reviewer use. Recommend your model, your effort for the reviewer, and one step lower for the worker. Read your effort from the environment; never guess.

5. **Spawn one worker and keep it for every fix round.** It holds the diff, so message it (e.g. `SendMessage`). No subagent tool? Tell the user to install one. **On Pi,** read `pi.md` beside this file first. Brief the worker with:
   - The spec verbatim and the branch `feat/<slug>` off `main`.
   - Scope: only the spec. Unrelated bugs and refactors go in its report.
   - Verify: rule 6. "It compiles" is not proof. If proof needs a deployed host, shared database, or credentials, stop and ask.
   - PR to `main` via `gh-create-pr`, else an imperative title and `## Summary` only. Without `gh` or a GitHub remote, stop at the pushed branch.
   - Report: PR number, what it ran, what it couldn't prove or run, and unrelated issues noted.

6. **Run slow checks only where the change is.** Fast checks run after the build and every fix. Slow ones (E2E, Playwright, integration tests that boot services) run only the cases covering the change: before the PR and after fixes touching them. Before merge, run the full slow suite once if CI doesn't. Skipped for missing env or services is not a pass; report it. Reviewers don't run slow checks.

7. **Review in a new subagent every round,** never reused and never the worker. Use `review-code pr <number>` without `--sub`; the subagent is already fresh. Without `review-code`, review for correctness, security, resource, and performance defects, rating severity, likelihood, and worth-fixing. Block on the wait, never poll.

8. **Run two or three rounds.** Round 2 always runs; a fresh reviewer catches what the first missed. Round 3 runs only if round 2 produced fixes. If round 3 leaves a worth-fixing High or Critical finding, ask the user before merge.

9. **Relay every report with findings to the worker; a clean round sends nothing.** The worker fixes worth-fixing findings, judgment calls only if small and in scope, leaves nits, and commits each fix separately. Name every skipped finding in one line.

10. **Merge only when** rule 6's checks pass after the last fix, the rounds ran, no worth-fixing finding is left, and CI is green (one blocking wait). Use a merge commit, never squash. Delete the branch only after GitHub reports the PR merged; a chained delete once ran after a hung merge and closed the PR. Then stop the worker and return to an up-to-date `main`.

11. **Report in one block:** PR link, what ran and was skipped, findings fixed and skipped per round, noted issues, and the merge result or why not.
