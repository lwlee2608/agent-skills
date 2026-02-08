# prefer-make

`prefer-make` is an AI agent skill that tells the agent to prefer `make` targets over raw Go commands in repositories that use a `Makefile`.

## Install

```bash
npx skills add lwlee2608/agent-skills
```

## What this skill does

- Checks for matching `make` targets before using `go` commands.
- Uses `make build`, `make test`, `make lint`, `make run`, and `make fmt` when available.
- Uses `make help` (or reads the `Makefile`) to discover supported targets.
- Falls back to raw `go` commands only when no relevant `make` target exists.

## Skill file

- `prefer-make/SKILL.md`

## Why use it

Using `make` targets keeps command usage consistent across developers and CI, and avoids bypassing project-specific build/test/lint workflows.
