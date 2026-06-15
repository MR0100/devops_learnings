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

## Common Mistakes

- Letting branches live for weeks; GitHub Flow assumes short-lived branches merged within days — long ones reintroduce the integration pain it was meant to avoid.
- Merging without `main` being deployable; the whole model rests on "main is always shippable," so red CI or unflagged half-features on main break the contract.
- Skipping branch protection and required reviews, turning the PR step into a rubber stamp that defeats the quality gate.
- Using GitHub Flow but needing to support multiple released versions — it has no release branches, so you'll be forced to bolt them on (that's the next topic).
- Forgetting feature flags for partially-done work, then either blocking merges or shipping incomplete features to all users.
- Treating "merge to main = deployed" as automatic without an actual CD pipeline, leaving a gap between merge and production.

## Best Practices

- Keep branches small and short-lived; open a draft PR early to get CI and feedback while the change is still cheap to redirect.
- Enforce branch protection on `main`: required status checks, required reviews, and (if you want a clean log) linear history.
- Gate incomplete work behind feature flags so you can merge continuously without exposing half-built features.
- Wire up CD so merging to `main` deploys automatically — the speed and confidence come from that automation, not the branching model alone.
- Handle "hotfixes" as ordinary fast PRs to `main`; there are no special hotfix branches in this model, which is a feature, not a gap.
- Pick a consistent merge strategy (commonly squash-merge) so `main`'s history stays readable.

## Quick Refs

```bash
# Standard cycle
git switch -c feat/short-name main
# ...small commits...
git push -u origin feat/short-name
gh pr create --fill                       # open PR; CI runs, reviewers approve
# after approval + green CI:
gh pr merge --squash --delete-branch      # or --merge / --rebase

# Keep branch current before merge
git fetch origin
git rebase origin/main                    # or: gh pr update-branch
git push --force-with-lease

# Hotfix = just a fast PR
git switch -c fix/urgent main
# ...fix...; PR; merge; CD deploys

# Branch protection (gh CLI)
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -f required_status_checks.strict=true \
  -F enforce_admins=true
```

| Need | GitHub Flow answer |
|------|--------------------|
| Where does work happen? | short-lived branch off `main` |
| How does it merge? | reviewed PR + green CI |
| How does it deploy? | CD on merge to `main` |
| Incomplete feature? | feature flag, merge anyway |
| Hotfix? | another fast PR to `main` |

## Interview Prep

**Junior**: "Describe GitHub Flow."

**Mid**: "GitHub Flow vs GitFlow."

**Senior**: "Hotfix in GitHub Flow — without release branches."

## Next Topic

→ [T03 — Trunk-Based Development](T03-Trunk-Based.md)
