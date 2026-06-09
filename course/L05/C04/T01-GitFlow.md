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

## Interview Prep

**Junior**: "What's GitFlow?"

**Mid**: "GitFlow drawbacks."

**Senior**: "When use GitFlow today?"

## Next Topic

→ [T02 — GitHub Flow](T02-GitHub-Flow.md)
