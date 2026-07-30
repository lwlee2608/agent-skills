---
name: plan-feature
description: Use when planning a project too big to hold in one session. Plans it as a map issue plus child decision tickets on the issue tracker, resolved one session at a time.
argument-hint: "[<feature description> | <map issue ID or URL>]"
user-invocable: true
disable-model-invocation: true
---

# Plan a Feature

Big features stall because the unknowns are unknown. Rather than guess at a task list, map the open **decisions** as tickets on the issue tracker and resolve them until the path is clear. Tickets are questions, not deliverables.

Detect the tracker first: Linear MCP tools if present, otherwise `gh issue`. If neither exists, ask before writing anything.

## Rules

0. **Chart or resume — decide before writing.** If the user named a map, or an open `plan-feature:map` issue already covers this feature, load it and work the frontier (rules 6-10). Chart a new map (rules 1-5) only when none exists.

1. **Name the destination first.** One or two lines describing what "done planning" looks like. If nothing is foggy, the work fits one session — say so and stop.

2. **Create one map issue.** Title it after the feature, label it `plan-feature:map`. Body:
   ```markdown
   ## Destination
   <what success looks like, 1-2 lines>

   ## Notes
   <domain context, constraints, standing preferences>

   ## Decisions so far
   <one line per closed ticket, with a link>

   ## Not yet specified
   <suspected decisions not yet sharp enough to ticket>

   ## Out of scope
   <ruled out, with a one-line reason>
   ```
   Open tickets are child issues — find them by query, never list them in the body.

3. **One ticket, one question.** Body is a single `## Question` section, answerable in one session. If you cannot state the question sharply, it belongs in "Not yet specified" instead.

4. **Label the research tickets.** A question you can answer alone — from docs, the codebase, a third-party API — gets the label `plan-feature:research`. Everything else needs the user's judgment: resolve it in conversation.

5. **Wire blocking after creating.** Create the tickets first, then set blocked-by relations in a second pass — the relations need IDs that do not exist yet.

6. **Work the frontier.** The frontier is open tickets that are unblocked and unassigned. Take the one the user named, else the first on the frontier. Claim it by assigning before any work, so parallel sessions do not collide.

7. **Resolve one ticket per session** — research is the exception. Post the answer as a comment, close the ticket, add a line to "Decisions so far". Then add any tickets the answer surfaced, and promote fog that just got sharp out of "Not yet specified".

8. **Ask before fanning out.** Unblocked research tickets can run as parallel subagents, one ticket each. Name the ones you intend to dispatch: run one or two directly, but for three or more ask the user first — with the list and the count — and do not launch until they agree.

   Each subagent gets the question plus the map's Notes and returns findings only — no deciding, no tracker writes, no implementing. This session records every resolution, so the map has one writer.

9. **Rule out, don't resolve.** A ticket that turns out to be beyond the destination gets closed into "Out of scope", not answered.

10. **Never implement.** Planning ends when no blocking question is left open. Building is a separate request.

## Verification procedure

1. Before creating a map: did you query for an existing one?
2. Does every ticket ask exactly one answerable question?
3. Is the map body free of open-ticket listings?
4. Is every ticket the agent can answer alone labelled `plan-feature:research`?
5. Before dispatching three or more subagents: did the user agree to the list?
6. After closing a ticket: comment posted, issue closed, map updated, new tickets wired?

## Common mistakes to watch for

- **Charting over an existing map.** A follow-up session resumes; it does not re-chart.
- **Tickets that are tasks.** "Add the retry handler" is work; "Where should retries live?" is a decision.
- **Answering your own question.** Decisions needing the user's judgment must be asked, not assumed — which is why only research tickets go to subagents. A decision ticket dispatched in parallel comes back as a guess.
- **Burning the map down in one go.** One ticket per session keeps each decision reviewable.
- **Fog dumped into tickets.** Vague questions produce vague answers; leave them in "Not yet specified".
