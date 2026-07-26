---
name: trim-comments
description: Use when asked to trim, clean up, shorten, or remove code comments. Two levels — "normal" (default) shortens verbose comments; "aggressive" deletes nearly every comment, keeping only trimmed unusual-workaround notes.
user-invocable: true
argument-hint: "[normal|aggressive] [<target>]"
---

# Trim Comments

Reduce comment noise. **normal** (default) shortens wordy comments but keeps their meaning — shorter, not cryptic; never deletes. **aggressive** deletes nearly every comment. Use aggressive only when the user says so ("aggressive", "strip", "remove all").

Two rules always hold:

- Edit comments only — never change a line of executable code.
- **Scope:** unless the user names files, trim only changed code — the uncommitted local diff first, then the PR diff. Touch the whole codebase only when explicitly asked.

## What each mode does

```
COMMENT TYPE                          NORMAL              AGGRESSIVE
─────────────────────────────────────────────────────────────────────
Restatement (// create user)          shorten             DELETE
Narration (// loop over users)        shorten             DELETE
Echo docstring (Gets name)            shorten             DELETE
Plain why-comment                     keep (shortened)    DELETE
TODO / FIXME / HACK                   keep                DELETE
Doc comment (godoc etc.)              keep (shortened)    stub if lint needs it, else DELETE
Unusual workaround / gotcha           keep (shortened)    KEEP but trim shorter
─────────────────────────────────────────────────────────────────────
Tooling directives (//go:generate…)   never touch         never touch
License / copyright headers           never touch         never touch
```

## Notes

- **Unusual workaround** = a non-obvious gotcha, a bug being worked around, a "must do X or Y breaks" note. Aggressive keeps these but trims to the shortest form that still conveys the reason.
- **Tooling directives** (`//go:generate`, `//go:embed`, `# noqa`, `# type: ignore`, `// eslint-disable`, `// @ts-expect-error`, `// nolint`) and **license headers** look like comments but aren't noise — deleting them changes behavior or has legal weight. Never touch them at either level.
