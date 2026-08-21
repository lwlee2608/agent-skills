# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**.

## Dependency categories

When assessing a candidate for deepening, classify its dependencies. The category determines whether the seam needs a port.

### 1. In-process

Pure computation, in-memory state, no I/O. Always deepenable: merge the modules. No port, no adapter.

### 2. Local-substitutable

Dependencies with local stand-ins (PGLite for Postgres, in-memory filesystem). Deepenable if the stand-in exists: run it directly. The seam is internal; no port at the module's external interface.

### 3. Remote but owned (Ports & Adapters)

Your own services across a network seam (microservices, internal APIs). Define a **port** at the seam. The deep module owns the logic; the transport is injected as an **adapter** — HTTP/gRPC/queue in production, in-memory otherwise.

Recommendation shape: *"Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it's deployed across a network."*

### 4. True external (Mock)

Third-party services (Stripe, Twilio, etc.) you don't control. The deepened module takes the dependency as an injected port; the second adapter is a mock.

## Seam discipline

- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a port unless at least two adapters are justified (typically production + test). A single-adapter seam is just indirection.
- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation, used by its own tests) as well as the external seam at its interface. Don't expose internal seams through the interface just because tests use them.

## Replace, don't layer

When a cluster is deepened, coverage moves to the new interface rather than accumulating on both sides of it. Old tests on the now-private shallow modules are waste: delete them. What replaces them asserts observable outcomes through the interface, so it survives internal refactors.
