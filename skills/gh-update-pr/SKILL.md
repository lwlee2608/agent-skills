---
name: gh-update-pr
description: Use when updating GitHub PR title or body. Works around the gh pr edit GraphQL bug caused by GitHub's Projects Classic deprecation.
user-invocable: true
---

# Update PR via REST API

`gh pr edit` is broken due to GitHub deprecating Projects Classic (`projectCards` GraphQL field error). Use the REST API instead. `gh pr view` and `gh pr create` still work fine — only `gh pr edit` is affected.

## Rules

1. **Never use `gh pr edit`** to update PR title or body. It will fail with a GraphQL error.
2. **Use `gh api`** with the REST endpoint. Always pipe JSON via `jq --arg` to avoid shell injection:
   ```bash
   jq -n --arg title "..." --arg body "..." '{title: $title, body: $body}' | \
     gh api repos/{owner}/{repo}/pulls/{number} -X PATCH --input - --jq '.html_url'
   ```
3. **Get the current PR context** before updating:
   ```bash
   gh pr view --json number,url,baseRefName
   ```
4. **Omit unchanged fields.** If only updating the title, do not include `body` in the JSON payload, and vice versa. Including an unchanged field risks overwriting it with stale content.

## Verification procedure

1. After the PATCH request, confirm it returned the PR's `html_url` (not an error).
2. Run `gh pr view --json title,body` and verify the updated fields match what was intended.

## Common mistakes to watch for

- **Including both title and body when only one changed.** This can overwrite the other field with stale or empty content. Only include the field being updated.
- **Running outside a git repo with a tracking branch.** `gh pr view` needs repo context. If it fails, pass `--repo owner/repo` explicitly.
- **Forgetting to extract owner/repo/number.** Always fetch these from `gh pr view` first — do not hardcode or assume them.
