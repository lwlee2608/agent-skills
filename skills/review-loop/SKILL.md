---
name: review-loop
description: Use when the user asks to review code and fix the findings in a loop until clean. Reviews with the review-code skill in a fresh subagent each round, fixes what is worth fixing, and re-reviews until nothing is left to fix.
argument-hint: "[diff|pr <number>|all|<path>] [--commit each|end]"
user-invocable: true
disable-model-invocation: true
---

# Review Loop

Review, fix, re-review until a round finds nothing worth fixing. Fixes are new code — they need their own review.

## Rules

1. **Review in a fresh subagent every round.** Invoke `review-code` with `<target> --sub` (default target `diff`). If `review-code` is missing, spawn a subagent to review for correctness, security, resource, and performance defects, rating each finding Yes / Judgment call / No for worth fixing. Never review your own fixes inline.

2. **Switch `pr` and `all` to `diff` from round 2.** GitHub does not see unpushed fixes, and re-reviewing the whole codebase wastes context. For `pr <number>`, run `gh pr checkout <number>` first.

3. **Fix every Yes; fix a Judgment call only if Trivial or Small.** Skip No. Do not re-fix or re-argue a skipped item when a later round raises it again.

4. **Run the repo's checks after each round's fixes** (`make build` / `make test` / `make lint`, else native commands). Fix breakage before the next review.

5. **Stop when a round has nothing new to fix.** Cap at 5 rounds. If the cap hits, or a fixed finding comes back, stop fixing and hand the open findings to the user.

6. **Commit only as the user chose.** `--commit each` — one commit per fixed finding. `--commit end` — one commit after the loop stops. No flag — leave fixes in the working tree. Never push. On the default branch, branch before the first commit — otherwise `diff` anchors at HEAD and committed fixes drop out of the next review.

7. **Report at the end:** rounds run and why it stopped, fixes (`path:line` — what changed), skipped findings with a reason each, open findings, and check results.

## Common mistakes to watch for

- **Reviewing `pr <number>` every round** — the fixes never get reviewed.
- **Fixing No-rated nits** to make a round "clean" — scope creep.
- **Stopping right after a fix round** — the fixes need their own review.
