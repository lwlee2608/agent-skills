---
name: codebase-design
description: Shared vocabulary for designing deep modules. Invoke explicitly to design or improve a module's interface, find deepening opportunities, decide where a seam goes, or make code more testable and AI-navigable.
user-invocable: true
disable-model-invocation: true
argument-hint: "[<module or path>]"
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever code is being designed or restructured. The aim is leverage for callers, locality for maintainers, and testability for everyone.

## Glossary

Use these terms exactly: don't substitute "component," "service," "API," or "boundary." Consistent language is the whole point.

**Module**: anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. _Avoid_: unit, component, service.

**Interface**: everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. _Avoid_: API, signature (too narrow, they refer only to the type-level surface).

**Implementation**: what's inside a module, its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth**: leverage at the interface. The amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Seam** _(Michael Feathers)_: a place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter**: a concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what's inside).

**Port**: an interface at a seam that exists specifically so adapters can be swapped across it (Ports & Adapters). A port is a **seam** plus the expectation of at least two **adapters**, typically production and test.

**Leverage**: what callers get from depth. More capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality**: what maintainers get from depth. Change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere.

## Procedure

Run these steps when invoked with a module, path, or design question. Skip straight to the relevant step if the user already named a candidate.

1. **Scope the target.** Read the given path (or ask which module is in play). Map the modules in scope and, for each, write down its interface — everything a caller must know, not just the type signature.

2. **Find the shallow ones.** Apply the **deletion test** to each: imagine deleting the module. If complexity vanishes, it was a pass-through and is a deepening candidate. If complexity reappears across N callers, it earns its keep. Flag clusters of shallow modules that always change together — those merge into one deep module.

3. **Rank by leverage.** Order candidates by how much behaviour a merged module would hide per unit of interface, and by how many call sites and tests would benefit. Present the ranked list with a one-line rationale each, and let the user pick.

4. **Classify the dependencies** of the chosen candidate, then pick its testing strategy — see [DEEPENING.md](DEEPENING.md).

5. **Design the interface.** Propose one interface directly. When the design space is genuinely wide, or the user asks for alternatives, use the parallel sub-agent pattern in [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) instead.

6. **Check the result** against the checklist below before recommending it.

## Verification checklist

Before presenting a design, confirm:

- The interface got **smaller**, not just relocated. Count entry points and parameters before and after.
- Every fact a caller must know is stated: invariants, ordering, error modes, configuration, performance.
- Tests can reach every behaviour **through** the interface. If a test needs to reach past it, the module is the wrong shape.
- Each proposed seam has at least two real adapters. One adapter is indirection, not a seam.
- The vocabulary above is used exactly — no "component", "service", "API", or "boundary".

## Deep vs shallow

**Deep module** = small interface + lots of implementation:

```
┌──────────────────────┐
│   Small Interface    │  ← Few methods, simple params
├──────────────────────┤
│                      │
│ Deep Implementation  │  ← Complex logic hidden
│                      │
└──────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid):

```
┌─────────────────────────────────┐
│        Large Interface          │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

When designing an interface, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, mockable, swappable parts; they just aren't part of the interface. A module can have **internal seams** (private to its implementation, used by its own tests) as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a seam unless something actually varies across it.

## Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them.**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, don't produce side effects.**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test setup.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow: interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.

## Going deeper

- **Deepening a cluster given its dependencies**, see [DEEPENING.md](DEEPENING.md): dependency categories, seam discipline, and replace-don't-layer testing.
- **Exploring alternative interfaces**, see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md): spin up parallel sub-agents to design the interface several radically different ways, then compare on depth, locality, and seam placement.

## Credit

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design).
