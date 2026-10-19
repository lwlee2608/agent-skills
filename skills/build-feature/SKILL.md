---
name: build-feature
description: Use when implementing a phased feature plan file. Builds each phase on its own branch and PR into a feature integration branch, reviews and fixes in rounds, merges, then runs the plan's demo and leaves the final merge to main to the user.
argument-hint: "[<path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Build a Feature, Phase by Phase

One phase, one PR, reviewed and fixed in rounds before merge. A feature built in one branch can't be tried, and code merged after one review pass merges its fixes unreviewed.

```
main
 └─ integrate/<plan>                         cut once, before the first phase
     ├─ <plan>-phase-1 ──PR──▶ integrate     build, verify, review x2-3, fix, merge
     ├─ <plan>-phase-2 ──PR──▶ integrate
     ├─ <plan>-phase-N ──PR──▶ integrate
     └──────────────────PR──▶ main           demo, then the user merges

one phase: feat/<plan> ──PR──▶ main          no integrate branch
```

**Start from the plan file, never memory.** Take the path from the argument, or look under `plans/` and ask if several match. Re-read it each phase. If any decision is `_open_`, stop and send the user back to planning. Before phase 1, check every Verify line and `## Demo`: a phase with no proof and no deferral is a planning bug, cheapest to raise now.

**Branch as the diagram shows.** Cut `integrate/<plan-name>` from up-to-date `main` and push it, or reuse it if it exists. Every phase branches from it and targets it, so `main` never holds half a feature. A one-phase plan skips it: branch `feat/<plan-name>` off `main`, and after the demo stop at the green PR for the user to merge.

**Start at the first phase with unchecked boxes, and build only its tasks.** Never pull work forward from a later phase, even three lines; the boundary keeps the PR reviewable. Unrelated bugs and tempting refactors become a one-line note in the plan. Tick boxes and update `## Progress` in the same commit as the work.

**Resume, don't restart.** First look for open PRs against the integration branch. An open PR for an unmerged phase means you are mid-cycle; its commits and review comments show which rounds ran. Outside solo mode, continue the phase's worker if the runtime still has it. Otherwise say so, and brief a fresh worker from the plan and PR.

**Show the route before any work.** Once you know where you stand, print the flow as a plain-text diagram from the plan's phases, merged PRs, and open PRs. Mark each step done, in progress, or pending, so the user sees what is left. With `Blocked by:` lines, group phases into waves: a wave holds the phases whose blockers all sit in earlier waves. Name each phase's blockers, since a phase starts once its own blockers merge, not the whole wave before it. Without them, list phases in order. A one-phase plan shows `feat/<plan>` instead of the integrate branch.

```
plans/<plan>.md
main
 └─ integrate/<plan>
     ├─ wave 1
     │   └─ [x] phase 1  <title>   merged #12
     ├─ wave 2
     │   ├─ [~] phase 2  <title>   PR #14, review round 2
     │   └─ [~] phase 3  <title>   building
     ├─ wave 3
     │   └─ [ ] phase 4  <title>   blocked by 2, 3
     ├─ [ ] demo
     └─ [ ] final PR ──▶ main      user merges
```

**Ask how to build before phase 1,** with `AskUserQuestion`. Record the answers as `**Build mode**` under Decisions so a resume keeps them. A one-phase plan skips this and builds solo.
- **Orchestrator** `(Recommended)` — a fresh worker subagent per phase, so phase 6 doesn't run on phase 1's context. Phases whose `Blocked by:` phases have merged run at once, each worker in its own git worktree. Without `Blocked by:` lines, run one at a time. Parallel workers tick only their own boxes; you update `## Progress` at each merge.
- **Solo** — you build every phase, with a fresh reviewer subagent per round. Later phases run on a crowded context.

Show each mode's diagram in its option's `preview`. If the question tool has no preview, print both diagrams before asking.

```
Orchestrator
you ─┬─ worker 1 ── phase 1 ── reviewers
     ├─ worker 2 ── phase 2 ── reviewers
     └─ worker 3 ── phase 3 ── reviewers
fresh context per phase; unblocked
phases run in parallel

Solo
you ─┬─ phase 1 ── reviewers
     ├─ phase 2 ── reviewers
     └─ phase 3 ── reviewers
one context, grows each phase
```

Then, in one more call, ask which model each subagent role uses: the reviewer always, the worker only in Orchestrator mode. Recommend your own model. If the spawn tool takes an effort parameter, ask effort too: reviewer at yours, worker one step down (`xhigh`→`high`, `high`→`medium`). Your effort is not in your context, so never guess it; in Claude Code, read `$CLAUDE_EFFORT`. If you cannot find it, offer the levels without a recommendation. If the spawn tool has no effort parameter, say once that subagents run at their agent definition's effort.

