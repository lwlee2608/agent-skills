---
name: whoami
description: Use when the user asks for the current session's ID (e.g., "/whoami", "what's your session id", "who are you") so another agent session can find or message this one. Works in Claude Code, pi, and OpenCode.
user-invocable: true
disable-model-invocation: true
---

# Who Am I

Report how another session can reach this one: harness, session ID, working directory, transcript, and tmux pane.

## Rules

1. **Read the ID from the environment, never guess it.** Each harness sets it in the shell tool's env:

   | Harness     | Detect by              | Session ID                | Transcript                          |
   |-------------|------------------------|---------------------------|-------------------------------------|
   | Claude Code | `CLAUDECODE=1`         | `$CLAUDE_CODE_SESSION_ID` | `~/.claude/projects/*/<id>.jsonl`   |
   | pi          | `PI_CODING_AGENT=true` | `$PI_SESSION_ID`          | `$PI_SESSION_FILE`                  |
   | OpenCode    | `OPENCODE=1`           | none — see rule 2         | none (stored in SQLite)             |

   Resolve the Claude Code transcript with the glob rather than rebuilding the encoded directory name. Omit any field marked none, and omit the pi transcript when `PI_SESSION_FILE` is unset (ephemeral session).

2. **For OpenCode, take the newest session for the current directory.** OpenCode sets no session-ID env var. Run `opencode session list --format json -n 10` and pick the most recently `updated` entry whose `directory` equals `$PWD`. The live session updates on every turn, so it is usually the newest. If two sessions in this directory updated within the last few minutes, say the ID is ambiguous and list both.

3. **Print only the env vars you need.** Never dump the whole environment; it holds API keys.

4. **Include the tmux pane when `$TMUX_PANE` is set.** pi and OpenCode have no message channel between sessions, so a peer reaches them by typing into this session's tmux pane. Omit the field outside tmux.

5. **Reply in this format and nothing else:**

   ```
   harness:    <Claude Code | pi | OpenCode>
   session:    <id>
   cwd:        <absolute path>
   tmux:       <pane id>
   transcript: <absolute path>
   ```

6. **If no harness matches, say so.** Don't fall back to a made-up ID.
