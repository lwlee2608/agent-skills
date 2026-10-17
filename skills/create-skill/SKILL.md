---
name: create-skill
description: Use when creating a new agent skill. Ensures the skill follows quality guidelines for SKILL.md files.
user-invocable: true
argument-hint: "[<name or description>]"
---

# Create an Agent Skill

Guide the creation of a SKILL.md file that meets quality standards.

## Rules

1. **One skill, one job.** If you need "and" to describe it, split it.

2. **Name it well.** Prefer gerund form (`processing-pdfs`). Noun phrases (`pdf-processing`) and action form (`process-pdfs`) are fine. Avoid vague names like `utils` or `helpers`. Spec limits: lowercase, numbers, and hyphens; max 64 chars; no `anthropic` or `claude`.

3. **Write the description as a trigger, in third person.** It decides when the skill activates. Start with "Use when..." and name a specific condition. First-person phrasing ("I can...") hurts discovery. Max 1024 chars.
   - Bad: "Helps with diagrams."
   - Good: "Use when creating or fixing ASCII box diagrams to ensure proper alignment."

4. **Use this structure:**

   ```markdown
   ---
   name: <kebab-case-name>
   description: <"Use when..." trigger description>
   user-invocable: true
   ---

   # <Short Title>

   <1-2 sentences: what problem this solves.>

   ## Rules

   <Numbered rules, each starting with a bolded imperative.>

   ## Verification procedure (if applicable)

   <Numbered checks the agent runs on its own work.>

   ## Common mistakes to watch for (only if observed — see rule 9)

   <Observed failure modes and how to avoid them.>
   ```

5. **Start each rule with a bolded imperative** ("**Use...**", "**Never...**"). Say what is required, not how to do it.

6. **Show exact syntax only for what the agent cannot know:** project-specific formats, structured output, and bug workarounds. Skip standard CLI usage. The agent already knows it, and newer models know it better.

7. **Explain the why behind non-obvious rules** so the agent can handle edge cases.

8. **Add a verification procedure to skills that produce output.** Self-checks catch more errors than "think carefully".

9. **Document only observed mistakes.** Add "Common mistakes" only with evidence: a user report, a failure in this session, or a documented bug. Otherwise omit it. Guesses add tokens and mislead.

10. **Write guidelines, not scripts.** State the goal, constraints, and reason; let the agent choose the steps. Scripts break, cost tokens, and age as models improve. Use exact steps only for fragile operations, such as a bug workaround. Cover the 80% case with a preference and a fallback, not every edge case.

11. **Keep skills independent.** Do not assume other skills are loaded.

12. **Keep it short.** Aim under 4KB; the hard max is 500 lines. Move detail to sibling files (`reference.md`, `examples.md`) linked from SKILL.md. Keep links one level deep, because nested files may be read only partly.

## Verification procedure

1. **Name** — Meets rule 2?
2. **Description** — Third person, starts with "Use when...", ≤1024 chars?
3. **Guidelines** — Do rules state goals, not steps? Are exact steps used only for fragile operations?
4. **Syntax** — Is exact syntax shown only for what the agent cannot know?
5. **Why** — Is every non-obvious rule explained?
6. **Scope** — One job, describable without "and"?
7. **Independence** — Works without other skills loaded?
8. **Evidence** — Is every common mistake backed by evidence? Delete guesses.

## Common mistakes to watch for

- **Inventing common mistakes.** Name each entry's evidence or drop it (rule 9).
- **Spelling out standard CLI commands.** They add tokens and go stale. Say what to do; write a command only if it is project-specific or a bug workaround (rule 6).
