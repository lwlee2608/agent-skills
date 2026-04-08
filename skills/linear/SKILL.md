---
name: linear
description: Use when the user wants to interact with Linear.app — reading or searching issues/tickets.
user-invocable: true
---

# Linear Issue Management

Interact with Linear.app issues using the `linear` CLI.

## Prerequisites

- **`linear` CLI** must be installed (`linear --version`). If missing, install with:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/lwlee2608/linear-cli/main/install.sh | bash
  ```
- **`LINEAR_API_KEY`** must be set. Check with `echo $LINEAR_API_KEY`. If unset, tell the user to export it (`export LINEAR_API_KEY="lin_api_..."`).

## Commands

### Get an issue

```bash
linear issue get ENG-123
```

Returns: identifier, title, state, team, priority, assignee, description.

### Search issues

```bash
linear issue search "login bug"
linear issue search "login bug" --limit 50
```

Returns a table: ID, TITLE, STATE, ASSIGNEE. Default limit is 20.
