---
name: writing-system-prompts
description: Use when writing or editing a system prompt for any LLM API or SDK (any code passing a `system=` / `system` role parameter, or a `.txt`/`.md` file holding such a prompt). Applies prompt-engineering and prompt-caching best practices.
user-invocable: true
---

# Writing LLM System Prompts

A well-built system prompt steers behavior across the whole conversation and — if structured for KV-cache reuse — costs a fraction of an uncached prefix on providers that offer prompt caching (Anthropic, OpenAI, Bedrock, Vertex, etc.).

## Rules

1. **Put the role first, in one sentence.** A single descriptive sentence in the system field (not the user turn) anchors tone and vocabulary, e.g. `You are a helpful coding assistant specializing in Python.` Plain prose at the top — do not wrap in markup.

2. **Order static-first, dynamic-last.** Cache hits require a byte-identical prefix. Sequence: role → tools/policies → long reference docs / few-shot examples → cache breakpoint → dynamic context → user turn. **Why:** one changed token before the breakpoint drops you from cached-read pricing (~10% of input) to full input cost.

3. **Mark cache breakpoints explicitly when the provider supports it.** Most caching is opt-in (e.g. Anthropic `cache_control`, Bedrock cachePoint). Place a breakpoint at the end of each stable block to reuse. Cache writes typically cost more than base input; reads a fraction of it. TTLs vary (commonly ~5 min, sometimes longer tiers). Only cache prefixes you'll reuse within the TTL — sparse traffic pays the write penalty repeatedly.

   ```python
   # Anthropic example — adapt to your provider's syntax
   system=[
       {"type": "text", "text": ROLE_AND_POLICIES},
       {"type": "text", "text": LONG_REFERENCE_DOC,
        "cache_control": {"type": "ephemeral"}},
   ]
   ```

4. **Never put churning content at the prefix.** Current time, request ID, user ID, or conversation summary at the top defeats caching for the whole prompt. Push them into the user turn or a post-breakpoint segment.

5. **Use structural delimiters for distinct sections.** Wrap longform inputs and behavioral directives in clear delimiters — XML tags (`<documents><document>…</document></documents>`, `<default_to_action>…</default_to_action>`), markdown headers, or named JSON fields. **Why:** delimited sections survive long contexts better than walls of prose, and several model families (notably Claude) are explicitly trained on XML structure.

6. **Place longform data above instructions in the user turn.** For 20k+ token inputs, docs at the top, question at the bottom — measured up to **30% quality lift** on multi-document tasks across major models.

7. **Write literal, scoped instructions.** Modern instruction-tuned models interpret prompts increasingly literally and won't silently generalize. If a rule applies broadly, say so: `Apply this formatting to every section, not just the first one.` Avoid ALL-CAPS shouting (`CRITICAL`, `MUST`) — it causes over-triggering on recent Claude models and adds little on others; use normal imperative voice.

8. **Tune verbosity, tone, tool use, and subagent spawning only when the default is wrong.** Examples: `Provide concise, focused responses. Skip non-essential context.` / `Use a warm, collaborative tone.` / `Spawn multiple subagents in the same turn when fanning out across items. Do not spawn a subagent for work you can complete in a single response.` Override defaults only after observing a problem — don't pre-empt.

## Verification procedure

After drafting or editing, check each:

1. **Role check** — One-sentence role at the very top of the system field?
2. **Cache-order check** — List segments top-to-bottom. Is every segment before the breakpoint stable across requests? Move per-request values below the breakpoint or into the user turn.
3. **Breakpoint check** — Is the breakpoint on the last static block? Is the cached prefix above the provider's minimum (e.g. 1024 tokens for Anthropic Opus/Sonnet, 2048 for Haiku, 1024 for OpenAI)? Below the minimum, breakpoints are silently ignored.
4. **Structure check** — Longform docs wrapped in delimiters? Behavioral blocks in named tags or sections?
5. **Literalism check** — If an instruction says "format the output" but means "format every section," rewrite with explicit scope.

## Common mistakes to watch for

- **Timestamp at the top.** `Current date: {{today}}` in the role line invalidates the cache every request. Move to the user turn.
- **Caching a tiny prefix.** A short system prompt below the provider's minimum — breakpoint silently ignored and you still pay the write surcharge. Either grow the cached block or drop the breakpoint.
- **Conversation history before the breakpoint.** History grows every request, so anything after it can never be cached. Put the breakpoint *before* the rolling history.
- **Copy-pasted legacy `CRITICAL: YOU MUST…` shouting.** Causes over-triggering on recent models. Rewrite as plain imperatives.
- **Role in the user message.** `You are a…` in `messages[0]` instead of the system field weakens steering and wastes a cacheable slot.
