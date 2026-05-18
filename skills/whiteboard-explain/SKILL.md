---
name: whiteboard-explain
description: Use when the user asks to explain or teach a technical concept. Replies in plain language with a simple diagram instead of a wall of jargon.
user-invocable: true
---

# Whiteboard Explain

Explain it the way a good engineer would at a whiteboard. The goal: the user understands. Nothing else.

- Plain English. Everyday words. Short sentences.
- Use a small diagram whenever it makes things clearer than words.
- Analogy first, technical term second.
- One concept per response. No preamble, no recap.

## Worked example

User: *"Explain how a load balancer works."*

Good:

```
It's basically a traffic cop in front of your servers.

         ┌──────────┐
         │  Client  │
         └────┬─────┘
              ▼
        ┌───────────┐
        │   Load    │   ← picks one server per request
        │  Balancer │
        └─────┬─────┘
       ┌──────┼──────┐
       ▼      ▼      ▼
     ┌───┐  ┌───┐  ┌───┐
     │S1 │  │S2 │  │S3 │
     └───┘  └───┘  └───┘

- Client sees one address; doesn't know which server answered.
- If S2 dies, the balancer stops sending there.
- More traffic? Add S4, S5… client unchanged.
```

Bad — what this skill prevents:

> A load balancer is a network device or software component that distributes incoming traffic across multiple backend servers using algorithms such as round-robin, least-connections, IP-hash… (wall of jargon, no picture.)
