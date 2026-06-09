# L05/C04 — Workflows

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-GitFlow.md) | GitFlow | 0.5 hr |
| [T02](T02-GitHub-Flow.md) | GitHub Flow | 0.5 hr |
| [T03](T03-Trunk-Based.md) | Trunk-Based Development | 1 hr |
| [T04](T04-Release-Branches.md) | Release Branches & Hotfixes | 0.5 hr |

## GitFlow (Vincent Driessen, 2010)

```
develop ──● ──● ──● ──● ──● ── (main integration branch)
              \           \
   feature/A ──● ──●        \
                     \       \
         release/1.0 ──●────●─→ tag v1.0
                            \
                main ────────● tag v1.0
                              \
                  hotfix/1.0.1 ●
                                \
                main ────────────●─→ v1.0.1
```

Branches:
- `main` — production
- `develop` — integration
- `feature/*` — new features
- `release/*` — prepping a release
- `hotfix/*` — emergency fixes

Strengths:
- Clear separation
- Good for packaged software with versioned releases

Weaknesses:
- Complex
- Slow integration (large develop → main merges)
- Discourages continuous delivery

**Modern verdict**: avoid unless you ship versioned packaged software.

## GitHub Flow

Simple:
1. Branch from `main`
2. Add commits
3. Open PR
4. Review + CI
5. Merge to `main`
6. Deploy `main`

Strengths:
- Simple
- Pairs well with continuous deployment

Weaknesses:
- No release branches for hotfix isolation
- All deployments come from `main`

## Trunk-Based Development

Everyone commits to `main` (trunk) directly or via short-lived branches (<1 day). Features behind flags. Deploy on every commit (or frequently).

```
main ──●──●──●──●──●──●──●──● (everyone here)
              ↑
        Feature flags hide
        incomplete work
```

Strengths:
- Highest DORA correlation (elite performers do this)
- Eliminates merge hell
- Forces small batches and good test coverage

Weaknesses:
- Requires discipline (small commits, tests, flags)
- Hard for teams without solid CI

## Release Branches

For organizations needing to support multiple versions:

```
main ──●──●──●──●──●──●──●──●
           \
   release/1.x ──●──●──● (cherry-pick critical fixes)
                       \
                   tag v1.0.5
```

Hotfix flow:
1. Fix on main
2. Cherry-pick to `release/1.x`
3. Tag and ship

## PR / MR Workflow Best Practices

| Practice | Why |
|---|---|
| Small PRs (< 300 LOC) | Faster review, less risk |
| Conventional commits | Auto-changelog, semver |
| Required reviews | Catches mistakes |
| CI must pass | Quality gate |
| Branch protection | Prevents direct push to main |
| Required up-to-date branch | Avoids "works in PR" surprises |
| Squash merge | Clean history |

## Squash vs Merge vs Rebase Merge (GitHub options)

| | History | Use |
|---|---|---|
| Merge commit | Preserves all PR commits + merge commit | Default; full history |
| Squash and merge | One commit per PR | Clean main; trunk-based default |
| Rebase and merge | Linear history (no merge commit) | Clean main + per-commit clarity |

## Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`, `perf`.

Example:
```
feat(auth): add OAuth login

Supports Google and GitHub providers via go-oauth2.

Closes #123
```

Enables automated semver bumping and changelog generation (semantic-release, release-please).

## Interview Themes

- "Compare GitFlow and trunk-based"
- "Why does DORA show trunk-based as best?"
- "How would you handle a hotfix on a versioned product?"
- "What are the prerequisites for trunk-based to work?"
- "Conventional commits — why?"
