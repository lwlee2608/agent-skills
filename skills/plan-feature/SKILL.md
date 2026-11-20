---
name: plan-feature
description: Use when planning a feature that has decisions to settle before building. Settles every open decision with the user, locks the answers into one markdown plan (plan file or GitHub issue), and cuts the work into as few user-verifiable phases as it needs.
argument-hint: "[<feature description> | <path to plan file> | <issue # or URL>]"
user-invocable: true
---

# Plan a Feature

Three failure modes: guessing at decisions that belong to the user, slicing by layer so nothing is visible until the last phase, and splitting work into more phases than it needs. Settle decisions before cutting vertical slices; a task list built around an open decision gets thrown away.

The plan lives in one place, in the format below. A plan file sits at `plans/<feature-slug>.md`, unless the repo keeps design docs elsewhere or the user names a directory. A GitHub issue holds the plan in its body, with the feature name as its title. If a plan for this feature exists, resume it.

## Stage 1 — Settle every decision

**Ask the intent first.** Ask the end goal or trigger behind the request, with your best guesses as options. Never infer the Why; a plausible guess is still a guess. If the goal points to a smaller or different fix, say so once, then follow.

**Ask how deep to interview, next.** Record it as the first Decision. It governs every question in both stages, except intent, plan location, framing gaps, and deploys, which are always asked.
- **Key decisions only** (recommended): ask what is expensive to reverse, usually scope, data model, public API, or what the user sees; settle the rest as `agent`.
- **Ask everything:** ask every decision, cheap ones included; make no `agent` picks.
- **Agent decides:** settle everything else as `agent`, and show the list before stage 2.

**Read the code before offering options.** Learn the files touched, patterns, and libraries; offer only options the codebase can take.

**Ask where the plan lives,** unless the argument settles it. Size the feature from the code: recommend a GitHub issue for a small feature and a plan file for a bigger one. Without `gh` or a GitHub remote, use a plan file and say so.

**Frame the feature.** Write the four framing lines from the format below, taking The Why from the intent answer. If you cannot write a line, ask about it first.

**Answer what the code answers.** Library support, existing schema, and how a similar feature works are research, not decisions. Tag them `research`. Never ask what you could read.

**Ask about what matters.** Rank questions by the Why: ask what bears on it, settle what does not. Tag every pick you make `agent`. Use `AskUserQuestion` with concrete options, your recommendation first, and the real trade-off in each. Batch independent questions, up to four per call; ask a follow-up only after the answer it depends on lands. Ask about decisions ("where do retries belong?"), not work ("add the retry handler").

**Plan only the technical detail that binds.** Keep invariants the reviewer must enforce, security rules, contracts outside the code (webhook URLs, flags flipped at rollout), and expensive-to-reverse choices, stated as properties ("prices per currency, in minor units"), not columns. Leave schema columns, endpoint paths, enum values, env names, and test cases to the builder and reviewer; a guess locked before the code exists binds them. Leave phase branching to the build skill. Restate rules from other docs that bind the build; a fresh builder skips a pointer.

**Settle the demo.** One demo for the whole feature, run after every phase merges. Ask whether the user wants one and what it is: `User runs steps`, `Agent runs walkthrough`, or `End-to-end check`. `none` is valid unless a phase defers its Verify. In the question, name the actor as "user" or "agent", never "you" or "I".

**Write the plan as you go.** Record answers as they land and mark unanswered ones `_open_`, so an interrupted session can resume. Ask the new questions each answer exposes. Create an issue once the framing lines exist. Edit its body with `gh issue edit --body-file`.

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
```

**Name phases by what the user gains.** "Log in and see an empty library", not "Auth layer".

**Give every phase a Verify line** that fails without the phase's code: a command, URL, click path, or test. "Checks pass" is not one. State the steps and the observable result; name queries or flags only when nothing visible shows the result. If you cannot write one, it is not a phase.

**Mind slow Verify steps.** The builder runs fast checks after every fix, slow ones (E2E, Playwright, integration tests that boot services or sleep) only for what changed, and all before merge when CI doesn't. A Verify line that runs slow tests filters to the phase's cases by file or name. Keep proof fast where a test can show it; leave cross-repo runs to `## Demo`.

**Verify locally,** with a dev server, test database, or scratch account. The builder must run every Verify line without stopping. With no local proof, add a fixture rather than target production.
- A step that needs a deployed URL, shared database, or production credential is a rollout step, listed at the end of the plan for the user to run after merge.
- A step that needs the user's own device or personal account goes in `## Demo`.
- Never plan a deploy for a Verify line or the demo unless the user explicitly agrees.

**Defer Verify only when a phase has no local surface:** `**Verify:** deferred — <why>`, and the demo must cover it. Never defer work you have not thought through. Two deferrals in a row means the slices are wrong.

**Size each phase to one build session:** write, verify, and review fixes in one context. That is a limit, not a target: merge phases that fit one session unless the user needs to check something real between them; one phase is fine. Never split just to hit a count. Keep guards and hardening in the phase that adds the behaviour. Each phase builds on what already runs. Cut the slices, then ask the user how many phases they want, with your count first and what each option merges or splits. For a plan in an issue, recommend one phase; if the slices need more, recommend a plan file, and keep the issue if the user prefers it.

**Give every phase a Blocked by line:** phases that must merge first, or `none`. A phase is blocked when it needs their code, shares their files, or the user chose sequential. This graph, not plan order, decides what runs in parallel. If two phases do not block each other, ask whether to run them as `2a`/`2b`.

**Write tasks as unchecked imperatives, one sitting each, naming where the work lands:** `- [ ] Link each generation to its source image (internal/db)`. Say what, not how: `Retry failed uploads`, not `Loop with exponential backoff, max 3`. If the user requires a specific way, record it as a Decision. The builder ticks the boxes.

**Locked decisions stay locked.** If the build proves one wrong, amend Decisions explicitly and name the phases it affects. Never quietly re-plan around the user's choice.

## Stage 3 — Review and trim

**Review the draft for critical flaws.** Reread the whole plan against the code, as a reviewer who did not write it. A flaw is critical if the built plan would break The Why, The Guardrail, or Done means: data lost or duplicated, a gap during a rolling deploy or a write that fails halfway, existing behaviour broken by a change the plan makes, decisions that contradict each other, or a Verify line that passes without the work. Skip nitpicks. Fix flaws in `agent` picks yourself. If a fix changes a user's decision, ask first. Tell the user each flaw found and how the plan now handles it.

**Then cut the plan short.** The builder knows the stack and reads the code, so reapply "Plan only the technical detail that binds" to the whole draft. Also cut `research` lines, `agent` picks that bind nothing, how-to in tasks, and file paths below the package. Never cut a user's decision. Merge tasks in the same area and update the `## Progress` count.

**List the `agent` picks from stages 2 and 3 at the end** so the user can overturn any.

**Commit a plan file last,** on a new branch off the default branch. Propose the name first: `feat/<feature-slug>` for one phase, `integrate/<feature-slug>` for more. Commit only the plan file; never push.

## Plan format

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
