# agent-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-4-blue.svg)]()

Reusable AI agent skills for Claude Code, OpenCode, and other skills-compatible agents.

## Install

```bash
npx skills add lwlee2608/agent-skills
```

## Supported agents

- Claude Code
- OpenCode
- Other agents that support the `skills` ecosystem

## Included skills

Repository layout: `skills/<skill-name>/SKILL.md`

### prefer-make

Prefer `make` targets over raw Go commands in repositories that use a `Makefile`.

- Uses `make build`, `make test`, `make lint`, `make run`, and `make fmt` when available.
- Falls back to raw `go` commands only when no relevant `make` target exists.
- Recommended when you want consistent local and CI behavior.

### gh-create-pr

Create GitHub PRs with short, feature-focused descriptions.

- Produces a `## Summary` section only — no test plan or co-author lines.
- Bullet points proportional to PR size.
- Uses imperative mood for titles.

### gh-update-pr

Update PR title/body through `gh api` REST calls when `gh pr edit` is unreliable.

- Uses `gh pr view` to detect PR context.
- Uses `gh api repos/{owner}/{repo}/pulls/{number} -X PATCH` to update title/body.
- Keeps `gh pr create` and `gh pr view` unchanged.

### ascii-diagram

Validate and fix alignment issues in ASCII diagrams.

- Redraws diagrams from scratch with correct padding and border widths.
- Supports both plain ASCII (`+`, `-`, `|`) and Unicode box-drawing characters.
- Validates alignment with a quick `awk` one-liner after redrawing.

## Why trust these skills

- Small and auditable: each skill is plain text in `skills/*/SKILL.md`.
- Narrow scope: each skill handles one workflow only.
- Easy to review before install: inspect this repo and each skill definition directly.

## Security note

Always review third-party skills before installing. See <https://skills.sh/docs> for ecosystem and telemetry details.
