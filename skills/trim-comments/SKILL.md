---
name: trim-comments
description: Use when asked to trim, clean up, shorten, or remove code comments. Two levels — "normal" (default) shortens verbose comments; "aggressive" deletes comments that merely restate the code, keeping only workaround/why/non-obvious ones.
user-invocable: true
argument-hint: [normal|aggressive] [<target>]
---

# Trim Comments

Reduce comment noise. **normal** (default) shortens wordy comments; **aggressive** deletes comments that just restate what the code already says. Use aggressive only when the user says so ("aggressive", "strip", "remove all").

Edit comments only — never change a line of executable code.

**Scope:** unless the user names files, trim only changed code — the uncommitted local diff first, then the PR diff. Touch the whole codebase only when explicitly asked.

## Always keep (never delete)

- **Why / workaround** comments — the non-obvious reason, gotcha, or bug workaround.
- **TODO / FIXME / HACK** markers and **links** to issues, specs, or PRs.
- **License / copyright** headers.
- **Tooling directives** that look like comments but change behavior: `//go:generate`, `//go:embed`, `# noqa`, `# type: ignore`, `// eslint-disable`, `// @ts-expect-error`, `// nolint`.
- **Doc comments a linter requires** (e.g. godoc on exported Go symbols) — shorten, don't delete.

## Aggressive — delete what restates the code

Delete restatements (`// create a new user` above `u := NewUser()`), narration (`// loop over users`), and echo docstrings ("Gets the name." on `getName()`). Keep the *why* comments.

## Normal — shorten, don't delete

Cut filler and full-sentence padding while preserving meaning. Shorter, not cryptic.
