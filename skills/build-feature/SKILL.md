---
name: build-feature
description: Use when the user asks to build a feature end to end from a description, without a plan file. A worker subagent builds it and opens a PR to main, then a review loop fixes and merges it.
argument-hint: "<feature description>"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature

A fresh worker builds the feature and opens a PR; you keep your context for the review loop that fixes and merges it.

```
you ─┬─ worker ── feat/<slug> off main: build, verify, PR ──▶ main
     └─ review-loop pr <n> [--second-opinion] --merge
```

## Rules

1. **Check for the old plan flow.** Phased plans moved to `implement-plan-feature`. If the argument is an existing file, or is empty while `plans/` holds a plan, ask if the user meant that. If yes, read its SKILL.md and follow it; if it isn't installed, say so and stop.

2. **Take the spec from the argument, never memory.** Nothing stops for the user before merge, so ask before spawning if the spec is missing or leaves open a choice that changes the code. If it needs phases or several design decisions, point to `plan-feature` and stop.

3. **Start from a clean, up-to-date `main`.** Stop if the working tree is dirty: the worker builds in this checkout, and the loop must see only its commits.

4. **Ask in one `AskUserQuestion` call** which model and effort the worker uses, and whether the loop gets `--second-opinion`. Recommend your model one effort step below yours, and the second opinion on. Read your effort from the environment; never guess it.

5. **Spawn one worker; never build your own spawner.** No subagent tool? Tell the user to install one. Block on the runtime's wait, never poll. Brief the worker with:
   - The spec verbatim and the branch `feat/<slug>` off `main`.
   - Scope: only what the spec asks. Unrelated bugs and refactors go in the report.
   - Verify: the repo's checks plus proof the feature works, such as a test that fails without it or a run against a local fixture. "It compiles" is not proof. If proof needs a deployed host, shared database, or credentials, stop and ask.
   - PR to `main` via `gh-create-pr` if installed, else an imperative title and a `## Summary` only. Without `gh` or a GitHub remote, stop at the pushed branch.
   - Report: PR number, what it ran, what it couldn't prove, and unrelated issues noted.

6. **Run the review loop yourself, not in the worker.** A subagent can't reliably spawn the fresh reviewer each round needs. On the PR branch, run `review-loop` with `pr <number> --merge`, plus `--second-opinion` if picked. Invoking this skill is the explicit ask `review-loop` requires. If it is missing, stop at the open PR.

7. **Report in one block:** PR link, the worker's verification and noted issues, the loop's rounds, fixes, skipped and open findings, and the merge result, or why it didn't merge.

8. **On Pi, spawn through `subagent` from `@lwlee2608/pi-subagent`,** then `wait` on the run ID:

   ```json
   {"action":"start","agent":"worker","lifetime":"once","label":"<slug>","model":"<provider/model>","effort":"<effort>","task":"<brief>"}
   ```

   An unsupported model or effort fails instead of falling back. `reason: "timeout"` is not failure; wait again. `reason: "attention"` means the worker asked a question: `reply` if it's within your authority, else ask the user.
