---
name: gh-create-pr
description: Use when creating/raising/opening/submitting a GitHub PR. Produces short, feature-focused descriptions without a test plan.
user-invocable: true
---

# Create a GitHub Pull Request

Create PRs with short, feature-focused descriptions. No test plan or co-author lines.

## Rules

1. **Create the PR** using `gh pr create` with a HEREDOC body:
   ```bash
   gh pr create --title "<short title>" --body "$(cat <<'EOF'
[## Context
<1–2 sentences — include this section only if rule 3 applies>

]## Summary
<bullet points describing the main features/changes, proportional to PR size>
EOF
)"
   ```
2. **Title**: Use imperative mood (e.g., "Add user auth", "Fix pagination bug").
3. **Context section**: Include `## Context` above `## Summary` only when the PR has business/user-facing motivation sourced from a linked issue, ticket, CLAUDE.md, or conversation. Keep it to 1–2 sentences in plain language — what the user or business gets, not how. **Do not invent or speculate**; omit the section entirely for purely technical work (refactor, chore, dep bump) or when no source material exists.
4. **Summary section**: Bullet points proportional to PR size, focused on the changes themselves.
5. **No test plan**: Do not add a test plan, checklist, or QA section.
6. **No co-author**: Do not add "Co-Authored-By" lines.
