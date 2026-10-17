---
name: create-skill
description: Use when creating a new agent skill. Ensures the skill follows quality guidelines for SKILL.md files.
user-invocable: true
argument-hint: "[<name or description>]"
---

# Create an Agent Skill

Guide the creation of a new SKILL.md file that meets quality standards for agent skills.

## Rules

1. **One skill, one job.** A skill should target exactly one workflow or domain. If you need the word "and" to describe what it does, split it into two skills.

2. **Prefer gerund form for names.** Per Anthropic's official guidance, use verb+ing: `processing-pdfs`, `analyzing-spreadsheets`, `writing-documentation`. Acceptable alternatives: noun phrases (`pdf-processing`) or action-oriented (`process-pdfs`). Avoid vague names (`utils`, `helpers`, `tools`) and overly generic ones (`documents`, `data`). Hard constraints from the spec: lowercase + numbers + hyphens only, max 64 chars, must not contain the reserved words `anthropic` or `claude`.

3. **Write a trigger-oriented description in third person.** The `description` field determines when the agent activates the skill. Start with "Use when..." and be specific enough to avoid false triggers but broad enough to catch the right moments. Always third person — Anthropic warns that `I can…` or `You can use this…` phrasing degrades discovery. Max 1024 chars.
   - Bad: "Helps with diagrams." / "I can fix your ASCII art."
   - Good: "Use when creating or fixing ASCII box diagrams, tables, or monospace text art to ensure proper alignment."

4. **Use this file structure:**

   ```markdown
   ---
   name: <kebab-case-name>
   description: <"Use when..." trigger description>
   user-invocable: true
   ---

   # <Short Title>

   <1-2 sentence intro: what problem this solves and when to use it.>

   ## Rules

   <Numbered, imperative rules. Each rule starts with a bolded verb phrase.>

   ## Verification procedure (if applicable)

   <Numbered checks the agent runs on its own work.>

   ## Common mistakes to watch for (only if observed — see rule 9)

   <Bulleted list of observed failure modes and how to avoid them.>
   ```

5. **Write rules in direct imperative voice.** Start each rule with a bolded action ("**Use...**", "**Never...**", "**Always prefer...**"). Each rule must be clear about what it requires, but leave the method to the agent (rule 10).

6. **Include exact syntax only for what the agent cannot know.** Provide the exact template in a fenced code block for project-specific formats, structured output, and workarounds (e.g., a flag that avoids a known bug). Do not spell out standard CLI usage; the agent already knows common tools, and newer models know their current versions better than a frozen skill does.

7. **Explain "why" for non-obvious constraints.** If a rule exists because of a bug, workaround, or past failure, state the reason so the agent can make correct judgment calls in edge cases.

8. **Include a verification procedure for skills that produce output.** Tell the agent how to check its own work. This catches more errors than generic "think carefully" instructions.

9. **Document only observed failure modes.** Add a "Common mistakes" section only when there is evidence: the user reported the mistake, it happened in this session, or it is a documented bug or gotcha. Never invent plausible-sounding mistakes to fill the section; guessed failure modes add tokens and can steer the agent wrong. If there is no evidence, omit the section.

10. **Write guidelines, not scripts.** State the goal, the constraints, and the reason, and let the agent choose the steps. Step-by-step instructions break easily, add tokens, and go out of date as models improve. Give exact steps only for fragile operations where one wrong move breaks things (e.g., a known-bug workaround). Design for the 80% case: give a preference with a fallback ("prefer X, fall back to Y") and do not try to cover every edge case.

11. **Keep skills independent.** A skill must work without assuming other skills are loaded. Cross-skill dependencies create fragile setups where uninstalling one skill silently breaks another.

12. **Keep it concise; split with progressive disclosure if needed.** Anthropic recommends SKILL.md body under **500 lines**. Aim shorter (under 4KB) when the skill fits. If content grows past that, move detail to sibling files (`reference.md`, `examples.md`, `forms.md`) and link from SKILL.md — Claude reads them on demand, so they cost zero context until needed. **Keep references one level deep** from SKILL.md; nested references can cause Claude to partial-read with `head` and miss content.

## Verification procedure

After drafting the skill, verify:

1. **Name check** — Lowercase + hyphens, ≤64 chars, no `anthropic`/`claude`? Gerund form (preferred) or noun phrase / action-oriented (acceptable)?
2. **Description check** — Third person, starts with "Use when...", ≤1024 chars, clearly describes the trigger condition?
3. **Guideline check** — Does each rule state a goal or constraint and not a sequence of steps? Are exact steps used only for fragile operations?
4. **Syntax check** — Are project-specific formats and workarounds shown with exact examples, and is standard CLI usage left out?
5. **Rationale check** — Does every non-obvious rule have a "why"?
6. **Scope check** — Does the skill do exactly one thing? Can you describe it in one sentence without "and"?
7. **Independence check** — Does the skill work standalone without other skills loaded?
8. **Evidence check** — Is every "Common mistakes" entry backed by a user report, an observed failure, or a documented bug? Delete any that are guesses.

## Common mistakes to watch for

- **Making up "Common mistakes" entries.** The agent fills the section with failure modes that sound likely but that nobody has seen happen. Before you add an entry, name its evidence (a user report, a failure seen in the session, or a documented bug). If you cannot name it, leave the entry out (rule 9).
- **Writing out standard CLI commands.** The agent already knows common tools, and newer models know their current flags better than a frozen skill does. Spelled-out commands add tokens and go out of date. Say what to do and let the agent pick the command. Write a command out only when it is project-specific or works around a known bug (rule 6).
