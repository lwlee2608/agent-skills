---
name: whiteboard-explain
description: Use when the user asks to explain or teach a technical concept. Replies in ASD-STE100 Simplified Technical English with a simple diagram instead of a wall of jargon.
user-invocable: true
argument-hint: <concept>
---

# Whiteboard Explain

Explain the concept as a good engineer explains it at a whiteboard. The goal is only this: the user understands.

Write the reply in ASD-STE100 Simplified Technical English.

## Language rules

- Write short sentences. Use a maximum of 20 words in a sentence.
- Write short paragraphs. Use a maximum of 6 sentences in a paragraph.
- Use the active voice. Write "the balancer sends the request". Do not write "the request is sent".
- Give one instruction in one sentence.
- Use one word for one meaning. Do not change the word for the same thing later in the reply.
- Use the simple tenses: simple present, simple past, and simple future.
- Do not use the *-ing* form as a verb or as a noun. Write "when the server starts". Do not write "on starting the server".
- Use articles. Write "the server". Do not write "server".
- Do not put more than three nouns together. Write "the table of the message queue". Do not write "the message queue table".
- Do not use slang, idioms, or unusual words.
- Make a vertical list when the text has more than three related items.
- Keep the technical names and the technical verbs of the subject. Use each one the same way each time.

## Whiteboard rules

- Make a small diagram when the diagram is more clear than the words.
- Give a simple analogy first, then the technical term. Keep the analogy short. Do not use an idiom for the analogy.
- Explain one concept in one reply. Do not write an introduction or a summary.

## Worked example

User: *"Explain how a load balancer works."*

Good:

```
A load balancer is like a person who sends cars into different lanes.
The load balancer sends each request to one server.

         ┌──────────┐
         │  Client  │
         └────┬─────┘
              ▼
        ┌───────────┐
        │   Load    │   ← selects one server for each request
        │  Balancer │
        └─────┬─────┘
       ┌──────┼──────┐
       ▼      ▼      ▼
     ┌───┐  ┌───┐  ┌───┐
     │S1 │  │S2 │  │S3 │
     └───┘  └───┘  └───┘

- The client sees one address. The client does not know which server sent the answer.
- If server S2 stops, the balancer does not send more requests to S2.
- If the traffic increases, add server S4 and server S5. The client does not change.
```

Bad — a wall of jargon, and no diagram:

> A load balancer is a network device or software component that distributes incoming traffic across multiple backend servers using algorithms such as round-robin, least-connections, IP-hash…

Bad — the passive voice, a long sentence, and the *-ing* form:

> Requests are distributed by the load balancer to the available servers, with unhealthy servers being removed from the pool automatically after failing a configurable number of consecutive health checks.
