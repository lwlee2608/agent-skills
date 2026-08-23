---
name: plan-feature
description: Use when planning a feature too big to hold in one session. Settles every open decision up front by asking the user, locks the answers into one markdown plan file, then breaks the work into phases of verifiable slices with task checkboxes.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
---

# Plan a Feature

Big features go wrong two ways: the agent guesses at decisions that were the user's to make, and it splits the work by layer so the user sees nothing until the last phase. This skill settles every decision first, then cuts the work into slices the user can try one at a time.

The plan lives at `plans/<feature-slug>.md`, unless the repo already keeps design docs elsewhere or the user names a directory. If a plan already covers this feature, resume it — don't re-chart.

Planning runs in two stages, in order. Never start stage 2 while a stage 1 question is open — a task list written around an open decision gets thrown away.

## Stage 1 — Settle every decision

1. **Read the code before asking anything.** Find the files the feature touches, the patterns it must match, and the libraries already available. An option you offer must be one the codebase can actually take.

2. **Answer for yourself whatever the codebase or docs can answer.** Library support, existing schema, current endpoints, how a neighbouring feature did it — these are research, not decisions. Never ask the user something you could have read. Mark them `` `research` `` in the plan so the user can see what you settled alone.

3. **Ask the user everything else, in batches.** `AskUserQuestion` takes up to 4 questions per call — use full batches, because a drip of one question per turn makes settling a plan feel like an interrogation. Each question gets 2-4 concrete candidate answers, the recommended one first, labelled `(Recommended)`. Put the real trade-off in each option's description, not marketing.

   Ask about decisions, not work. "Where do retries belong?" is a decision. "Add the retry handler" is a task, and tasks belong in stage 2.

4. **Keep asking until nothing is open.** Each answer usually exposes the next question. Loop until you have nothing left worth asking, then say so plainly.

   Write the plan file as you go, not at the end. Record answers as they land and open questions with no answer, so an interrupted session resumes from the file instead of re-researching:

   ```markdown
   - **Where do retries belong?** — In the transport client, not the handler.
   - **Which queue backend?** — _open_
   ```

5. **State disagreement before locking, not after.** If the user picks something you think is wrong, say why in one or two lines. If they confirm, record their choice and move on.

## Stage 2 — Cut the work into testable phases

6. **Every phase must be something you can prove works.** Aim for new behaviour the user can exercise themselves — that is what makes a slice worth cutting — but the proof does not have to be a click path. Each phase carries a **Verify** line naming exactly what shows the phase works: a command, a URL, a click path, or a test that fails without this phase's code. If you cannot write that line, it is not a phase. "Checks pass" is not a Verify line — name the command and what it should show.

   Save the demo for the end. There is one demo per feature, once every phase has merged, and `build-feature` asks the user how they want it done. Do not stage a demo per phase.

7. **Verification must run locally.** It runs against a dev server, a test database, a scratch account — something the user can re-run, get wrong, and run again. A Verify line naming a shared database, a deployed URL, or production credentials is not a proof, it is a rollout step: put it under `## Rollout`, where nobody can mistake it for one. Write it as a Verify line instead and the agent building the phase will run it before the code is even reviewed. If a phase has no local proof, it needs a seed script or a fixture, not a production target.

8. **Some work can only be proven at the end, and that is allowed.** When a phase has no local surface of its own — a migration that only matters against real data, an integration you cannot exercise without the third party — write `**Verify:** deferred — <why>` and cover it in the feature's `## Rollout` block, which names the one end-to-end check the user runs after every phase merges.

   Deferral is for work with no local surface, never for work you have not thought through. Two deferred phases in a row means the slices are wrong. And when you cannot tell whether a phase is provable locally, that is a stage 1 question — ask the user how they want to verify it rather than guessing. The same goes for the feature as a whole: if you cannot see how the finished feature would ever be demonstrated, ask in stage 1, not after four phases have merged.

