---
name: opencode-review
description: Use when the user asks to review code/a PR with opencode or with a non-Claude model (e.g., "review with opencode", "review using gpt-5.3-codex", "/opencode-review"). Spawns a fresh opencode session with an OpenAI model and returns its review.
user-invocable: true
---

# Code Review via opencode

Delegate code review to a fresh `opencode` session running an OpenAI model (default `openai/gpt-5.3-codex`). The goal is a second opinion from a different model — don't duplicate the review yourself.

## Rules

1. **Check `opencode` is installed.** Run `command -v opencode` first. If missing, tell the user to install it and stop — do not fall back to a Claude-side review.

2. **Resolve the review scope** in this priority order:
   - User named a PR number → `gh pr diff <N>`
   - User named a ref range (e.g., `main...HEAD`, `abc123..def456`) → use it verbatim
   - Otherwise → default to `main...HEAD`

3. **Resolve the model.** Default `openai/gpt-5.3-codex`. If the user names another model, use `openai/<name>` (e.g., `gpt-5.3-codex-spark` → `openai/gpt-5.3-codex-spark`).

4. **Start a fresh opencode session.** Never pass `-c`, `-s`, or `--fork` — reusing a prior session pollutes the review with unrelated context. That's the whole point of this skill.

5. **Run opencode with this exact shape:**
   ```bash
   opencode run \
     -m <provider/model> \
     --dir "$(pwd)" \
     --title "review: <scope>" \
     "$(cat <<'EOF'
   You are performing a code review. Work in the current git repo.

   Scope: <scope>

   Steps:
   1. Run `git diff <scope>` (or `gh pr diff <N>` for a PR) to see the changes.
   2. Read any files you need for surrounding context.
   3. Return a review covering:
      - Correctness / likely bugs
      - Security concerns
      - Code quality & consistency with existing patterns
      - Test coverage gaps
   4. Cite every finding with `path:line` references.

   Do not modify any files.
   EOF
   )"
   ```
   - `--dir "$(pwd)"` is required so opencode can run `git` and read repo files.
   - Do **not** pass `--dangerously-skip-permissions` — this is a read-only review.
   - Let opencode fetch the diff itself via `git` rather than inlining a large diff into the prompt (shell-escaping large diffs breaks quoting).

6. **Forward opencode's output verbatim** to the user. Don't summarize, re-review, or second-guess it — the user asked for a different model's take, not yours.

7. **Surface errors loudly.** If `opencode run` exits non-zero, print the error and stop. Don't silently fall back.

## Verification procedure

1. `command -v opencode` succeeds before invoking.
2. The chosen model appears in `opencode models openai` output.
3. opencode's review output contains concrete `path:line` citations — if it doesn't, it probably didn't read the diff and should be re-run.

## Common mistakes to watch for

- **Reusing a session** with `-c`/`-s`: pollutes the review with unrelated context.
- **Omitting `--dir`**: opencode runs in `$HOME` and can't see the repo.
- **Inlining the diff into the prompt**: shell quoting breaks on large diffs. Let opencode run `git diff` itself.
- **Duplicating the review**: Claude re-reviews after opencode returns. Don't — just forward the output.
- **Swallowing non-zero exits**: always surface `opencode run` failures.
