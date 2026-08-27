---
name: plan-feature
description: Use when planning a feature too big to hold in one session. Settles every open decision by asking the user, locks the answers into one markdown plan file, then cuts the work into phases the user can verify one at a time.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
---

# Plan a Feature

Two failure modes: guessing at decisions that were the user's, and slicing by layer so nothing is visible until the last phase. Settle decisions first, then cut vertical slices.

Plan lives at `plans/<feature-slug>.md` — unless the repo keeps design docs elsewhere, or the user names a directory. Plan already covers this feature? Resume it.

Stage 1 before stage 2, always. A task list written around an open decision gets thrown away.

## Stage 1 — Settle every decision

**Read the code first.** Files touched, patterns to match, libraries already there. Every option you offer must be one the codebase can take.

**Answer what the code answers.** Library support, existing schema, how a neighbouring feature did it — research, not decisions. Mark them `` `research` ``. Never ask what you could read.

**Ask the rest, batches of 4,** via `AskUserQuestion`. 2-4 concrete options each, recommended first, labelled `(Recommended)`, real trade-off in the description. Decisions ("where do retries belong?"), not work ("add the retry handler").

**Settle the demo.** One per feature, at the end, after every phase merges; `build-feature` runs it verbatim and invents nothing. Ask whether the user wants one and what it is — steps they run themselves, a walkthrough the agent runs, an end-to-end check. `none` is valid and common. Record under `## Demo`. `none` is unavailable only when a phase defers its Verify: the demo is that phase's only proof.

**Loop until nothing is open.** Each answer exposes the next question. Write the file as you go — answers as they land, unanswered ones as `_open_` — so an interrupted session resumes from the file. Disagree with a pick? Say why in two lines, then record their call.

Hand over only when no `_open_` is left and no answer is hedged.

## Stage 2 — Cut the work into phases

**Slice vertically.** `Backend`, `Frontend`, `Database`, `Tests`, `Foundations`, `Setup` are all the same bug: user blind until the end, integration problems last.

```
Bad — layer slices, nothing usable until the end
  Phase 1  Backend    [db][api]............  user sees nothing
  Phase 2  Frontend   ...........[ui][wire]  everything lands at once

Good — feature slices, each one usable
  Phase 1  Log in            [db][api][ui]   user has an account
  Phase 2  Generate an image [db][api][ui]   user makes an image
  Phase 3  Animate it        [db][api][ui]   user makes a clip
```

**Name phases by what the user gains.** "Log in and see an empty library", not "Auth layer".

**Every phase carries a Verify line** — a command, URL, click path, or test that fails without this phase's code. "Checks pass" is not one. Can't write it? Not a phase.

**Verify runs locally.** Dev server, test database, scratch account. A deployed URL, shared database, or production credential is a rollout step — park it at the end of the plan for the user to run after merge. No local proof means the phase needs a fixture, not a production target.

**`**Verify:** deferred — <why>`** when a phase has no local surface, and the `## Demo` must cover it. For work with no surface, never for work you haven't thought through. Two deferrals in a row means the slices are wrong. Can't tell? Stage 1 question.

**Size each phase to one build session** — write, verify, two rounds of review fixes, one context. Twenty files is too big whatever it gives the user. Order smallest-visible-thing first, each building on what runs. Prefer 3-6; over 8 the slices are too thin; one is right when the feature fits one session. Never split to hit a count.

**Parallelism only when it pays.** Two phases sharing no dependency and no meaningful files: ask whether to run them as `2a`/`2b`, each with its own Verify line and a note of where they merge. No qualifying pair? Say sequential, don't ask.

**Tasks start unchecked.** Imperative, one sitting each, naming the file: `- [ ] Add source_generation_id to generations (internal/db/migrations)`. Ticking is `build-feature`'s job.

**Locked decisions stay locked.** Proved wrong by the build? Amend Decisions explicitly and name the phases it invalidates. Never quietly re-plan around the user's choice.

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

Add sections the feature needs — constraints, post-merge rollout steps, what was ruled out. Nothing it doesn't.
