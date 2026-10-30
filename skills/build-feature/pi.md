# build-feature on Pi

Maps build-feature's spawn, wait, fix, and retire steps to the `subagent` tool from `@lwlee2608/pi-subagent`.

**Check the tool first.** It is `@lwlee2608/pi-subagent` only if `action` accepts exactly `start`, `message`, `wait`, `status`, `stop`, `reply`, and `recover`; npm `pi-subagents` also has an `action` parameter. Anything else: stop and tell the user to install `@lwlee2608/pi-subagent`. Never install or swap extensions yourself.

```json
{"action":"start","agent":"worker","lifetime":"retained","label":"<slug>","model":"<provider/model>","effort":"<effort>","task":"<brief>"}
{"action":"start","agent":"reviewer","lifetime":"once","parentWorkerId":"<worker-id>","model":"<provider/model>","effort":"<effort>","task":"<review brief>"}
{"action":"wait","runIds":["<run-id>"]}
{"action":"reply","questionId":"<question-id>","message":"<answer>"}
{"action":"message","workerId":"<worker-id>","mode":"task","label":"Round <r>","message":"<full report + fix brief>"}
{"action":"stop","workerId":"<worker-id>"}
```

**Start returns admission, not success.** Keep the `workerId` and `runId`, then `wait`. Pass the picked model and effort on every `start`; an unsupported pick fails instead of falling back.

**Omit `cwd`.** The worker builds in your checkout, so reviewers there read the PR branch. Pi children can't delegate, so the review brief never passes `--sub`.

**Wait, never poll.** `reason: "timeout"` is not failure; wait again. `reason: "attention"` means a worker asked a question: read `pendingQuestionIds`, `reply` if the answer is within your authority, else ask the user.

**Relay the full review, not the wait text.** Run results are capped at 4 KiB. Take the reviewer's last reply from `workers[].sessionFile`:

```sh
jq -rs '[.[] | select(.type=="message" and .message.role=="assistant")] | last | .message.content[] | select(.type=="text") | .text' <sessionFile>
```

Empty output or an error blocks the round; never relay the capped text.

**Fix rounds go to the same worker** as a `message` task, only once it is idle; wait on the new run ID.

**Stop the worker after the merge** and confirm `processAlive: false`.
