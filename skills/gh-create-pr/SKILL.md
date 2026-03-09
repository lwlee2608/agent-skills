---
name: gh-create-pr
description: Use when creating a GitHub pull request. Produces short, feature-focused PR descriptions without a test plan section.
user-invocable: true
---

# Create a GitHub Pull Request

Create PRs with short, feature-focused descriptions. No test plan or co-author lines.

## Rules

1. **Create the PR** using `gh pr create` with a HEREDOC body:
   ```bash
   gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
<bullet points describing the main features/changes, proportional to PR size>
EOF
)"
   ```
2. **Title**: Use imperative mood (e.g., "Add user auth", "Fix pagination bug").
3. **Description**: Only a `## Summary` section with bullet points proportional to the PR size.
4. **No test plan**: Do not add a test plan, checklist, or QA section.
5. **No co-author**: Do not add "Co-Authored-By" lines.
