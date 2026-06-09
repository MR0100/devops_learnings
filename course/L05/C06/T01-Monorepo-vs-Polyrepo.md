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

## Interview Prep

**Mid**: "Monorepo vs polyrepo."

**Senior**: "Pick for a 200-engineer org."

**Staff**: "Migration cost of switching."

## Next Topic

→ [T02 — Tools (Bazel, Nx, Turborepo, Pants)](T02-Monorepo-Tools.md)
