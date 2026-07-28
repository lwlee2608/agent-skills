---
name: opencode-review
description: Use when the user asks to review code/a PR with opencode or with a non-Claude model (e.g., "review with opencode", "review using gpt-5.6-sol", "/opencode-review"). Runs a fresh opencode session in a subagent, tells it to use the review-code skill, and relays its review.
argument-hint: "PR number, ref range, or model"
user-invocable: true
disable-model-invocation: true
---

# Code Review via opencode

Delegate code review to a fresh `opencode` session running a VelociRouter model (default `velocirouter/gpt-5.6-sol`). The goal is a second opinion from a different model — don't duplicate the review yourself.

Assume `opencode` is installed and the `review-code` skill is available to it. Don't probe for either — if `opencode run` fails, surface the error and stop.

## Rules

1. **Resolve the review target.** Hand `review-code` its own vocabulary; don't resolve the diff yourself.
   - User named a PR number → `pr <N>`
   - User named a ref range (e.g., `main...HEAD`, `abc123..def456`) → use it verbatim
   - Otherwise → `diff`

2. **Resolve the model.** Default `velocirouter/gpt-5.6-sol`. If the user names another model without a provider prefix, use `velocirouter/<name>` (e.g., `gpt-5.6-sol-fast` → `velocirouter/gpt-5.6-sol-fast`). If they give a full `provider/model`, use it verbatim.

3. **Run opencode inside a subagent — never from the main session.** `opencode run` streams the model's reasoning and tool logs to stdout; that whole transcript lands in whichever context invoked it. Spawn one general-purpose subagent whose only job is to run the command and hand back the review.

4. **Start a fresh opencode session.** Never pass `-c`, `-s`, or `--fork` — reusing a prior session pollutes the review with unrelated context. That's the whole point of this skill.

5. **Give the subagent this task** (substituting target and model):

   > Run the command below exactly as written, from the repo root. Do not review the code yourself, do not read the diff, do not edit files.
   >
   > ```bash
   > set -o pipefail
   > OUT=$(mktemp /tmp/opencode-review-XXXXXX.md)
   > opencode run \
   >   -m <provider/model> \
   >   --dir "$(pwd)" \
   >   --title "review: <target>" \
   >   "Use the review-code skill to review <target> in this repo. Do not modify any files." \
   >   | tee "$OUT"
   > rc=$?
   > echo "raw output: $OUT (exit $rc)"
   > exit $rc
   > ```
   >
   > `set -o pipefail` is load-bearing: without it the pipeline reports `tee`'s exit status and an opencode failure looks like success.
   >
   > Do not rename `rc` to `status` — `status` is read-only in zsh, so the assignment aborts the script after opencode has already run, making a successful review look like a failure.
   >
   > If the exit status is non-zero, return the error output and nothing else. Otherwise return two things: the path printed on the last line, and the review itself copied verbatim — findings, ratings, and `path:line` citations exactly as opencode wrote them. Drop only the surrounding tool logs and reasoning chatter.

   - `--dir "$(pwd)"` is required so opencode can run `git` and read repo files.
   - Do **not** pass `--dangerously-skip-permissions` — this is a read-only review.
   - Don't inline the diff into the prompt. The `review-code` skill resolves the target itself, and shell-escaping a large diff breaks quoting.

6. **Relay the subagent's review verbatim** to the user. Don't summarize, re-review, or second-guess it — the user asked for a different model's take, not yours. Mention the raw-output path so they can read the full transcript if they want it.

7. **Surface errors loudly.** If the command exited non-zero, print the error and stop. Don't silently fall back to a Claude-side review.

## Verification procedure

1. The command ran in a subagent, not the main session.
2. If opencode rejects the model, check `opencode models` — VelociRouter models are listed as `velocirouter/<name>`.
3. The relayed review contains concrete `path:line` citations — if it doesn't, opencode probably never loaded the skill or read the diff, and it should be re-run.

## Common mistakes to watch for

- **Running `opencode run` from the main session**: floods the context with the model's full transcript. Always delegate.
- **Letting the subagent do the reviewing**: it's a courier, not a reviewer. Its prompt must say so.
- **Duplicating the review**: Claude re-reviews after opencode returns. Don't — just relay.
