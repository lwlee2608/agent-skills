---
name: plan-feature
description: Use when planning a project too big to hold in one session. Plans it as a map issue plus child decision tickets on the issue tracker, resolved one session at a time.
argument-hint: "[<feature description>]"
user-invocable: true
---

# Plan a Feature

Big features stall because the unknowns are unknown. Instead of guessing at a task list, map the open **decisions** as tickets on the issue tracker and resolve them until the path is clear. Tickets are questions, not deliverables.

Detect the tracker first: use the Linear MCP tools if present, otherwise `gh issue`. If neither exists, ask the user before writing anything.

## Rules

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

4. **Wire blocking after creating.** Create the tickets first, then set blocked-by relations in a second pass — the relations need issue IDs that do not exist yet.

5. **Work the frontier.** The frontier is open tickets that are unblocked and unassigned. Take the one the user named, else the first on the frontier. Assign it to yourself immediately so parallel sessions do not collide.

6. **Resolve one ticket per session.** Post the answer as a comment, close the ticket, add a line to "Decisions so far". Then add any tickets the answer surfaced, and promote fog that just got sharp out of "Not yet specified".

7. **Rule out, don't resolve.** A ticket that turns out to be beyond the destination gets closed into "Out of scope", not answered.

8. **Never implement.** Planning ends when no blocking question is left open. Building is a separate request.

## Verification procedure

1. Does every ticket ask exactly one answerable question?
2. Is the map body free of open-ticket listings?
3. After closing a ticket: comment posted, issue closed, map updated, new tickets wired?

## Common mistakes to watch for

- **Tickets that are tasks.** "Add the retry handler" is work; "Where should retries live?" is a decision.
- **Answering your own question.** Decisions needing the user's judgment must be asked, not assumed.
- **Burning the map down in one go.** One ticket per session keeps each decision reviewable.
- **Fog dumped into tickets.** Vague questions produce vague answers; leave them in "Not yet specified".
