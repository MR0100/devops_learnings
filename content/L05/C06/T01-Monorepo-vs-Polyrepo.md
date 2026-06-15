# L05/C06/T01 — Monorepo vs Polyrepo

## Learning Objectives

- Compare monorepo and polyrepo
- Recognize when each fits

## Definitions

- **Monorepo**: one repo holding many projects/services
- **Polyrepo**: many repos, one (or few) per project

## Famous Monorepos

- **Google**: ~80% of code in single repo (billions of lines)
- **Meta**: 100M+ files
- **Microsoft**: Windows monorepo (300+ GB)
- **Twitter / X**: monorepo for backend

## Strengths of Monorepo

- **Atomic cross-project changes**: refactor lib + all consumers in one PR
- **Single dependency graph**: no version drift
- **Single source of truth**
- **Easier code reuse**
- **Easier large-scale refactoring**
- **Unified CI/CD**
- **One place to search**

## Weaknesses of Monorepo

- **Tooling needs**: standard Git slows down at huge scale
- **Build system complexity**: must rebuild only affected
- **Access control**: hard to limit who sees what
- **PR fatigue**: huge PR queues
- **Onboarding cost**: lots to ingest

## Strengths of Polyrepo

- **Team autonomy**: each team owns their repo
- **Independent versioning**: lib v1.2 vs app's pinned v1.1
- **Smaller scope**: easier to understand
- **Simpler tooling**: standard Git just works
- **Granular access control**

## Weaknesses of Polyrepo

- **Cross-repo changes hard**: update lib, then 50 PRs to consumers
- **Version drift**: lib v1, v2, v3 all in use
- **Dependency hell**: complex coordination
- **Repeated infra**: each repo has own CI config
- **Inconsistency**: each team does differently

## When Monorepo

- One team or aligned teams
- Many shared libs
- Atomic refactors important
- Have tooling investment to make it work
- Many similar services

## When Polyrepo

- Diverse, independent teams
- Lib used by external customers (separate releases)
- Different deploy cycles
- Less shared infra

## Hybrid

Many companies: ~5-10 mid-size repos. Not one giant; not 1000 tiny.

Example:
- platform-monorepo (infra, shared libs)
- frontend-monorepo (web apps)
- mobile-monorepo (iOS + Android)
- ml-monorepo (models + pipelines)

## Migration Direction

Trend has been monorepo direction for medium-large companies:
- Atomic changes outweigh team autonomy
- Tools have matured
- Easier to navigate

But: polyrepo still right for many.

## Cost of Switching

Both directions painful:
- Polyrepo → monorepo: move + re-tool
- Monorepo → polyrepo: extract + version + coordinate

Easier to choose well upfront than switch.

## Tooling Required for Monorepo

- **Bazel / Buck2 / Nx / Turborepo**: build only changed targets
- **Selective CI**: only build/test affected
- **Sparse checkout**: don't need entire repo locally
- **CODEOWNERS**: route reviews per path
- **Branch protection**: prevent unauthorized merges

## Polyrepo Coordination Tools

- **Renovate / Dependabot**: auto-update lib versions across repos
- **Cross-repo CI dependencies**: trigger downstream
- **Mono-clone tools**: `gita`, multi-repo helpers

## Real Examples

### Google (Monorepo)
- ~80% in one repo
- 50,000+ commits/day
- Custom build system (Blaze → Bazel)
- Custom Git frontend (Piper, since Git doesn't scale)

### GitHub (Polyrepo)
- Many smaller repos
- Microservice architecture
- Each team owns repos

## Common Misconceptions

- **"Monorepo = monolith"**: No. Many services in one repo is fine.
- **"Polyrepo = microservices"**: No. Polyrepo is just code organization.

## Decision Framework

| Question | Lean Toward |
|---|---|
| Cross-cutting refactors common? | Monorepo |
| Teams highly independent? | Polyrepo |
| Have build system expertise? | Monorepo |
| Want simple tooling? | Polyrepo |
| Code highly interdependent? | Monorepo |

## Common Mistakes

- Assuming "monorepo = one giant build"; without selective/affected-only builds (Bazel, Nx, Turborepo) CI time explodes as the repo grows.
- Adopting a monorepo on plain Git without partial clone / sparse-checkout and then hitting multi-GB clones and slow `git status` once the tree is huge.
- Treating polyrepo as "free isolation" while ignoring the real cost: cross-cutting changes now span many PRs, versions, and release coordination.
- Migrating repos together with `git read-tree`/naive copy and losing per-file history; use `git subtree` or `git filter-repo` to preserve it.
- Letting a monorepo's `main` get blocked by one team's broken build because there's no per-project CI gating or code-owner scoping.
- Choosing the model based on fashion rather than your actual constraints (team independence, refactor frequency, build expertise).

## Best Practices

- Match the model to constraints: monorepo when code is interdependent and you have build-system expertise; polyrepo when teams are autonomous and want simple tooling.
- For large monorepos, enable partial clone (`--filter=blob:none`) and sparse-checkout so developers and CI fetch only what they touch.
- Invest in affected-graph build tooling and remote caching from day one of a monorepo — it's the single biggest determinant of whether it scales.
- Scope ownership and required reviews with CODEOWNERS so one tree's changes route to the right team and don't block everyone.
- When splitting or merging repos, use `git filter-repo` / `git subtree split` to preserve history rather than copying files.
- Revisit the decision as the org grows; hybrid (a few well-chosen monorepos plus some standalone repos) is a legitimate and common outcome.

## Quick Refs

```bash
# Work efficiently in a large monorepo
git clone --filter=blob:none <url>        # partial clone (lazy blob fetch)
git sparse-checkout init --cone
git sparse-checkout set services/api libs/common   # only these paths
git clone --depth 1 <url>                 # shallow, history-light CI checkout

# Split one directory out into its own repo (preserve history)
git subtree split --prefix=services/api -b api-only
# then push api-only branch to a new repo, OR:
git filter-repo --path services/api/ --path-rename services/api/:

# Merge a separate repo INTO a monorepo (preserve history)
git remote add legacy ../legacy-repo
git fetch legacy
git merge --allow-unrelated-histories legacy/main

# Inspect what's big / slow
git count-objects -vH
```

| Lean toward | Signal |
|-------------|--------|
| Monorepo | frequent cross-cutting refactors, interdependent code, build expertise |
| Polyrepo | independent teams, simple tooling, loosely coupled services |
| Hybrid | a few coupled domains + many standalone services |

## Interview Prep

**Mid**: "Monorepo vs polyrepo."

**Senior**: "Pick for a 200-engineer org."

**Staff**: "Migration cost of switching."

## Next Topic

→ [T02 — Tools (Bazel, Nx, Turborepo, Pants)](T02-Monorepo-Tools.md)
