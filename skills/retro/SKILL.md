---
name: retro
description: Use when the user asks for a retrospective on an agent session ("/retro", "how did this session go", "what could this session do better"), for the current session or a given session ID or transcript path. Reports time per phase, tool-call errors, repeated slow test runs, and skill inefficiencies. Works for Claude Code and pi.
user-invocable: true
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

9. **Draw the subagent tree when the session spawned any.** Nest each agent under its spawner, one line each: ID, role and task, span, agent time, outcome. Agent time excludes waiting on other agents, so parallel agents can sum past wall time. Group `build-feature` runs by phase. Tag waste at the end of its line. Example, a `build-feature` orchestrator run:

   ```
   you  orchestrator                        10:00–11:40  14m
    ├─ phase 1                              10:02–11:01
    │   ├─ W1  worker  build, PR #12        10:02–10:54  39m
    │   ├─ R1  review  round 1, 3 findings  10:32–10:38   6m
    │   ├─ R2  review  round 2, 1 finding   10:46–10:51   5m
    │   └─ R3  review  round 3, clean       10:55–10:59   4m
    ├─ phase 2a (parallel with 2b)          11:02–11:35
    │   ├─ W2  worker  build, PR #13        11:02–11:30  24m  waste: e2e 3×, +10m
    │   ├─ R1  review  round 1, clean       11:14–11:19   5m
    │   └─ R2  review  round 2, clean       11:21–11:25   4m
    └─ phase 2b (parallel with 2a)          11:02–11:38
        ├─ W3  worker  build, PR #14        11:02–11:33  27m
        ├─ R1  review  round 1, 2 findings  11:16–11:22   6m
        └─ R2  review  round 2, clean       11:27–11:31   4m
   ```

   Subagents the harness spawned on its own have no phases; list them in spawn order, role as agent type, task as spawn description:

   ```
   you  main session                         14:00–14:52  31m
    ├─ E1  Explore  find auth handlers       14:03–14:06   3m
    ├─ E2  Explore  find session store       14:03–14:05   2m
    ├─ G1  general  check diagram alignment  14:31–14:33   2m  waste: 6-line diagram, inline is faster
    └─ G2  general  review-code, local diff  14:40–14:49   9m
        └─ E3  Explore  find callers         14:42–14:44   2m
   ```

10. **Reply in this format.** Cite a timestamp for every finding. Omit empty sections. If the session ran clean, say so in one line; never invent findings.

   ```
   Session: <id> (<harness>), <start>–<end>, <agent time> agent / <user wait> user wait
   Grade: <A–F> — <one-line reason>

   Time by phase
   | Phase | Time | % | Notes |

   Subagents
   <tree from rule 9>

   Wasteful verification
   - <suite> run <N>× (<total>) at <times> — <why wasteful>; saves ~<time>

   Tool-call errors
   - <N>× <cause> at <times> — <fix>

   Improvements
   1. <file or skill>: <one-line change> — <evidence>
   ```
