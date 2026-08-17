# agent-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-14-blue.svg)]()

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

### create-skill

Guide the creation of new SKILL.md files that meet quality standards.

- Covers naming, descriptions, rule structure, verification procedures, and common mistakes.
- Includes a 7-point self-review checklist for validating newly created skills.
- Enforces conciseness (under 4KB) and single-responsibility scope.

### ascii-diagram

Validate and fix alignment issues in ASCII diagrams.

- Redraws diagrams from scratch with correct padding and border widths.
- Supports both plain ASCII (`+`, `-`, `|`) and Unicode box-drawing characters.
- Validates alignment with a quick `awk` one-liner after redrawing.

### whiteboard-explain

Explain technical concepts the way an engineer would at a whiteboard.

- Writes in ASD-STE100 Simplified Technical English: active voice, simple tenses, one word per meaning.
- Analogy before jargon; short sentences capped at 20 words.
- Pairs the explanation with a small diagram whenever it adds clarity.
- One concept per response, no preamble or recap.

### writing-system-prompts

Apply prompt-engineering and prompt-caching best practices when authoring LLM system prompts.

- Orders content static-first, dynamic-last so cache prefixes stay reusable.
- Marks explicit cache breakpoints and keeps churning content (timestamps, IDs, history) below them.
- Uses structural delimiters and literal, scoped instructions instead of ALL-CAPS shouting.

### handoff

Condense the current conversation into a handoff document for another agent to pick up.

- Writes a summary to `/tmp` with a "Suggested skills" section.
- References existing artifacts (PRDs, ADRs, commits) by path or URL rather than duplicating them.
- Redacts API keys, passwords, and other sensitive information.

### trim-comments

Remove comment noise from code at two levels.

- **normal** (default) shortens verbose comments while keeping their meaning.
- **aggressive** deletes comments that merely restate the code.
- Always preserves "why"/workaround comments, TODO/FIXME, license headers, and linter directives.

### review-code

Review a local diff, a GitHub PR, or a whole codebase and report findings.

- Target is passed as an argument: `diff` (default), `pr <number>`, `all`, or a path.
- Each finding gets a severity, a likelihood, a worth-fixing verdict, and a high-level fix.
- Reports only — never edits code.

### opencode-review

Get a second-opinion review from a non-Claude model via `opencode`.

- Runs a fresh `opencode` session on `velocirouter/gpt-5.6-sol` (override with any `opencode models` entry).
- Delegates the rubric to the `review-code` skill rather than duplicating it.
- Runs inside a subagent and relays the review verbatim, keeping the transcript out of the main session.

### linear-issues

Read, create, update, and comment on Linear issues through the Linear MCP server.

- Routes everything through `mcp__linear__*` tools — never the web UI or raw GraphQL.
- Resolves team/state/label/assignee names to IDs before writing.
- Keeps ticket comments to 1–3 sentences: outcome first, link the PR, no filler.
- Leaves PR-linked issues alone — the GitHub integration moves them to Done on merge.

### plan-feature

Plan work too big for one session as a map issue plus child decision tickets.

- Tickets are questions, not tasks — resolved one per session until nothing is left to decide.
- Detects the tracker: Linear MCP if present, otherwise `gh issue`.
- Fans research tickets out to parallel subagents, asking first when there are three or more.
- Plans only — never implements.

### generate-media

Generate or edit one image or video through a provider API — OpenRouter today, one file per provider under `providers/`.

- Picks the cheapest model that fits by querying `/api/v1/models`, never a hardcoded list.
- Quotes the model and rough cost before spending, and waits when the call is not cheap.
- Drafts video cheap before paying for the final — Seedance 2.0 Mini at 480p costs ~5% of a Kling clip.
- Saves outside the repo to `~/.cache/generate-media/` and reports the real `usage.cost` from the response.
- Needs `OPENROUTER_API_KEY` only. No scripts, no dependencies.

## Why trust these skills

- Small and auditable: each skill is plain text in `skills/*/SKILL.md`.
- Narrow scope: each skill handles one workflow only.
- Easy to review before install: inspect this repo and each skill definition directly.

## Security note

Always review third-party skills before installing. See <https://skills.sh/docs> for ecosystem and telemetry details.
