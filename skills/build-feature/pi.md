# build-feature on Pi

Maps build-feature's spawn, wait, continue, resume, and retire steps to the `subagent` tool from `@lwlee2608/pi-subagent`.

**Check the tool before asking how to build.** It is `@lwlee2608/pi-subagent` only if `action` accepts exactly `start`, `message`, `wait`, `status`, `stop`, `reply`, and `recover` — npm `pi-subagents` also has an `action` parameter, so its presence proves nothing. No `subagent` tool: stop and tell the user to install `@lwlee2608/pi-subagent`. Any other `subagent` tool: ignore the calls below and build Solo with its one-shot reviewer through its own API; leave Orchestrator out of the mode question and say it needs `@lwlee2608/pi-subagent`. Never install or swap extensions yourself, and never load two `subagent` tools.

```json
{"action":"start","agent":"worker","lifetime":"retained","cwd":"<phase-worktree>","label":"Phase <n>","model":"<provider/model>","effort":"<effort>","task":"<brief>"}
{"action":"start","agent":"reviewer","lifetime":"once","cwd":"<phase-worktree>","model":"<provider/model>","effort":"<effort>","task":"<review brief>"}
{"action":"wait","runIds":["<run-id>"]}
{"action":"reply","questionId":"<question-id>","message":"<answer>"}
{"action":"message","workerId":"<worker-id>","mode":"task","label":"Phase <n> round <r>","message":"<full report + fix brief>"}
{"action":"recover","workerId":"<worker-id>"}
{"action":"stop","workerId":"<worker-id>"}
```

**Start returns admission, not success.** Keep the returned `workerId` and `runId`, then `wait`. Pass the recorded model and effort on every `start`; an unsupported pick fails instead of falling back.

**You own the worktree.** Create it on the phase branch before starting the worker — `git worktree add -b <plan>-phase-<n> <path> integrate/<plan-name>` — so the worker skips cutting the branch.

**Reviewers run in the phase worktree.** An omitted `cwd` is your checkout on the integration branch, where the reviewer reads pre-PR code. Solo: omit it, your checkout is the phase branch. Drop `--sub` from the `review-code` target — Pi children can't delegate. A `once` reviewer retires itself and keeps its result.

**Wait, never poll.** `reason: "timeout"` is not failure — wait again. `reason: "attention"` means any owned worker asked a question, maybe not one you waited on: read `pendingQuestionIds` and `status`, `reply` if the answer is within your authority, else ask the user. `cancelled: true` in place of `message` interrupts the worker; it never licenses a guess. After replying, wait on the same run ID. Finished runs report `runs[].result.outcome`: `completed`, `failed`, or `interrupted`.

**Relay the full review, not the wait text.** Run result text is capped at 4 KiB. Extract the reviewer's final reply from `workers[].sessionFile` in the wait result:

```sh
jq -rs '[.[] | select(.type=="message" and .message.role=="assistant")] | last | .message.content[] | select(.type=="text") | .text' <sessionFile>
```

Empty output or an error blocks the review cycle — never relay the capped text instead.

**Fix rounds go to the original worker** as a `message` task, only once it's idle; it returns a new run ID to wait on. A working worker accepts only `mode: "steer"`.

**Resume only in the original parent session.** `status` lists its saved workers. A closed one: `recover` reopens it idle and replays nothing, so follow with a `message` task carrying the context it needs; old question IDs stay cancelled. Refused recovery is a blocker — report it; never remove locks, swap models, or adopt another parent's worker. A different parent session: brief a fresh worker, as SKILL.md says.

**Retire before cleanup.** After the merge: `stop` the worker, confirm `processAlive: false`, `git worktree remove <path>`, then delete the phase branch — git refuses to delete a branch checked out in a worktree. A failed stop blocks the removal.
