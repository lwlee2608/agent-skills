---
name: review-code
description: Use when asked to review a local diff, a GitHub PR, or a whole codebase. Reports rated findings; never edits code.
user-invocable: true
argument-hint: "[diff|pr <number>|all|<path>] [--sub]"
---

# Review Code

Review a target and report findings. Each finding is rated by **severity** (how bad if it happens), **likelihood** (how often the bad path actually runs), and a **worth-fixing** verdict derived from both — plus a high-level fix when worth fixing. This skill **reports only**; it never edits code unless the user explicitly asks afterward.

## Resolve the target

Pick the target from the argument, ignoring any flags. Default to `diff` when no target is given.

1. **`diff` (default)** — local work on the current branch: uncommitted edits, unpushed commits, and already-pushed commits, reviewed together. Anchor on the base-branch fork point, **not** the branch's own remote — otherwise commits drop out of the diff once they are pushed. Include untracked files, which a plain diff omits.
2. **`pr <number>`** (or a PR URL) — review a GitHub PR: its diff plus enough PR context (title, description, base branch) to judge intent. If the GitHub CLI is unavailable, say so and fall back to `diff`.
3. **`all` / `codebase`** — review the whole repository. State the scope you can realistically cover and prioritize entry points, core logic, and recently changed files. Note anything skipped.
4. **`<path>`** — a file or directory argument scopes the review to that path.

For a diff/PR, review the changed lines **plus enough surrounding context** to judge them (callers, related functions). A bug is in scope even if the changed line only exposes it.

## Where to run the review

Default is inline. With `--sub`, run the whole review in a subagent and relay its report verbatim — use it for `all`/`codebase` or a large diff, where reading the files would bloat the session. Never re-review or paste back what the subagent returns. If the harness has no subagents, say so and review inline.

## Review lens (in priority order)

1. **Correctness** — logic errors, off-by-one, nil/null derefs, wrong conditionals, race conditions, unhandled errors, incorrect API usage, broken edge cases.
2. **Security** — injection, missing authz/authn, secrets in code, unsafe deserialization, path traversal, unvalidated input.
3. **Data & resources** — leaks (fd/memory/goroutine), unbounded growth, missing transaction boundaries, N+1 queries.
4. **Performance** — needless allocations, O(n²) on hot paths, blocking calls in loops.
5. **Maintainability** — duplication, dead code, unclear naming, missing-but-needed tests. Report these only when they materially hurt; do not pad the report with style nits.

Do not invent problems. If the code is clean, say so. Prefer a few high-confidence findings over many speculative ones.

## Rating each finding

**Severity** — impact *if* the bad path executes:
- **Critical** — data loss/corruption, security breach, crash on a common path, wrong results affecting users or money.
- **High** — wrong results or crash under realistic conditions; security issue needing some precondition.
- **Medium** — degraded behavior, perf regression, or a correctness bug on a rare path.
- **Low** — style, readability, minor inefficiency with no functional impact.

**Likelihood** — how often the triggering condition is actually met:
- **High** — hit by normal usage or common inputs.
- **Medium** — uncommon but realistic inputs/timing/config.
- **Low** — requires rare, adversarial, or near-impossible conditions.

**Worth fixing** — derived from severity × likelihood, adjusted for fix cost:

```
                 Likelihood
Severity     High        Medium      Low
Critical     Yes         Yes         Yes
High         Yes         Yes         Judgment call
Medium       Yes         Judgment    No (note only)
Low          Judgment    No          No
```

- **Yes** — recommend fixing; include a fix.
- **Judgment call** — explain the trade-off (fix effort vs. payoff) and give a recommendation; include a fix.
- **No** — note it for awareness; omit the fix or keep it to one line.

**Fix effort** — rate whenever a fix is included (Yes / Judgment call); omit for No:
- **Trivial** — a few lines, one file, no design change.
- **Small** — localized change, under an hour of work.
- **Medium** — touches several files or needs new tests.
- **Large** — refactor, design change, or risky migration.

Bump a Judgment call to **Yes** when the fix effort is Trivial; drop toward **No** when it is Large or risky relative to payoff. State the reason when you override the matrix.

## Report format

Lead with a one-line summary and a table sorted by worth-fixing (Yes first), then severity. Then one block per finding.

```
**Reviewed:** <target> — <N files, what was covered>
**Summary:** <one line: overall health + count of must-fix findings>

| # | Finding | Severity | Likelihood | Worth fixing | Fix effort |
|---|---------|----------|------------|--------------|------------|
| 1 | <short title> | High | High | Yes | Small |
| 2 | <short title> | Low | Medium | No | — |
```

Then for each:

```
### 1. <short title>
- **Location:** `path/to/file.ext:42`
- **Category:** correctness | security | resources | performance | maintainability
- **Severity:** High — <why this impact>
- **Likelihood:** High — <what triggers it>
- **Worth fixing:** Yes
- **Issue:** <what is wrong and what goes wrong as a result>
- **Fix:** <high-level approach, not a full patch — omit or keep to one line if Worth fixing = No>
- **Fix effort:** Trivial | Small | Medium | Large — <one clause on what the fix touches; omit if Worth fixing = No>
```

End with: `**Not worth fixing right now:** <one-line list>` if any No/low items were folded out, so nothing is silently dropped.

## Verification procedure

Before sending the report, check:
1. **Every finding cites a real location** (`file:line`) you actually inspected — no hypothetical line numbers.
2. **The worth-fixing verdict matches the matrix**, or you stated why you overrode it.
3. **Every "Yes" and "Judgment call" has a concrete fix and a fix-effort rating**; every fix is high-level (approach, not a finished diff), and none was applied to the working tree.
4. **Clean code is reported as clean.** If you found nothing worth fixing, say that plainly instead of manufacturing Low findings.

## Common mistakes to watch for

- **Conflating severity with likelihood.** A SQL injection reachable only by an admin is High severity / Low likelihood — rate the two axes separately.
- **Reviewing only changed lines.** A diff can introduce a bug whose root cause is in unchanged code a caller away; read enough context to judge it.
- **Guessing the target state.** If the tools return nothing or error out, report that instead of reviewing an empty target.
