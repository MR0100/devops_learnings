# L05/C04/T01 — GitFlow

## Learning Objectives

- Understand GitFlow's branching model
- Recognize when it fits

## Branches

- **main** — production
- **develop** — integration / latest "done" work
- **feature/\*** — new features (off develop)
- **release/\*** — preparing a release (off develop)
- **hotfix/\*** — emergency fixes (off main)

## Workflow

```
main:    ●─────●─────●  (v1.0, v1.1, v1.2 tags)
              /     /
             /     /
develop:  ●─●─●─●─●─●─●─●
              \       /
   feature/a:  ●─●─●
                    \
                     ●  (merged to develop when done)
```

## Typical Sequence

### Feature
```bash
git switch develop
git switch -c feature/login
# work
git switch develop
git merge --no-ff feature/login
git branch -d feature/login
```

### Release
```bash
git switch develop
git switch -c release/1.0
# bug fixes, version bumps
git switch main
git merge --no-ff release/1.0
git tag v1.0
git switch develop
git merge --no-ff release/1.0
git branch -d release/1.0
```

### Hotfix
```bash
git switch main
git switch -c hotfix/1.0.1
# fix
git switch main
git merge --no-ff hotfix/1.0.1
git tag v1.0.1
git switch develop
git merge --no-ff hotfix/1.0.1
git branch -d hotfix/1.0.1
```

## Strengths

- Clear separation
- Good for versioned releases
- Multiple versions supported simultaneously
- Explicit "in QA" via release branches

## Weaknesses

- Many long-lived branches
- High merge complexity
- Slow integration
- Discourages continuous delivery
- "Big bang" releases

## When GitFlow Fits

- Versioned packaged software (desktop, mobile apps via stores)
- Multiple versions in support
- Long QA cycles
- Regulated industries with formal release process

## When NOT

- Continuous delivery / SaaS
- Single-version product
- Trunk-based culture
- Small teams (overhead doesn't pay off)

## Tooling

`git-flow` extension automates:
```bash
git flow init
git flow feature start foo
git flow feature finish foo
git flow release start 1.0
git flow release finish 1.0
```

## Modern Verdict

For most modern web/SaaS teams: skip GitFlow.

For desktop/mobile with versioning: still relevant.

## Comparison

|  | GitFlow | GitHub Flow | Trunk-Based |
|---|---|---|---|
| Long-lived | develop, main | main | main |
| Feature life | days-weeks | hours-days | hours |
| Release | branch | from main | continuous |
| DORA elite | unlikely | possible | best |

## DORA Correlation

DORA research: trunk-based development correlates with elite performance. GitFlow doesn't.

## Hybrid

Some teams use GitFlow's release/hotfix concepts without `develop`:
- Work on main
- For release: tag main
- For hotfix: branch from tag

Best of both.

## Common Mistakes

- Adopting GitFlow for a single continuously-deployed web app, where the `develop`/`release` ceremony adds overhead with no payoff — it was designed for versioned, scheduled-release software.
- Letting `develop` and `main` drift apart because hotfixes merged to `main` were never merged back into `develop`, so the next release silently regresses the fix.
- Treating feature branches as long-lived; GitFlow doesn't forbid that, and stale features turn integration into a conflict marathon.
- Forgetting to tag `main` when finishing a release, losing the clean anchor you need for hotfix branches and `git describe`.
- Cherry-picking a hotfix into `develop` instead of merging the hotfix branch into both `main` and `develop`, which loses the merge link and can cause duplicate-commit conflicts later.
- Using GitFlow as an excuse to batch huge releases, undermining the small-batch deployment that DORA metrics correlate with high performance.

## Best Practices

- Reserve GitFlow for software with real versioned releases and multiple supported versions (desktop apps, libraries, firmware), not rapidly-deployed SaaS.
- Always merge hotfix branches into *both* `main` and `develop` (or back-merge `main`→`develop` after) so fixes never get lost.
- Keep feature branches short and rebase/merge from `develop` frequently to keep integration cheap.
- Tag every release on `main` with an annotated, ideally signed tag so it's a durable, describable anchor.
- Automate the branch ceremony (git-flow extensions or release tooling) so the rules are enforced rather than remembered.
- Periodically reassess: if you deploy from `develop` constantly, you've effectively outgrown GitFlow — consider GitHub Flow or trunk-based.

## Quick Refs

```bash
# Feature
git switch -c feature/x develop
# ...work...
git switch develop && git merge --no-ff feature/x

# Release
git switch -c release/1.4 develop
# bump version, fix bugs only
git switch main && git merge --no-ff release/1.4
git tag -a v1.4 -m "Release 1.4"
git switch develop && git merge --no-ff release/1.4   # back-merge!

# Hotfix (from a released tag/main)
git switch -c hotfix/1.4.1 main
# ...fix...
git switch main && git merge --no-ff hotfix/1.4.1
git tag -a v1.4.1 -m "Hotfix"
git switch develop && git merge --no-ff hotfix/1.4.1  # don't forget develop

# git-flow extension equivalents
git flow feature start x   /  git flow feature finish x
git flow release start 1.4 /  git flow release finish 1.4
git flow hotfix  start 1.4.1
```

| Branch | From | Merges to |
|--------|------|-----------|
| feature/* | develop | develop |
| release/* | develop | main + develop |
| hotfix/* | main | main + develop |

## Interview Prep

**Junior**: "What's GitFlow?"

**Mid**: "GitFlow drawbacks."

**Senior**: "When use GitFlow today?"

## Next Topic

→ [T02 — GitHub Flow](T02-GitHub-Flow.md)
