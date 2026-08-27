---
name: plan-feature
description: Use when planning a feature too big to hold in one session. Settles every open decision by asking the user, locks the answers into one markdown plan file, then cuts the work into phases the user can verify one at a time.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
---

# Plan a Feature

Big features go wrong two ways: the agent guesses at decisions that were the user's to make, and it splits work by layer so the user sees nothing until the last phase. Settle the decisions first, then cut vertical slices.

The plan lives at `plans/<feature-slug>.md`, unless the repo keeps design docs elsewhere or the user names a directory. If a plan already covers this feature, resume it.

Two stages, in order. Never start stage 2 while a stage 1 question is open — a task list written around an open decision gets thrown away.

## Stage 1 — Settle every decision

**Read the code first.** Find the files the feature touches, the patterns it must match, the libraries already there. An option you offer must be one the codebase can take.

**Answer for yourself whatever the code or docs can answer** — library support, existing schema, how a neighbouring feature did it. That is research, not a decision. Mark it `` `research` `` in the plan so the user sees what you settled alone. Never ask what you could have read.

**Ask the user everything else, in batches of up to 4** with `AskUserQuestion`. Each question gets 2-4 concrete answers, recommended one first, labelled `(Recommended)`, with the real trade-off in the description. Ask about decisions ("where do retries belong?"), not work ("add the retry handler") — work is stage 2.

**Settle how the finished feature gets demonstrated.** One demo per feature, at the end, once every phase has merged — `build-feature` runs whatever this says and invents nothing. Ask whether the user wants one at all and, if so, what it is: a local run they drive with your steps, a scripted walkthrough the agent runs and reports, or an end-to-end check. `none` is a valid answer and plenty of features deserve it. Record the choice under `## Demo`. The one case where `none` is unavailable is a feature with a deferred phase — the demo is that phase's only proof, so it must cover it.

**Keep asking until nothing is open.** Each answer usually exposes the next question. Write the plan file as you go, recording answers as they land and unanswered ones as `_open_`, so an interrupted session resumes from the file. If the user picks something you think is wrong, say why in a line or two; if they confirm, record it and move on.

Hand over only when no `_open_` entry is left and no answer is hedged or `TBD`.

## Stage 2 — Cut the work into phases

**Slice vertically, never by layer.** `Backend`, `Frontend`, `Database`, `Tests`, `Foundations`, `Setup` as phase names are all the same bug — the user is blind until the end and integration problems surface last. Each phase cuts through every layer it needs.

```
Bad — layer slices, nothing usable until the end
  Phase 1  Backend    [db][api]............  user sees nothing
  Phase 2  Frontend   ...........[ui][wire]  everything lands at once

Good — feature slices, each one usable
  Phase 1  Log in            [db][api][ui]   user has an account
  Phase 2  Generate an image [db][api][ui]   user makes an image
  Phase 3  Animate it        [db][api][ui]   user makes a clip
```

**Name a phase by what the user gains.** "Log in and see an empty library", not "Auth layer".

**Every phase carries a Verify line** naming exactly what proves it works: a command, a URL, a click path, or a test that fails without this phase's code. "Checks pass" is not a Verify line. If you cannot write one, it is not a phase.

**Verification must run locally** — a dev server, a test database, a scratch account. A Verify line naming a deployed URL, a shared database, or production credentials is a rollout step, not a proof; write it as one at the end of the plan for the user to run after merge. A phase with no local proof needs a fixture or seed script, not a production target.

**Some work can only be proven at the end.** Write `**Verify:** deferred — <why>` when a phase has no local surface of its own, and make sure the `## Demo` covers it. Deferral is for work with no local surface, never for work you have not thought through — two deferred phases in a row means the slices are wrong. If you cannot tell whether a phase is provable locally, that is a stage 1 question.

**Order phases so the earliest is the smallest visible thing**, each later one building on what already runs. Size each to one build session — write, verify, two rounds of review fixes, in one context. A phase touching twenty files is too big whatever it gives the user; cut it. Prefer 3-6 phases, and more than 8 means the slices are too thin — but a feature small enough to fit one session is one phase, so do not split it to hit a count.

**Parallelism, only when it pays.** If two phases share no dependency and no meaningful files, ask with `AskUserQuestion` whether to run them side by side as `2a`/`2b`, each with its own Verify line and a note of where they merge. If no pair qualifies, say the phases are sequential and move on — do not ask.

**Tasks are work, and start unchecked.** Imperative, one sitting each, naming the file where known: `- [ ] Add source_generation_id to generations (internal/db/migrations)`. Ticking them is the build — that is `build-feature`.

**Locked decisions stay locked.** If building proves one wrong, amend the Decisions section explicitly and name which phases it invalidates. Never quietly re-plan around a choice the user made.

## Plan file format

```markdown
# <Feature>

## Decisions
- **<question>** — <answer, one or two lines>
- **<question>** — <answer> `research`
- **<question>** — _open_   <-- only while stage 1 is running

## Progress
Phase 1 of 3 · 0/11 tasks

### Phase 1 — <what the user gains>
<one line: what they can do now that they could not before>
- [ ] <task>
- [ ] <task>
**Verify:** <command, URL, click path, or test — or `deferred — <why>`>

## Demo
<how the finished feature gets shown once every phase has merged — or `none`>
```

Add further sections the feature actually needs — context and constraints, steps to run against shared systems after merge, what was ruled out and why. Do not invent sections it does not need.