9. **Never split phases by layer.** `Backend`, `Frontend`, `Database`, `API`, `Tests`, `Refactor` as phase names are all the same bug: the user is blind until the final phase, and integration problems surface last. A `foundations` or `setup` first phase is that bug wearing a different name — scaffolding with nothing to see, so fold it into the first real feature slice. Slice vertically instead: each phase cuts through every layer it needs.

   ```
   Bad — layer slices, nothing usable until the end
     Phase 1  Backend    [db][api]............  user sees nothing
     Phase 2  Frontend   ...........[ui][wire]  everything lands at once

   Good — feature slices, each one usable
     Phase 1  Log in            [db][api][ui]   user has an account
     Phase 2  Generate an image [db][api][ui]   user makes an image
     Phase 3  Animate it        [db][api][ui]   user makes a clip
   ```

10. **Name a phase by what the user gains.** "Log in and see an empty library" is a phase name. "Auth layer" is not.

11. **Order phases so the earliest is the smallest visible thing.** Each later phase builds on what already runs. Prefer 3-6 phases; if you have more than 8, the slices are too thin.

12. **Raise parallelism only when it pays.** A pair of phases qualifies only if both hold:
    - **No dependency.** Neither phase needs the other's schema, API, types, or new files. If B builds on what A introduces, B waits — starting it early means guessing at A's shape and rewriting later.
    - **Little overlap.** They touch mostly different files. Two phases editing the same modules will collide on merge, and reconciling the branches costs more than the parallel run saved.

    If no pair clears both bars, say the phases are sequential and move on — do not ask. When a pair does, ask with `AskUserQuestion` whether to run them side by side, naming the pair and any files they share.

    If the user agrees, split the phase numbers (`2a`, `2b`), give each branch its own Verify line, and record the flow as a diagram that names the merge point — Phase 3 starts only after both branches land:

    ```
    Phase 1 ──┬── Phase 2a  Generate an image ──┬── Phase 3  Animate an image
              │             internal/gen        │
              └── Phase 2b  Browse the images ──┘
                            internal/library
    ```

13. **Tasks are work, and start unchecked.** Imperative, one sitting each, naming the file where it is known: `- [ ] Add source_generation_id to generations (internal/db/migrations)`. Ticking them is the build — a separate request, handled by `build-feature`.

14. **Locked decisions stay locked.** If building proves one wrong, amend the Decisions section explicitly and note which phases it invalidates. Never quietly re-plan around a decision the user made.

## Plan file format

```markdown
# <Feature>

## Destination
<what success looks like, 1-2 lines>

## Decisions
- **<question>** — <the answer, one or two lines>
- **<question>** — <the answer> `research`
- **<question>** — _open_   <-- only while stage 1 is still running

## Progress
Phase 1 of 3 · 0/11 tasks

## Parallelism
<only when the user agreed — a diagram of which phases branch, and where they merge back>

### Phase 1 — <what the user gains>
<one line: what they can do after this that they could not before>
- [ ] <task>
- [ ] <task>
- [ ] <task>
**Verify:** <exact command, URL, click path, or test that proves it — or `deferred — <why>`>

### Phase 2 — <what the user gains>
...

## Notes
<domain context, constraints, standing preferences>

## Rollout
<steps against shared or production systems, for the user to run after merge — never part of a Verify line>
<the end-to-end check covering any phase whose Verify line was deferred>

## Out of scope
<ruled out, with a one-line reason>
```

## Verification procedure

Before handing the plan over, check:

1. **No open questions** — no `_open_` entry is left under Decisions, and no answer is `TBD`, "to be confirmed", or hedged. An `_open_` entry is fine mid-session; it is not fine at handover.
2. **Nothing decided that was the user's to decide** — every `research` mark is a fact you read, not a preference you picked.
3. **A Verify line per phase** — each names a specific command, URL, click path, or test, or says `deferred` with a reason and is covered by the `## Rollout` end-to-end check. No two consecutive phases defer.
4. **Every Verify line runs locally** — none names a production host, a shared database, or a credential the user would have to hand over.
5. **No layer names, and a vertical cut** — no phase is called backend, frontend, database, API, tests, refactor, foundations, or setup, and each phase's tasks touch the layers that phase needs rather than one layer across all phases.
6. **Counts match** — the Progress line matches the actual task boxes.
7. **Parallelism is earned or absent** — if the plan branches, the branches share no dependency and no meaningful files, and the diagram names where they merge. Otherwise there is no Parallelism section at all.
