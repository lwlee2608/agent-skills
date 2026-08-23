---
name: plan-feature
description: Use when planning a feature too big to hold in one session. Settles every open decision up front by asking the user, locks the answers into one markdown plan file, then breaks the work into phases of user-testable slices with task checkboxes.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Plan a Feature

Big features go wrong two ways: the agent guesses at decisions that were the user's to make, and it splits the work by layer so the user sees nothing until the last phase. This skill settles every decision first, then cuts the work into slices the user can try one at a time.

The plan lives at `plans/<feature-slug>.md`, unless the repo already keeps design docs elsewhere or the user names a directory. If a plan already covers this feature, resume it — don't re-chart.

Planning runs in two stages, in order. Never start stage 2 while a question in stage 1 is open.

## Stage 1 — Settle every decision

1. **Read the code before asking anything.** Find the files the feature touches, the existing patterns it must match, and the libraries already available. An option you offer must be one the codebase can actually take.

2. **Answer for yourself whatever the codebase or docs can answer.** Library support, existing schema, current endpoints, how a neighbouring feature did it — these are research, not decisions. Never ask the user something you could have read. Mark them `` `research` `` in the plan so the user can see what you settled alone.

3. **Ask the user everything else, in batches.** `AskUserQuestion` takes up to 4 questions per call — use full batches instead of one question per turn. Each question gets 2-4 concrete candidate answers, the recommended one first, labelled `(Recommended)`. Put the real trade-off in each option's description, not marketing.

4. **Keep asking until nothing is open.** After each batch, new questions usually appear — the answer to one exposes the next. Loop until you have no open question worth asking, then say so plainly.

   Write the plan file as you go, not at the end. Record answers as they land and open questions with no answer, so an interrupted session resumes from the file instead of re-researching:

   ```markdown
   - **Where do retries belong?** — In the transport client, not the handler.
   - **Which queue backend?** — _open_
   ```

5. **State disagreement before locking, not after.** If the user picks something you think is wrong, say why in one or two lines. If they confirm, record their choice and move on.

## Stage 2 — Cut the work into testable phases

6. **Every phase must be something the user can run and see.** A phase ends with new behaviour they can exercise themselves. If you cannot write the **Demo** line — the exact command, URL, or click path that proves it works — it is not a phase.

7. **Never split phases by layer.** `Backend`, `Frontend`, `Database`, `API`, `Tests`, `Refactor` as phase names are all the same bug: the user is blind until the final phase, and integration problems surface last. Slice vertically — each phase cuts through every layer it needs.

   ```
   Bad — layer slices, nothing usable until the end
     Phase 1  Backend    [db][api]............  user sees nothing
     Phase 2  Frontend   ...........[ui][wire]  everything lands at once

   Good — feature slices, each one usable
     Phase 1  Log in            [db][api][ui]   user has an account
     Phase 2  Generate an image [db][api][ui]   user makes an image
     Phase 3  Animate it        [db][api][ui]   user makes a clip
   ```

8. **Name a phase by what the user gains.** "Log in and see an empty library" is a phase name. "Auth layer" is not.

9. **Order phases so the earliest is the smallest visible thing.** Each later phase builds on what already runs. Prefer 3-6 phases; if you have more than 8, the slices are too thin.

10. **Tasks are work, not questions, and start unchecked.** Imperative, one sitting each, naming the file where it is known: `- [ ] Add source_generation_id to generations (internal/db/migrations)`. Ticking them is the build — a separate request.

11. **Locked decisions stay locked.** If building proves one wrong, amend the Decisions section explicitly and note which phases it invalidates. Never quietly re-plan around a decision the user made.

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

### Phase 1 — <what the user gains>
<one line: what they can do after this that they could not before>
- [ ] <task>
- [ ] <task>
- [ ] <task>
**Demo:** <exact command, URL, or click path that proves it>

### Phase 2 — <what the user gains>
...

## Notes
<domain context, constraints, standing preferences>

## Out of scope
<ruled out, with a one-line reason>
```

## Verification procedure

Before handing the plan over, check:

1. **No open questions** — no `_open_` entry is left under Decisions, and no answer is `TBD`, "to be confirmed", or hedged. An `_open_` entry is fine mid-session; it is not fine when handing the plan over.
2. **Nothing decided that was the user's to decide** — every `research` mark is a fact you read, not a preference you picked.
3. **Demo line per phase** — each one names a command, URL, or click path a person can follow without reading the code.
4. **No layer names** — no phase is called backend, frontend, database, API, tests, or refactor.
5. **Vertical cut** — each phase's tasks touch the layers that phase needs, not one layer across all phases.
6. **Counts match** — the Progress line matches the actual task boxes.

## Common mistakes to watch for

- **Asking one question per turn.** Batch up to 4. A drip of single questions makes settling a plan feel like an interrogation.
- **Asking what the code already answers.** "Does the library support X?" is something to go and read, then report.
- **A "foundations" or "setup" first phase.** Scaffolding with nothing to see is a layer slice wearing a different name. Fold it into the first real feature slice.
- **Tasks disguised as decisions.** "Add the retry handler" is a task. "Where do retries belong?" is a decision.
- **Phases that only a developer can verify.** "Unit tests pass" is not a demo. The user must be able to see the behaviour.
- **Writing tasks while a decision is still open.** The task list will be wrong, and rewriting it costs more than waiting.
