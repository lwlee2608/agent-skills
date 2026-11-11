---
name: merge-pr
description: Merge a GitHub PR, close linked issues, and delete the branch.
user-invocable: true
disable-model-invocation: true
argument-hint: "[<PR#>]"
---

# Merge PR

## Rules

1. **Merge with a merge commit**, not squash or rebase. Default to the current branch's PR. Merge only when its checks pass or are skipped; otherwise report the failing check and stop.
2. **Ask before merging a stack.** If the PR's base is not the default branch, merging lands it on that base, not the default branch. List the stack and ask before merging the PRs below it.
3. **Close linked issues still open.** GitHub auto-closes them only for merges into the default branch. Skip if none.
4. **Update linked issues' checklists.** For every issue the PR closes or references, check off the items it completed with `gh issue edit --body-file`; leave undone items unticked with a reason. Keep referenced-only issues open. Skip if none. List these edits, by issue and checkbox, in any merge approval you ask for. If one is denied, don't reroute; report it and ask.
5. **Delete the branch**, remote and local. First move each open PR based on it to this PR's base (`gh pr list --base <branch>`, then `gh pr edit <n> --base <base>`). Deleting a base branch closes the PRs on it, and a closed PR cannot reopen while its base is gone.
