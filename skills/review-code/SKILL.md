---
name: review-code
description: Use when asked to review a local diff, a GitHub PR, or a whole codebase. Reports each finding with severity, likelihood, a worth-fixing verdict, and a high-level fix.
user-invocable: true
argument-hint: "[diff|pr <number>|all|<path>]"
---

# Review Code

Review a target and report findings. Each finding is rated by **severity** (how bad if it happens), **likelihood** (how often the bad path actually runs), and a **worth-fixing** verdict derived from both — plus a high-level fix when worth fixing. This skill **reports only**; it never edits code unless the user explicitly asks afterward.

## Resolve the target

Pick the target from the argument. Default to `diff` when none is given.

1. **`diff` (default)** — review local work on the current branch. The change can live in three places at once — uncommitted edits in the working tree, local commits not yet pushed, and commits already pushed to the branch — and is usually a mix. Gather and review all three together. Anchor the comparison on where the branch forked from its base branch, **not** on the branch's own remote — otherwise commits drop out of the diff once they are pushed. Include new untracked files, which a plain diff omits.
2. **`pr <number>`** (or a PR URL) — review a GitHub PR: its diff plus enough PR context (title, description, base branch) to judge intent. If the GitHub CLI is unavailable, say so and fall back to `diff`.
3. **`all` / `codebase`** — review the whole repository. State the scope you can realistically cover and prioritize entry points, core logic, and recently changed files. Note anything skipped.
4. **`<path>`** — a file or directory argument scopes the review to that path.

For a diff/PR, review the changed lines **plus enough surrounding context** to judge them (callers, related functions). A bug is in scope even if the changed line only exposes it.

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

Bump a Judgment call to **Yes** when the fix is trivial; drop toward **No** when the fix is large/risky relative to payoff. State the reason when you override the matrix.

## Report format

Lead with a one-line summary and a table sorted by worth-fixing (Yes first), then severity. Then one block per finding.

```
**Reviewed:** <target> — <N files, what was covered>
**Summary:** <one line: overall health + count of must-fix findings>

| # | Finding | Severity | Likelihood | Worth fixing |
|---|---------|----------|------------|--------------|
| 1 | <short title> | High | High | Yes |
| 2 | <short title> | Low | Medium | No |
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
```

End with: `**Not worth fixing right now:** <one-line list>` if any No/low items were folded out, so nothing is silently dropped.

## Verification procedure

Before sending the report, check:
1. **Every finding cites a real location** (`file:line`) you actually inspected — no hypothetical line numbers.
2. **Severity and likelihood are independent** — do not collapse them ("it's bad so it's likely"). A Critical-but-Low and a Low-but-High are both valid and common.
3. **The worth-fixing verdict matches the matrix**, or you stated why you overrode it.
4. **Every "Yes" and "Judgment call" has a concrete fix**; every fix is high-level (approach, not a finished diff).
5. **No fix was applied** to the working tree — this skill reports only.
6. **Clean code is reported as clean.** If you found nothing worth fixing, say that plainly instead of manufacturing Low findings.

## Common mistakes to watch for

- **Conflating severity with likelihood.** A SQL injection reachable only by an admin is High severity / Low likelihood — rate the two axes separately.
- **Reviewing only changed lines.** A diff can introduce a bug whose root cause is in unchanged code a caller away; read enough context to judge it.
- **Padding with style nits.** Low/Low findings drown the real issues. Fold them into the one-line "not worth fixing" list.
- **Writing fixes as full patches.** Keep fixes high-level; the user asked for findings, not edits.
- **Silently capping a codebase review.** If you could not cover everything, say what you skipped and why.
- **Missing changes that were already pushed.** Comparing against the branch's own remote hides commits once they are pushed. Anchor on the base-branch fork point so committed, pushed, and uncommitted work are all reviewed.
- **Forgetting untracked files.** Brand-new files often fall outside a plain diff — pull them in or they go unreviewed.
- **Guessing the target state.** If the tools return nothing or error out, report that instead of reviewing an empty target.
