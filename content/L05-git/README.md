# L05 — Version Control & Git Internals

## Overview

Every change in DevOps starts with Git. Knowing it as a *user* gets you to mid-level. Knowing it as a *system* (objects, refs, packs) gets you to senior+.

**7 chapters, 27 topics.**

## Chapter Map

### [C01](C01/) — Git Fundamentals
- T01 Working Directory, Staging, Repository
- T02 Commits, Trees, Blobs (The Object Model)
- T03 Refs, HEAD, Branches, Tags
- T04 Remotes, fetch/pull/push

### [C02](C02/) — Git Internals
- T01 The .git Directory Tour
- T02 Pack Files and Garbage Collection
- T03 The Reflog (Your Safety Net)
- T04 Plumbing vs Porcelain Commands

### [C03](C03/) — Branching & Merging
- T01 Fast-Forward vs Three-Way Merge
- T02 Rebase vs Merge (The Real Tradeoffs)
- T03 Cherry-Pick, Revert, Reset
- T04 Resolving Conflicts at Scale

### [C04](C04/) — Workflows
- T01 GitFlow
- T02 GitHub Flow
- T03 Trunk-Based Development
- T04 Release Branches & Hotfixes

### [C05](C05/) — Advanced Git
- T01 Interactive Rebase, Squash, Fixup
- T02 bisect for Finding Bugs
- T03 Submodules vs Subtrees
- T04 Git LFS for Large Files
- T05 Worktrees

### [C06](C06/) — Git at Scale
- T01 Monorepo vs Polyrepo
- T02 Tools (Bazel, Nx, Turborepo, Pants)
- T03 Code Owners & Branch Protection
- T04 Commit Signing (GPG, Sigstore)

### [C07](C07/) — Git Hooks & Automation
- T01 Client-Side Hooks (pre-commit, commit-msg, pre-push)
- T02 Server-Side Hooks
- T03 pre-commit Framework
- T04 Conventional Commits

## The Git Object Model

```
Commit ───► Tree ───► Blob (file content)
   │
   └─► parent Commit ───► Tree ───► Blob

(everything is content-addressed by SHA-1/256)
```

Everything in Git is:
- **Blob** — file content
- **Tree** — directory listing (filename → blob/tree)
- **Commit** — pointer to a tree + parents + author + message
- **Tag** — pointer to a commit (annotated) or just a ref (lightweight)

## Refs

Refs are named pointers to commits:
- `.git/refs/heads/main` — branches
- `.git/refs/tags/v1.0` — tags
- `.git/refs/remotes/origin/main` — remote-tracking branches
- `.git/HEAD` — current branch / detached state
- `.git/packed-refs` — packed refs (after gc)

## Trunk-Based vs GitFlow

| | GitFlow | Trunk-Based |
|---|---|---|
| Branches | develop, feature, release, hotfix | main + short-lived branches |
| Best for | Periodic versioned releases | Continuous delivery |
| Modern use | Legacy / packaged software | SaaS, modern DevOps |
| DORA correlation | Lower elite | Higher elite |

## Recommended Reading

- *Pro Git* — Scott Chacon, Ben Straub (free online)
- *Git Internals* (Pro Git Ch 10) — best 60 pages on the topic
- `man gitcore-tutorial`

## Interview Relevance

- "Explain Git internals"
- "Difference between merge and rebase, and when each"
- "How do you recover a deleted commit?"
- "Compare monorepo vs polyrepo"

## Next

→ [L06 — Programming for DevOps (Python & Go)](../L06-programming-for-devops/README.md)
