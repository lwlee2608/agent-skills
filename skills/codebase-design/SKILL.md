---
name: codebase-design
description: Loads shared vocabulary and principles for designing deep modules. Invoke explicitly when designing or restructuring a module's interface, deciding where a seam goes, or making code more testable.
user-invocable: true
disable-model-invocation: true
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

**Port**: an interface at a seam that exists specifically so adapters can be swapped across it (Ports & Adapters). A port is a **seam** plus the expectation of at least two **adapters**, typically production and test. A port may be a language-level `interface`, but not every seam needs one.

**Leverage**: what callers get from depth. More capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality**: what maintainers get from depth. Change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere.

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
- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a seam unless something actually varies across it. A test double counts as the second adapter only when the real dependency cannot run in the test.

## Testability

Testability is a consequence of shape, not a separate goal. Two rules produce it:

1. **Accept dependencies, don't create them.** A module that constructs its own dependencies fixes them for every caller. Take them as parameters.
2. **Return results, don't mutate.** A module that reports what it computed leaves the decision to act with the caller.

**Don't declare an interface just so something can be mocked.** "I need to mock this" is not a reason for a port:

```
Can the real dependency run inside the test?
  yes -> use it. No interface.
        (pure logic, in-memory state, temp files,
         Postgres/Redis/Kafka in a container)
  no  -> port + two adapters, production and test.
        (third-party APIs, another team's service
         across a network seam)
```

Injecting a dependency is what makes a module testable. Declaring an interface over it is a separate decision, and only the "no" branch earns it. Mocking what you could have run proves the code calls what you told it to call: it cannot catch a wrong query, a wrong endpoint, or a schema that drifted, which are the failures that actually happen.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as a language keyword** (Go's or TypeScript's `interface`) **or a class's public methods**: too narrow: interface here includes every fact a caller must know. A concrete Go struct already has one. Declare a Go `interface` only for a **port**; with a single adapter it adds surface, not depth.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.
- **Mockability as a reason to declare an interface**: it makes every dependency look like it needs a port. Ask whether the real dependency can run in the test first; see [DEEPENING.md](DEEPENING.md) for the categories.

## Going deeper

- **Deepening a cluster given its dependencies**, see [DEEPENING.md](DEEPENING.md): dependency categories, seam discipline, and replace-don't-layer.
- **Exploring alternative interfaces**, see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md): spin up parallel sub-agents to design the interface several radically different ways, then compare on depth, locality, and seam placement.

## Credit

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design).
