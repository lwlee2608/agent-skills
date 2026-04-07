---
name: linear
description: Use when the user wants to interact with Linear.app — reading, searching, creating, or updating issues/tickets, listing teams, or checking workflow states.
user-invocable: true
---

# Linear Issue Management

Interact with Linear.app issues via its GraphQL API. Covers reading, searching, creating, and updating issues.

## Rules

1. **Require `LINEAR_API_KEY`** before making any API call. Check with `echo $LINEAR_API_KEY`. If unset, tell the user to export it (`export LINEAR_API_KEY="lin_api_..."`). Never hardcode or log the key.

2. **Send all requests as POST to `https://api.linear.app/graphql`**:
   ```bash
   curl -s -X POST https://api.linear.app/graphql \
     -H "Content-Type: application/json" \
     -H "Authorization: $LINEAR_API_KEY" \
     -d "$(jq -n --arg q 'QUERY_HERE' '{"query": $q}')" | jq .
   ```
   Do **not** use `Bearer` prefix — Linear API keys are passed directly. Use `jq -n --arg` to safely inject the query — never string-interpolate into `-d` (injection risk).

3. **Look up an issue by identifier** (e.g., `ENG-123`) — accepts both UUIDs and identifiers:
   ```graphql
   { issue(id: "ENG-123") { id identifier title state { name } assignee { name } priority url } }
   ```

4. **Search issues by text** using `searchIssues` (uses `term`, not `query`):
   ```graphql
   { searchIssues(term: "login bug", first: 10) { nodes { id identifier title state { name } assignee { name } priority url } } }
   ```

5. **List issues with filters** using the `issues` query:
   ```graphql
   { issues(filter: { team: { key: { eq: "ENG" } }, state: { name: { in: ["In Progress", "Todo"] } } }, first: 20) { nodes { id identifier title state { name } assignee { name } priority } pageInfo { hasNextPage endCursor } } }
   ```
   Use `first`/`after` for pagination. Check `pageInfo.hasNextPage`.

6. **Get full issue details** — add `description`, `comments`, `labels` fields to the `issue` query in rule 3.

7. **Create an issue** with `issueCreate`. Requires `teamId` — look it up first if unknown:
   ```graphql
   mutation { issueCreate(input: { title: "Issue title", description: "Details", teamId: "TEAM_UUID", priority: 3 }) { success issue { id identifier title url } } }
   ```
   Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low.

8. **Update an issue** with `issueUpdate`. Requires the UUID `id`, not the identifier:
   ```graphql
   mutation { issueUpdate(id: "ISSUE_UUID", input: { stateId: "STATE_UUID", priority: 2 }) { success issue { id identifier title state { name } } } }
   ```

9. **List teams** with `{ teams { nodes { id name key } } }` to discover team IDs.

10. **List workflow states** for a team to get valid state IDs:
    ```graphql
    { workflowStates(filter: { team: { key: { eq: "ENG" } } }) { nodes { id name type } } }
    ```

11. **Look up the current user** with `{ viewer { id name email } }` for assignment.

12. **Always resolve UUIDs before mutations.** Mutations require UUIDs for state/user/label IDs. Use `issue(id: "ENG-123")` to get the issue UUID, then use it in the mutation.

## Verification procedure

1. **Auth check** — Run `{ viewer { id name email } }` to confirm the API key works before other operations.
2. **Mutation check** — After `issueCreate`/`issueUpdate`, verify `success` is `true` and display the issue identifier and URL.
3. **ID resolution check** — Before any mutation, confirm you have valid UUIDs (36-char format) for all ID fields.

## Common mistakes to watch for

- **Using identifier instead of UUID in mutations**: `issueUpdate` requires the UUID `id`. Use `issue(id: "ENG-123")` to resolve it first.
- **Missing teamId on create**: `issueCreate` requires `teamId`. Query teams first if unspecified.
- **Unsafe JSON construction**: Always use `jq -n --arg` — never string-interpolate into `-d` directly.
- **Forgetting pagination**: Check `pageInfo.hasNextPage` and use `after` for next pages.
- **Wrong priority scale**: 1=Urgent (highest), 4=Low — the reverse of what many expect.
