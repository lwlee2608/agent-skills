---
name: second-opinion
description: Use when the user asks for a second-opinion review from another model via pi (e.g., "get a second opinion", "review with pi", "review using gpt-6-astra", "/second-opinion"). Runs a fresh pi session on the review-code skill and relays its review.
argument-hint: "PR number, ref range, or model"
user-invocable: true
disable-model-invocation: true
---

# Second Opinion

Get a code review from the model configured in pi by running a fresh `pi` session. The user wants that model's take, not yours — relay it, don't redo it.

Assume `pi` is installed, its default provider and model are set in `~/.pi/agent/settings.json`, and the `review-code` skill is available to it. Don't probe for any of these — if `pi` fails, surface the error and stop.

## Rules

1. **Resolve the target in `review-code`'s vocabulary.** Don't compute the diff yourself.
   - PR number → `pr <N>`
   - "PR" with no number → `pr <N>` for the current branch (`gh pr view --json number -q .number`)
   - Ref range (e.g., `main...HEAD`) → verbatim
   - Otherwise → `diff`

2. **Pass the user's model verbatim to `--model`**, or omit `--model` if they named none — pi falls back to its configured default.

3. **Run this from the repo root**, substituting target and model:

   ```bash
   pi -p \
     --model <provider/model> \
     --exclude-tools edit,write \
     --name "review: <target>" \
     "Use the review-code skill to review <target> in this repo. Do not modify any files."
   ```

   - `-p` prints only the final answer, so the output is safe to read in the main session.
   - `--exclude-tools edit,write` keeps the reviewer from "fixing" findings. `bash` stays on for `git` and `gh`.
   - Reviews can take several minutes — use the longest allowed timeout or run it in the background.

4. **Never resume a session.** No `-c`, `-r`, `--session`, `--session-id`, or `--fork` — prior context pollutes the review.

5. **Never inline the diff in the prompt.** `review-code` resolves the target itself, and a large diff breaks shell quoting.

6. **Relay the review verbatim.** Don't summarize, re-rate, or add your own findings.

7. **On non-zero exit, print the error and stop.** Never fall back to a Claude-side review.

## Verification procedure

1. The command had no session-reuse flag.
2. Every reported finding has a `path:line` citation. If findings lack them, pi likely never loaded `review-code` — re-run once, then report. A clean review with no findings needs no citations.
3. If pi rejects the model, check `pi --list-models <name>` and retry with a listed name.
