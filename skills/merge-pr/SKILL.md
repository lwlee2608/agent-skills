---
name: merge-pr
description: Merge a GitHub PR, close linked issues, and delete the branch.
user-invocable: true
disable-model-invocation: true
argument-hint: "[<PR#>]"
---

# Merge PR

## Rules

1. **Merge with a merge commit**, not squash or rebase. Default to the current branch's PR.
2. **Close linked issues still open.** GitHub auto-closes them only for merges into the default branch. Skip if none.
3. **Delete the branch**, remote and local.
