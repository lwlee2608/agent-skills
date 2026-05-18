---
name: whiteboard-explain
description: Use when the user asks to explain, teach, or break down a technical concept, system, algorithm, or architecture. Produces a whiteboard-style explanation using plain language and ASCII diagrams instead of long technical prose.
user-invocable: true
---

# Whiteboard Explain

Explain technical things the way a good engineer would at a whiteboard: short sentences, everyday words, and a diagram that does most of the work. Use this whenever the user wants to *understand* something, not when they want code written or a task done.

## Rules

1. **Lead with a one-line "what it is".** First sentence must finish the phrase "It's basically…" in plain English. No jargon in this line. If the concept needs a term of art, define it on first use in five words or fewer.

2. **Always include at least one ASCII diagram.** Text-only explanations are banned for this skill — the diagram is the point. Pick the simplest shape that fits:
   - **Flow / pipeline** → boxes connected by `→` arrows
   - **Layers / stack** → stacked boxes, top-down
   - **Hierarchy / tree** → indented branches with `├─` `└─`
   - **Before/after or comparison** → two diagrams side-by-side or stacked with a label
   - **State machine** → labeled circles/boxes with arrows showing transitions
   - **Sequence / timing** → vertical lanes with horizontal arrows between them

3. **Use Unicode box-drawing characters** (`┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼`) and `→ ← ↑ ↓` for arrows. Plain ASCII (`+ - |`) only if the user asks. **Never mix styles in one diagram.**

4. **Cap prose at ~6 short lines per section.** If you need more, add another diagram instead. A diagram + 2 lines beats 10 lines of paragraph.

5. **Replace jargon with everyday analogies** the first time a term appears. Examples: "a mutex is like a bathroom key — only one person holds it at a time"; "a hash map is like a coat-check ticket — you hand in a key, you get back a thing." Use the technical term *after* the analogy, not before.

6. **Show, don't list.** If you are about to write a bulleted list of more than 3 items, ask whether a diagram would communicate it better. Usually yes.

7. **Skip the preamble.** No "Great question!" no "Let me explain…" no "In summary…". Start with the one-liner. End when the diagram is drawn and labeled.

8. **One concept per response.** If the user's question covers multiple concepts, explain the most important one first and offer to draw the others. Do not produce a 5-diagram brain-dump.

9. **Verify diagram alignment before sending.** Print the diagram to a file, eyeball it in fixed-width, and confirm every box row is the same width, no tabs, no trailing spaces. Misaligned boxes destroy the whiteboard feel. (If the `ascii-diagram` skill is available, use its verification loop.)

## Output template

```
It's basically <one-line plain-English description>.

<ASCII diagram>

<2–4 short lines labeling the parts of the diagram or naming the key idea>

<Optional: one analogy line if the concept is abstract>
```

## Worked example

User: *"Explain how a load balancer works."*

Good response:

```
It's basically a traffic cop in front of your servers.

         ┌──────────┐
         │  Client  │
         └────┬─────┘
              │
              ▼
        ┌───────────┐
        │   Load    │   ← picks one server per request
        │  Balancer │     (round-robin, least-busy, etc.)
        └─────┬─────┘
       ┌──────┼──────┐
       ▼      ▼      ▼
     ┌───┐  ┌───┐  ┌───┐
     │S1 │  │S2 │  │S3 │
     └───┘  └───┘  └───┘

- Client sees one address; doesn't know which server answered.
- If S2 dies, the balancer stops sending traffic there.
- More traffic? Add S4, S5… without touching the client.
```

Bad response (what to avoid):

> A load balancer is a network device or software component that distributes incoming network traffic across multiple backend servers using various algorithms such as round-robin, least-connections, IP-hash, and weighted distribution, providing horizontal scalability, fault tolerance, and high availability for distributed systems…

(Wall of text, no diagram, jargon before plain meaning — exactly what this skill prevents.)

## Verification procedure

Before sending the response, check:

1. **One-liner test** — Does sentence 1 start with "It's basically" (or equivalent plain framing) and avoid jargon? If not, rewrite.
2. **Diagram present** — Is there at least one ASCII diagram? If no diagram, the response fails this skill.
3. **Word count** — Is prose under ~6 short lines per section? If a paragraph runs long, replace half of it with a diagram or labels.
4. **Jargon check** — Scan every technical term. Is each one either (a) defined inline in ≤5 words, or (b) introduced with an everyday analogy? If not, fix it.
5. **Alignment** — Check the diagram in fixed-width: every box row same width, no tabs, no trailing spaces. (Use the `ascii-diagram` skill if available.)
6. **Scope** — Did the response explain *one* concept? If it explains 2+, cut the extras and offer them as follow-ups.

## Common mistakes to watch for

- **Drawing the diagram, then writing a paragraph that re-explains the same thing in words.** The diagram already said it — trust it. Add labels, not paragraphs.
- **Using the technical term before the analogy.** "A mutex (mutual exclusion lock) is like a bathroom key…" reads worse than "It's like a bathroom key — only one person holds it at a time. We call it a mutex." Save the term for after the picture lands.
- **ASCII art that is decorative instead of structural.** Every box, arrow, and line must mean something. If you can delete it without losing information, delete it.
- **Listing five bullet points where a tree or flow diagram would be clearer.** Bullets are a default fallback; pick the right shape (rules 2, 6).
- **Over-explaining edge cases.** Whiteboards show the happy path. Mention edge cases in one line at most, or offer to draw them separately.
