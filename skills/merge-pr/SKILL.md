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
3. **Update linked issues' checklists.** For every issue the PR closes or references, check off the items it completed with `gh issue edit --body-file`; leave undone items unticked with a reason. Keep referenced-only issues open. Skip if none. List these edits, by issue and checkbox, in any merge approval you ask for. If one is denied, don't reroute; report it and ask.
4. **Delete the branch**, remote and local.
