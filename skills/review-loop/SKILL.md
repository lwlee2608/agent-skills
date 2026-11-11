---
name: review-loop
description: Use only when the user explicitly asks to review and fix in a loop until clean. Not for plain reviews (use review-code); never invoke proactively.
argument-hint: "[diff|pr <number>|all|<path>] [--commit each|end] [-2o] [--merge]"
user-invocable: true
---

# Review Loop

Review, fix, re-review until a round finds nothing worth fixing. Fixes are new code — they need their own review.

## Before round 1

If the target is empty or bare `pr` and the branch has no PR, ask whether to push and open one. Yes: push (branch first if on the default branch), open it with `gh-create-pr`, review it. No: review `diff`, no push.

## Rules

1. **Review in a fresh subagent every round.** Invoke `review-code` with `<target>` (default `diff`). If `review-code` is missing, spawn a subagent to review for correctness, security, resource, and performance defects, rating each finding Yes / Judgment call / No for worth fixing. Never review your own fixes inline.

2. **Pass `-2o` to round 1 only.** Round 1 reviews the full change; later rounds review small fix diffs, where another agent adds cost but little coverage. Its Final Call reads code before any fixes exist, so it does not break rule 1.

3. **Use `diff` from round 2 for every target, including paths.** GitHub does not see unpushed fixes, re-reviewing the whole codebase wastes context, and path-scoped reviews can miss fixes in related files. For `pr <number>`, check out the PR first.

4. **Fix every Yes; fix a Judgment call only if Trivial or Small.** Skip No. When a round has a Final Call, act on it instead: Fix → fix, Optional → fix only if Trivial or Small, Skip → skip. The reviewer has not seen this session: skip a finding that contradicts a decision you can quote from the user, plan, or issue, never your own choice. Leave it open if Critical or High. Do not re-fix or re-argue a skipped item when a later round raises it again.

5. **Run the repo's checks after each round's fixes** (`make build` / `make test` / `make lint`, else native commands). Fix breakage before the next review.

6. **Stop when a round has nothing new to fix.** Cap at 5 rounds; round 5 is review-only, even if it finds actionable issues. Do not edit after that review — hand the open findings to the user. If a fixed finding comes back in any round, stop fixing and report the open findings. When the loop stops, check every checklist item in the linked issue against the code; find it from the target PR or the current branch's PR (`gh pr view --json closingIssuesReferences`), whatever the target; an item not done is an open finding unless a stated reason drops it.

7. **Commit each fix unless told otherwise.** `--commit each` (default) — one commit per fixed finding. `--commit end` — one commit after the loop stops. Never push, except under `--merge` (rule 8). On the default branch, branch before the first commit — otherwise `diff` anchors at HEAD and committed fixes drop out of the next review.

8. **With `--merge`, merge only a clean loop.** Merge only if no findings are open and checks pass; otherwise skip it and say why. If the branch has no PR or `merge-pr` is missing, say so and stop without a push. Otherwise push, then merge its PR by reading and following `merge-pr`'s SKILL.md. The Skill tool refuses it because it is user-only; the flag is the user's go-ahead.

9. **Report at the end:** rounds run and why it stopped, fixes (`path:line` — what changed), skipped findings with a reason each, open findings, check results, and the merge result under `--merge`.
