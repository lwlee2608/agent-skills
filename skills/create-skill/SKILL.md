---
name: create-skill
description: Use when creating a new agent skill. Ensures the skill follows quality guidelines for SKILL.md files.
user-invocable: true
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

   <Numbered steps the agent follows to check its own work.>

   ## Common mistakes to watch for (if applicable)

   <Bulleted list of predictable failure modes and how to avoid them.>
   ```

5. **Write rules in direct imperative voice.** Start each rule with a bolded action ("**Use...**", "**Never...**", "**Always prefer...**"). Rules must be specific enough that two agents would follow them the same way.

6. **Include exact syntax for anything format-sensitive.** If the skill involves CLI commands, file formats, or structured output, provide the exact command or template in a fenced code block. Do not leave format details to interpretation.

7. **Explain "why" for non-obvious constraints.** If a rule exists because of a bug, workaround, or past failure, state the reason so the agent can make correct judgment calls in edge cases.

8. **Include a verification procedure for skills that produce output.** Tell the agent how to check its own work. This catches more errors than generic "think carefully" instructions.

9. **Document common failure modes.** LLMs make predictable, repeated mistakes. List the top 3-5 mistakes for the skill's domain so the agent can avoid them.

10. **Design for the 80% case.** Over-specified skills become brittle. Establish a preference hierarchy with fallbacks (e.g., "prefer X, fall back to Y if X is unavailable") rather than trying to cover every edge case.

11. **Keep skills independent.** A skill must work without assuming other skills are loaded. Cross-skill dependencies create fragile setups where uninstalling one skill silently breaks another.

12. **Keep it concise; split with progressive disclosure if needed.** Anthropic recommends SKILL.md body under **500 lines**. Aim shorter (under 4KB) when the skill fits. If content grows past that, move detail to sibling files (`reference.md`, `examples.md`, `forms.md`) and link from SKILL.md — Claude reads them on demand, so they cost zero context until needed. **Keep references one level deep** from SKILL.md; nested references can cause Claude to partial-read with `head` and miss content.

## Verification procedure

After drafting the skill, verify:

1. **Name check** — Lowercase + hyphens, ≤64 chars, no `anthropic`/`claude`? Gerund form (preferred) or noun phrase / action-oriented (acceptable)?
2. **Description check** — Third person, starts with "Use when...", ≤1024 chars, clearly describes the trigger condition?
3. **Rule clarity** — Could two different agents follow each rule identically without ambiguity?
4. **Syntax check** — Are all format-sensitive outputs shown with exact examples?
5. **Rationale check** — Does every non-obvious rule have a "why"?
6. **Scope check** — Does the skill do exactly one thing? Can you describe it in one sentence without "and"?
7. **Independence check** — Does the skill work standalone without other skills loaded?

## Common mistakes to watch for

- **Vague descriptions**: "Helps with X" gives the agent no trigger signal. Always use "Use when..." with a specific condition.
- **Missing code examples**: Rules like "format the output correctly" without showing the exact format leave too much to interpretation.
- **Over-scoping**: Combining "create and validate and deploy" into one skill. Split them.
- **Generic CoT padding**: "Think carefully before proceeding" wastes tokens. Use domain-specific reasoning steps instead (e.g., "Calculate box widths from content before drawing").
- **No verification step**: The skill tells the agent what to do but never how to check if it did it right.
- **Wrong naming form**: `helper`, `utils`, `my-skill`, or names containing `claude`/`anthropic` (the latter two are rejected by the spec). Default to gerund form (`writing-X`, `processing-X`) unless a noun phrase reads more naturally.
- **First-person description**: `I can help you…` or `You can use this to…` degrades discovery. Always third person: `Processes X. Use when…`.
