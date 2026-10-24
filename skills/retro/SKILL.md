---
name: retro
description: Use when the user asks for a retrospective on an agent session ("/retro", "how did this session go", "what could this session do better"), for the current session or a given session ID or transcript path. Reports time per phase, tool-call errors, repeated slow test runs, and skill inefficiencies. Works for Claude Code and pi.
user-invocable: true
disable-model-invocation: true
---

# Retro

Review a session transcript. Report how well it ran, where the time went, and what to change next time.

## Rules

1. **Default to the current session.** Find it by this session's ID, never by the newest file; parallel sessions share a project folder. Accept a session ID or a transcript path instead. Include subagent transcripts, since their work counts too. OpenCode keeps sessions in a database, so say it is not supported.

2. **Condense the transcript before you read it.** Transcripts run to megabytes, mostly tool output. Extract a short timeline: each user prompt, and each tool call with its time, duration, input, and error. Read a full result only when one error needs it.

3. **Time each phase.** Phases are understanding, implementing, testing, reviewing, and other (git, CI, deploy). A phase lasts until the next one starts. Time waiting for the user is not agent time; report it apart. Questions to the user and permission prompts count as user wait. Background tasks finish later than their call shows, so use their completion notice. Skip this retro's own calls.

4. **Flag slow checks run again for no reason.** Slow means Playwright, e2e, integration, full suites, or CI watches. A rerun is waste when no covered code changed, or a narrower check would have proved the fix. A rerun after a relevant change is fine.

5. **Group tool-call errors by cause.** Examples: bad path, bad args, permission denied, missing command. A failing call retried unchanged matters most.

6. **Find where effort went to waste.** Look for:
   - skill steps ignored, or skill steps that cause waste
   - the same lookup repeated
   - whole files read when a search would do
   - independent calls run one at a time
   - subagents for tiny tasks
   - user corrections ("no", "I said", "again")

   Tie each to the skill, instruction file, or habit that should change.

7. **Report only; never edit.** The user decides what to change.

8. **Grade by share of agent time wasted.** A: none. B: under 10%. C: 10–25%. D: 25–50%. F: over 50%, or the task failed.

9. **Chart the subagents when the session spawned any.** One row per agent, nested under its spawner, with bars on a shared time axis: `█` working, `░` alive but waiting on another agent. Overlapping bars ran in parallel; staggered bars ran in sequence. End each row with agent time, which counts only `█`, so parallel agents can sum past wall time. Then add the task or outcome and any waste tag. Render the chart with a script from the condensed timeline; never place bars by hand. Scale it to about 60 columns. Group `build-feature` runs by phase. Example, a `build-feature` orchestrator run at 2 minutes per column:

   ```
                       10:00          10:30          11:00          11:30
   you  orchestrator   █░░░░░░░░░░░░░░█░░░█░░█░░█░█░██░░░░░░░░░░░░░░█░███   16m
    ├─ phase 1
    │   ├─ W1  worker   ██████████████░░░░███░░░██░░                        39m
    │   ├─ R1  review                  ███                                   6m  3 findings
    │   ├─ R2  review                         ██                             5m  1 finding
    │   └─ R3  review                             ██                         4m  clean
    ├─ phase 2a
    │   ├─ W2  worker                                 ██████░░█░░███░░      19m  waste: e2e 3×, +10m
    │   ├─ R1  review                                       ██               5m  clean
    │   └─ R2  review                                          ██            4m  clean
    └─ phase 2b
        ├─ W3  worker                                 ███████░░░██░░█░░░    21m
        ├─ R1  review                                        ███             6m  2 findings
        └─ R2  review                                             ██         4m  clean
   ```

   Subagents the harness spawned on its own have no phases; list them in spawn order, with the agent type as role. Example at 1 minute per column:

   ```
                       14:00          14:15          14:30          14:45
   you  main session   ███░░░█████████████████████████░░███████░░░░░░░░░███   38m
    ├─ E1  Explore        ███                                                  3m  find auth handlers
    ├─ E2  Explore        ██                                                   2m  find session store
    ├─ G1  general                                    ██                       2m  check diagram alignment; waste: 6 lines, inline is faster
    └─ G2  general                                             ██░░█████       7m  review-code, local diff
        └─ E3  Explore                                           ██            2m  find callers
   ```

10. **Reply in this format.** Cite a timestamp for every finding. Omit empty sections. If the session ran clean, say so in one line; never invent findings.

   ```
   Session: <id> (<harness>), <start>–<end>, <agent time> agent / <user wait> user wait
   Grade: <A–F> — <one-line reason>

   Time by phase
   | Phase | Time | % | Notes |

   Subagents
   <chart from rule 9>

   Wasteful verification
   - <suite> run <N>× (<total>) at <times> — <why wasteful>; saves ~<time>

   Tool-call errors
   - <N>× <cause> at <times> — <fix>

   Improvements
   1. <file or skill>: <one-line change> — <evidence>
   ```
