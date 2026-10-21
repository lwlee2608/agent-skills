---
name: plan-feature
description: Use when planning a feature too big to hold in one session. Settles every open decision by asking the user, locks the answers into one markdown plan file, then cuts the work into phases the user can verify one at a time.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
---

# Plan a Feature

Two failure modes: guessing at decisions that belong to the user, and slicing by layer so nothing is visible until the last phase. Settle decisions first, then cut vertical slices. Finish stage 1 before stage 2; a task list built around an open decision gets thrown away.

The plan lives at `plans/<feature-slug>.md`, unless the repo keeps design docs elsewhere or the user names a directory. If a plan for this feature exists, resume it.

## Stage 1 — Settle every decision

**Ask the intent first.** Ask what end goal or trigger is behind the request. Offer your best guesses as options. Never infer the Why from the request; a plausible guess is still a guess. If the goal points to a smaller or different fix, say so once, then follow.

**Ask how deep to interview, next.** Record it as the first Decision. It governs every question in both stages, except intent, framing gaps, and deploys, which are always asked.
- **Key decisions only** (recommended): ask what is expensive to reverse; settle the rest as `agent`.
- **Ask everything:** ask every decision, cheap ones included; make no `agent` picks.
- **Agent decides:** settle everything else as `agent`, and show the list before stage 2.

**Read the code first.** Learn the files touched, the patterns, and the libraries in use. Offer only options the codebase can take.

**Frame the feature.** Write the four framing lines from the format below, taking The Why from the intent answer. If you cannot write a line, ask about it first.

**Answer what the code answers.** Library support, existing schema, and how a similar feature works are research, not decisions. Tag them `research`. Never ask what you could read.

**Ask about what matters.** Under key decisions only, ask what is expensive to reverse, usually scope, data model, public API, or what the user sees, and settle cheap-to-reverse calls yourself. Use the Why to rank questions: ask what bears on it, settle what does not. Tag every pick you make `agent`. Use `AskUserQuestion` with concrete options, your recommendation first, and the real trade-off in each. Batch independent questions, up to four per call; ask a follow-up only after the answer it depends on lands. Ask about decisions ("where do retries belong?"), not work ("add the retry handler").

**Plan only the technical detail that binds.** Keep invariants the reviewer must enforce, security rules, contracts outside the code (webhook URLs, flags flipped at rollout), and expensive-to-reverse choices, stated as properties ("prices per currency, in minor units"), not columns. Leave schema columns, endpoint paths, enum values, env names, and test cases to the builder and reviewer; a locked guess made before the code exists binds them to it.

**Settle the demo.** One demo for the whole feature, run after every phase merges. Ask whether the user wants one and what it is: steps they run, a walkthrough you run, or an end-to-end check. `none` is valid unless a phase defers its Verify.

**Write the file as you go.** Record answers as they land and mark unanswered ones `_open_`, so an interrupted session can resume. Each answer can expose a new question; keep going until none is open.

**Disagree once, then follow.** If you disagree with any pick in this skill, say why in two lines, then record the user's call.

**Move to stage 2 only when nothing is open,** no answer is hedged, and the user has seen every `agent` pick.

## Stage 2 — Cut the work into phases

**Slice vertically.** Layer phases (`Backend`, `Frontend`, `Database`, `Tests`, `Setup`) keep the user blind until the end and push integration problems last.

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

**Give every phase a Verify line** that fails without the phase's code: a command, URL, click path, or test. "Checks pass" is not one. State the steps and the observable result; name queries or flags only when nothing visible shows the result. If you cannot write one, it is not a phase.

**Verify locally,** with a dev server, test database, or scratch account. The builder must run every Verify line without stopping. If there is no local proof, add a fixture rather than target production.
- A step that needs a deployed URL, shared database, or production credential is a rollout step. List it at the end of the plan for the user to run after merge.
- A step that needs the user's own device or personal account goes in `## Demo`.
- Never plan a deploy for a Verify line or the demo unless the user explicitly agrees.

**Defer Verify only when a phase has no local surface:** `**Verify:** deferred — <why>`, and the demo must cover it. Never defer work you have not thought through. Two deferrals in a row means the slices are wrong.

**Size each phase to one build session:** write, verify, and review fixes in one context. Put the smallest visible thing first, each phase building on what already runs. Prefer 3-6 phases; one is fine if the feature fits one session. Cut the slices, then ask the user how many phases they want, with your count first and what each option merges or splits. Never split just to hit a count.

**Give every phase a Blocked by line:** phases that must merge first, or `none`. A phase is blocked when it needs their code, shares their files, or the user chose sequential. This graph, not plan order, decides what runs in parallel. If two phases do not block each other and share no files, ask whether to run them as `2a`/`2b`.

**Write tasks as unchecked imperatives, one sitting each, naming the file:** `- [ ] Add source_generation_id to generations (internal/db/migrations)`. Say what, not how: `Retry failed uploads`, not `Loop with exponential backoff, max 3`. If the user requires a specific way, record it as a Decision. The builder ticks the boxes.

**Locked decisions stay locked.** If the build proves one wrong, amend Decisions explicitly and name the phases it affects. Never quietly re-plan around the user's choice.

**List stage 2's `agent` picks at the end** so the user can overturn any.

## Plan file format

```markdown
# <Feature>
**The Job** — <what gets built>
**The Why** — <end goal behind the ask, from the user: who needs it, what breaks or stalls without it>
**The Guardrail** — <what must not change — omit if none>
**Done means** — <observable outcome that closes the feature>

## Decisions
- **Interview depth** — <key decisions only | ask everything | agent decides>
- **<question>** — <answer, one or two lines>
- **<question>** — <answer> `agent`
- **<question>** — <answer> `research`
- **<question>** — _open_   <-- only while stage 1 is running

## Progress
Active: 1 · 0/11 tasks

### Phase 1 — <what the user gains>
<one line: what they can do now that they could not before>
**Blocked by:** <phase numbers, or `none`>
- [ ] <task>
- [ ] <task>
**Verify:** <command, URL, click path, or test — or `deferred — <why>`>

## Demo
<how the finished feature gets shown once every phase has merged — or `none`>
```

Add sections the feature needs, such as constraints, post-merge rollout steps, or what was ruled out. Nothing else.
