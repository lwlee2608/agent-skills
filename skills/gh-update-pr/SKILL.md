---
name: gh-update-pr
description: Use when updating a GitHub PR title or body. Changes only the requested fields and keeps the rest of the text intact.
user-invocable: true
argument-hint: "[<PR#>]"
---

# Update a PR

Change a PR's title or body without losing text that was not part of the request.

## Rules

1. **Read the current PR first.** Do not assume the number or the text. A body rewritten from memory loses what others wrote.
2. **Change only what was asked.** `gh pr edit` leaves a field alone if you pass no flag for it.
3. **Never pass the body inline.** Use a file or stdin. PR bodies contain backticks and quotes that the shell would expand.
4. **Upgrade gh on a `projectCards` GraphQL error.** Versions older than 2.82.1 fail this way. Tell the user to upgrade rather than working around it.
