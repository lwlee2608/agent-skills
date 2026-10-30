---
name: build-feature
description: Use when the user asks to build a feature end to end from a description, without a plan file. A worker subagent builds it and opens a PR to main, then a review loop fixes and merges it.
argument-hint: "<feature description>"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature

Hand one feature to a fresh worker, then review, fix, and merge its PR. The worker builds on a clean context, and you keep yours for the review loop.

```
you ─┬─ worker ── feat/<slug> off main: build, verify, PR ──▶ main
     └─ review-loop pr <n> [--second-opinion] --merge
          fresh reviewer per round ── you fix ── clean ── merge
```

## Rules

1. **Confirm the user didn't mean the plan flow.** This skill used to build phased plan files; that flow is now `implement-plan-feature`. If the argument is a path to an existing file, or there is no argument and `plans/` holds a plan, ask whether they meant `implement-plan-feature`. If yes, read its SKILL.md and follow it with the same argument; their answer is the go-ahead. If it isn't installed, say so and stop.

2. **Take the spec from the argument, never memory.** If it is missing, or leaves open a choice that changes the code, ask before spawning. Nothing stops for the user before merge, so a wrong guess ships to `main`. A feature that needs phases or several design decisions belongs in `plan-feature`, then `implement-plan-feature`; say so and stop.

3. **Ask which model and effort the worker uses, and whether the review loop gets `--second-opinion`,** in one `AskUserQuestion` call. Recommend your model at one effort step below yours, and the second opinion on. Read your effort from the environment; never guess it.

4. **Start from a clean, up-to-date `main`.** If the working tree is dirty, stop and say so. The worker builds in this checkout, and the review loop must see only its commits.

5. **Spawn one worker to build, verify, and open the PR.** No subagent tool? Stop and tell the user to install one; never build your own spawner. Block on the runtime's wait, never poll. Brief the worker with:
   - The spec verbatim and the branch `feat/<slug>`, cut from `main`.
   - Scope: build only what the spec asks. Unrelated bugs and refactors go in its report, not the code.
   - Verify: run the repo's checks plus proof the feature works, such as a test that fails without it or a run against a local fixture or dev server. "It compiles" is not proof. Use something disposable; if proof needs a deployed host, shared database, or credentials, stop and ask.
   - PR: target `main`, using `gh-create-pr` if installed. Otherwise an imperative title and a `## Summary` only, with no test plan or co-author line. Without `gh` or a GitHub remote, stop at the pushed branch.
   - Report: PR number, what it ran, and what it could not prove.

6. **Run the review loop yourself, not in the worker.** A subagent can't reliably spawn its own reviewers, and the loop needs a fresh reviewer each round. Once the worker reports, check out the PR branch and run `review-loop` with `pr <number> --merge`, plus `--second-opinion` if picked. The user invoking this skill is the explicit ask `review-loop` requires. If `review-loop` is missing, stop at the open PR and say so.

7. **Report in one block:** PR link, the worker's verification, the loop's rounds, fixes, skipped and open findings, and the merge result. If the loop did not merge, say why and what is left for the user.

**On Pi,** spawn through `subagent` from `@lwlee2608/pi-subagent`, then `wait` on the run ID:

```json
{"action":"start","agent":"worker","lifetime":"once","label":"<slug>","model":"<provider/model>","effort":"<effort>","task":"<brief>"}
```

Pass the picked model and effort; an unsupported pick fails instead of falling back. `reason: "timeout"` is not failure; wait again. `reason: "attention"` means the worker asked a question: `reply` if the answer is within your authority, else ask the user.
