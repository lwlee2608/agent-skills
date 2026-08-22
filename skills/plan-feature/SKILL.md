---
name: plan-feature
description: Use when planning a project too big to hold in one session. Plans it as a single markdown file — phases, their open decisions, and the tasks each phase turns into — resolved one decision at a time.
argument-hint: "[<feature description> | <path to plan file>]"
user-invocable: true
disable-model-invocation: true
---

# Plan a Feature

Big features stall because the unknowns are unknown. Rather than guess at a task list up front, write the open **decisions** into one plan file and resolve them until the path is clear. A phase earns its task list only once its decisions are settled.

The plan lives at `plans/<feature-slug>.md`, unless the repo already keeps design docs elsewhere. If one already covers this feature, resume it — don't re-chart.

```markdown
# <Feature>

## Destination
<what success looks like, 1-2 lines>

## Progress
1/3 phases · 4/9 decided

### Phase 1 — <name> (decided)
Decisions (2/2)
- [x] <question> — <the answer, one or two lines>
- [x] <question> — <the answer>

Tasks (0/3)
- [ ] <task>
- [ ] <task>
- [ ] <task>

### Phase 2 — <name>
Decisions (1/3)
- [x] <question> — <the answer>
- [ ] <question> `research`
- [ ] <question> — blocked by: <other question>

## Notes
<domain context, constraints, standing preferences>

## Not yet specified
<suspected decisions not yet sharp enough to write down>

## Out of scope
<ruled out, with a one-line reason>
```

## Rules

1. **Entries are questions, not work.** "Where should retries live?" is a decision; "Add the retry handler" is a task. A question you can't state sharply goes in "Not yet specified" instead.

2. **One decision per session** — research is the exception. Work the unblocked decisions, earliest phase first.

3. **Ask the user, with `AskUserQuestion`.** Do the legwork, then offer 2-4 candidate answers, recommended one first. A question you can answer alone from docs or the codebase is marked `` `research` `` and is the only kind you may settle yourself.

4. **Research can fan out to subagents**, one question each. For three or more, name the list and get the user's agreement first. Subagents return findings only — this session is the plan's only writer.

5. **A phase's tasks get written when its last decision lands**, not before. Leave the boxes unchecked; ticking them is the build, which is a separate request.

6. **Planning ends when every decision is checked and every phase is tasked.** A question that turns out to be beyond the destination moves to "Out of scope" rather than being answered.
