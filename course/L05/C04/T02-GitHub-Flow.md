# L05/C04/T02 — GitHub Flow

## Learning Objectives

- Apply GitHub Flow
- Compare to GitFlow

## The Flow

1. Branch from main
2. Add commits
3. Open Pull Request
4. Discuss + review
5. Deploy from PR branch (optional)
6. Merge to main
7. Deploy main

That's it. Simple.

## Diagram

```
main:    ●─●─●─●─●─●─●
            \   /\  /
            feature1  feature2
```

Short-lived branches; merged when reviewed.

## Why Simple Wins

- Just one long-lived branch (main)
- Always deployable
- Continuous integration natural
- Clear "merged = done"
- No release branches to maintain

## Compared to GitFlow

| | GitHub Flow | GitFlow |
|---|---|---|
| Long branches | main only | main + develop |
| Release process | Continuous | Release branches |
| Hotfix | Just another PR | Hotfix branches |
| Complexity | Low | High |
| Best for | SaaS / web | Versioned software |

## Workflow Steps

```bash
git switch main
git pull
git switch -c feature/add-login

# Work
git add .
git commit -m "Add login"
git push -u origin feature/add-login

# Open PR on GitHub
# Review feedback; push more commits
# CI runs; reviewers approve
# Merge via GitHub UI (squash / merge commit / rebase)
```

## Deployment

GitHub Flow assumes: main is always deployable. CD pipelines deploy main automatically.

For PR previews: deploy ephemeral environment per PR (Vercel, Netlify, custom).

## Merging Strategies on GitHub

- **Merge commit**: preserve PR history, one merge commit per PR
- **Squash merge**: collapse PR into one commit on main
- **Rebase and merge**: linear history, no merge commit

Pick one team-wide. Most modern teams: squash.

## When GitHub Flow

- SaaS / continuous delivery
- Single product, no version branches
- Small to medium team
- Want simplicity

## When NOT

- Need release branches for QA cycles
- Multiple versions supported (1.x, 2.x both live)
- Regulated industries with formal release gates

## Hotfix in GitHub Flow

No special branch type:
1. Branch from main
2. Fix
3. PR (expedited review)
4. Merge + deploy

Same as any PR; just urgent.

## Feature Flags

Critical companion for GitHub Flow:
- Code can be on main (merged) but feature off
- Gradual rollout via flag
- No need to delay merges

Combined: trunk-based + GitHub Flow + feature flags = elite practice.

## Common Patterns

### Long PRs
Anti-pattern. Keep PRs small (< 300 LOC).

### Stale Branches
Auto-delete branches after merge (GitHub setting).

### Required Reviews
1-2 reviewers required before merge.

### Required Checks
CI must pass.

### Branch Protection
- No direct push to main
- Force protect main
- Require up-to-date

## Tooling

GitHub built-in. GitLab MR equivalent. Bitbucket pull request equivalent.

## Interview Prep

**Junior**: "Describe GitHub Flow."

**Mid**: "GitHub Flow vs GitFlow."

**Senior**: "Hotfix in GitHub Flow — without release branches."

## Next Topic

→ [T03 — Trunk-Based Development](T03-Trunk-Based.md)
