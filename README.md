# agent-skills

AI agent skills for Claude Code, OpenCode, and other compatible agents.

## Install

```bash
npx skills add lwlee2608/agent-skills
```

## Skills

### prefer-make

Tells the agent to prefer `make` targets over raw Go commands in repositories that use a `Makefile`.

- Uses `make build`, `make test`, `make lint`, `make run`, and `make fmt` when available.
- Falls back to raw `go` commands only when no relevant `make` target exists.

### gh-update-pr

Works around the `gh pr edit` GraphQL bug caused by GitHub's Projects Classic deprecation. Instructs the agent to use `gh api` REST endpoint instead.
