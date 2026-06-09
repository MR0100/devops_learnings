# L05/C04/T03 — Trunk-Based Development

## Learning Objectives

- Understand trunk-based development
- Recognize prerequisites
- Apply with feature flags

## What It Is

Everyone commits to `main` (the trunk). Branches are short-lived (hours, not weeks). Or even direct commits.

```
main:    ●──●──●──●──●──●──●──●──●  (everyone here)
           ↑↑↑↑↑↑↑
           all commits to main
```

## Why It Wins

DORA research correlates trunk-based with elite performance:
- Faster deployment frequency
- Lower change failure rate
- Faster lead time
- Less merge hell

## Practices Required

### Short-Lived Branches
< 1 day life. Merge often.

### Feature Flags
Hide incomplete features. Commit half-done code; flag off in production.

```go
if featureFlag.IsEnabled("new-checkout", user) {
    return newCheckout()
}
return oldCheckout()
```

### Strong CI
- Tests must pass before merge
- Fast (< 10 min)
- Comprehensive

### Good Test Coverage
- Catch regressions automatically
- Confidence to merge

### Code Review
- PR or pre-commit review
- Lightweight, fast turnaround

## Trunk-Based Variants

### Direct to Trunk
Senior engineers push directly to main with pre-push hooks/checks.

### PR-Based
Open PR, review, merge fast (same day).

Most teams: PR-based trunk-based.

## Feature Flags Critical

Without flags: must wait for feature complete to merge.
With flags: merge as you go; ship when ready.

```
Day 1: scaffold new code (off)
Day 2: implement core logic (off)
Day 3: tests (off)
Day 4: enable for employees
Day 5: 10% of users
Day 7: 100%
Day 14: remove flag
```

## Long-Lived Feature Branch (Anti-Pattern)

```
feature/big-rewrite (3 months)
```

Reality:
- Diverges from main
- Merge becomes Everest
- Tests rotted
- Other features broken
- Risky big-bang merge

Avoid. Break into smaller pieces; merge to main behind flags.

## Hot Fixes

Same workflow:
1. Branch from main
2. Fix
3. Merge to main
4. Deploy

No special branch type. Quick PR; review; merge.

## Combined with GitHub Flow

GitHub Flow + trunk-based + feature flags = elite.

## When Trunk-Based

- Modern SaaS
- Continuous deployment
- Mature CI/CD
- Strong test culture

## When NOT

- Without tests: too risky
- Without flags: incomplete code in prod
- Versioned packaged software with QA cycles
- Compliance-heavy environments with formal gates

## Prerequisites Checklist

- [ ] Fast CI (< 10 min)
- [ ] Test coverage > 70% (varies by team)
- [ ] Feature flag system
- [ ] Auto deploy of main
- [ ] Quick rollback mechanism
- [ ] Observability for fast detection

Without these: not ready.

## Migration to Trunk-Based

1. Improve CI speed + tests
2. Add feature flag system
3. Reduce branch life (start with < 1 week target)
4. Smaller PRs
5. Increase frequency
6. Eventually: same-day commits to main

## Common Mistakes

- **Adopting without flags**: half-done features in prod
- **Adopting without tests**: cascading bugs
- **Long PRs**: defeats purpose
- **No discipline on PR size**: people merge megaPRs

## Branch Discipline

```bash
# Daily routine:
git fetch && git rebase origin/main
# work; small commits
# Quick PR; merge same day
```

## Branch Naming

```
<author>/<short-description>
alice/add-search
bob/fix-login-bug
```

Or feature-based:
```
feature/search
fix/login
```

## Stacked PRs

For larger work split into smaller pieces:
```
main → PR-1 (foundation) → PR-2 (use foundation)
```

PR-2 stacks on PR-1. Tools: `git absorb`, GitHub's GraphQL API, `git-spr`.

## Velocity Tradeoff

Trunk-based optimizes for velocity + small batches. Trades:
- More merges (but each smaller)
- More flag management
- Requires CI discipline

## Interview Prep

**Junior**: "Trunk-based dev — what?"

**Mid**: "Why DORA prefers trunk-based?"

**Senior**: "Migration from GitFlow to trunk-based."

**Staff**: "Prerequisites for trunk-based to work."

## Next Topic

→ [T04 — Release Branches & Hotfixes](T04-Release-Branches.md)
