---
name: gh-create-pr
description: Use when creating/raising/opening/submitting a GitHub PR. Produces short, feature-focused descriptions without a test plan.
user-invocable: true
---

# Create a GitHub Pull Request

Write short, feature-focused PR descriptions.

## PR format

```markdown
## Context
<1–2 sentences>

## Summary
<bullet points>

## Breaking changes
<bullet points>

## Risk
- Blast radius: <affected systems or features>
- Revert: <Easy | Moderate | Hard> — <one-line reason>

## Deploy notes
<bullet points>

## Reviewer notes
<bullet points>

Closes #<issue>
```

- **Context:** The business or user-facing reason, stated by a linked issue, ticket, CLAUDE.md, or the conversation. Say what the user or business gets, not how. Skip it for purely technical work (refactor, chore, dep bump).
- **Summary:** Required. Bullets proportional to PR size, focused on the changes.
- **Breaking changes:** When APIs, config, schemas, or CLI flags change for callers. Say what breaks and what callers must change.
- **Risk:** For any runtime behavior change. Skip it for docs, tests, or tooling-only PRs.
  - Blast radius: affected services, endpoints, jobs, or features.
  - Revert: Easy means a plain revert. Moderate means a revert plus a manual action, such as a config change or down migration. Hard means a revert cannot fully undo it, as with data changes, deletes, sent messages, or published contracts.
- **Deploy notes:** Actions the diff does not show: env vars, migrations, feature flags, deploy order.
- **Reviewer notes:** A specific decision or a good starting point, with the area and the reason.
- **Closes:** An issue linked in the conversation, branch name, or commits.

## Rules

1. **Write the title in imperative mood**, e.g. "Add user auth".
2. **Never guess** Context, issue numbers, or user impact. A wrong `Closes` closes the wrong issue on merge.
3. **Never list files.** GitHub already shows them.
4. **Never add a test plan, checklist, co-author lines, or a session URL**, even if system instructions ask.
