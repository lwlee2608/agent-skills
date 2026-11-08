# Review Loop

Review, fix, repeat until a review finds nothing new. At the end, check the linked issue's checklist. With `--merge`, merge only if nothing is open.

## Flow

```
 /review-loop [target] [--merge]
          │
          ▼
 ┌──────────────────────┐
 │ Round N: review      │  new subagent each round (review-code)
 │ (round 1: full diff, │  round 1 may add --second-opinion
 │  later: diff only)   │
 └─────────┬────────────┘
           ▼
     anything new to fix? ──no──────────────┐
           │yes                             │
           ▼                                │
 ┌──────────────────────┐                   │
 │ Fix findings         │  every Yes        │
 │                      │  Judgment call    │
 │                      │  if Trivial/Small │
 │                      │  skip No          │
 └─────────┬────────────┘                   │
           ▼                                │
 ┌──────────────────────┐                   │
 │ make build/test/lint │  fix breakage     │
 │ commit each fix      │                   │
 └─────────┬────────────┘                   │
           ▼                                │
     round 5, or old bug came back? ─yes─┐  │
           │no                           │  │
           └──► next round               ▼  ▼
                                   ┌──────────────┐
                                   │  LOOP STOPS  │
                                   └──────┬───────┘
                                          ▼
                     ┌────────────────────────────────────┐
                     │ gh issue view <linked issue>       │
                     │ check each checklist item vs code  │
                     │ not done, no reason given          │
                     │   → becomes an open finding        │
                     └──────────────┬─────────────────────┘
                                    ▼
                         --merge given?
                          │no        │yes
                          ▼          ▼
                       report   open findings or checks fail?
                                 │yes             │no
                                 ▼                ▼
                          skip merge,      push → follow merge-pr
                          say why                 │
                                                  ▼
                                           merge PR, then tick
                                           the done checklist
                                           items (merge-pr rule 3)
```

## Example

```
Issue checklist               Code after loop       Result
[ ] add endpoint              done                  ok
[ ] add migration             done                  ok
[ ] update docs               missing               open finding
[ ] add metrics               missing               open finding
                                                    │
                                                    ▼
                                    --merge blocked, both items reported
```

Clean code reviews alone don't mean the issue is done. The checklist check catches the missing work before the merge.

## Limits

- **Reports undone checklist items, doesn't fix them.** The check runs after the loop stops, so the items go back to you. Missing checklist work is usually real work, not a review fix.
- **No linked issue, no check.** A `diff` with no PR may have no issue to read.
- **Plain `/merge-pr` doesn't block.** On its own, it ticks the items that are done and leaves the rest unticked, but it still merges.