**No subagent tool?** Stop and tell the user to install one. Never build your own spawner. **On Pi,** read `pi.md` beside this file before asking how to build.

**Workers build; you orchestrate.** A phase's code and verification stay with its worker: it cuts the phase branch, builds, verifies, opens the PR, and applies review fixes. You own the integration branch, reviews, merges, reports, and the demo. Brief the worker with the plan path, its phase, and this skill's rules on scope, verifying, PRs, fixes, and locked decisions. Keep the same worker for every review round by messaging it (e.g. `SendMessage`); it already holds the diff. Relay each review report that has findings; a clean round needs no message. In solo mode, you are the worker.

```
phase N
  worker W ── spawned once: builds, verifies, opens PR
     │  round 1  reviewer R1 (new) ──report──▶ you ──relay──▶ W fixes, commits
     │  round 2  reviewer R2 (new) ──report──▶ you ──relay──▶ W fixes, commits
     │  round 3  reviewer R3 (new) ──report──▶ you ──relay──▶ W fixes, commits
     ▼
  merge ── W retired; phase N+1 gets a new worker
```

**Verify locally before the PR.** Run the repo's checks plus proof the phase does what it promised. Proof is the plan's Verify line; failing that, a test that fails without this phase's code, or a run against a local fixture or dev server. "It compiles" is not proof.
- Use something disposable. If proof needs a deployed host, shared database, or admin login, stop and ask, naming what it would change. Never open a credential file to make it runnable.
- For a `deferred` Verify line (older plans say `**Demo:**`), run the checks, say the proof is deferred to the demo, and move on. Don't invent one.
- For a step that needs the user's own device or personal account, with no scratch account possible, run the rest, defer that step to the demo without asking, and name it in the phase report.

**Open the PR against the integration branch, never `main`.** Title it `Phase <n>: <imperative title>`. The body is a `## Summary` of what the user gains, bullets in proportion to the change, and the plan file path. No test plan, checklist, or co-author line. Without `gh` or a GitHub remote, stop at the pushed branch and say so; don't fake a review cycle.

**Review in a new subagent every round,** never reused and never the writer, who is the last to spot what it assumed. Use the repo's review skill if installed, as `review-code` with target `pr <number> --sub`. Otherwise have the subagent review the diff for correctness, security, resource, and performance defects, rating severity, likelihood, and worth-fixing. Ask for plain prose; an output schema fails the task before the review starts. Block on the runtime's wait, never poll. Relay the report as-is.

**Run two or three rounds** on the same PR, each after the previous fix commits land. Round 2 always runs, even after a clean round 1, because a fresh reviewer catches what the first missed. Round 3 runs only if round 2 produced fixes. Three is the cap: if round 3 leaves a worth-fixing High or Critical finding, stop before merging, since the phase is too big to converge. Report it with what you would do, and ask the user. Otherwise fix, re-verify, merge, and note in the phase report that those last fixes merged unreviewed.

**Fix only what's worth fixing.** Fix every worth-fixing finding. Fix a judgment call if it is small and in this phase's scope; otherwise log it in the plan. Leave nits. Commit fixes separately so the next round sees them. Name what you skipped in one line; a silently dropped finding reads as one that never existed.

**Merge only when all four hold:** verification passes after the last fix commit, the required rounds ran, no worth-fixing finding is left, and CI is green. Wait on CI with one blocking call, not a poll loop. If the PR is behind the integration branch, merge it in and re-verify first. Use a merge commit, never squash; the per-phase history is the record. Then delete the phase branch and return to an up-to-date integration branch.

**Report each phase in one block, then start the next** without asking, unless the user asked you to pause. Include the PR link, tasks done, findings fixed and skipped, and what you ran.

**A locked decision proved wrong stops the build.** Name the decision, what the code showed, and which later phases it invalidates. The user amends the plan; never quietly re-plan around their choice.

**Run the demo once at the end, exactly as the plan says.** After every phase merges, run `## Demo` and report what you saw. `none` skips to the final PR. If you can't run it yourself, hand the user the steps and wait. Never invent a demo or stage one per phase. Add every deferred user-only Verify step to the handoff. If the plan has no `## Demo` (older plans), ask, record the answer in the plan, then run it. A broken demo gets fixed in the phase that owns it, through the same branch, review, and merge cycle.

**Open the final PR from the integration branch to `main`** with the feature summary, the phase PRs, the demo and its result, any deferred Verify steps still unrun, commands the user can run, and any post-merge steps from the plan. If `main` moved, merge it in and re-run the checks. Then stop; the user merges that PR.
