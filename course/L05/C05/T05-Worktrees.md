# L05/C05/T05 — Worktrees

## Learning Objectives

- Use multiple worktrees from one repo
- Save context-switch overhead

## What Worktrees Are

Multiple working directories sharing one `.git/` database. Each worktree can be on a different branch.

```
repo/
  .git/                  ← shared object DB
  (main worktree files)
repo-feature/
  .git                   ← small file pointing back
  (feature branch files)
```

## Creating

```bash
# In main worktree
git worktree add ../repo-feature feature/foo
# Creates ../repo-feature with feature/foo checked out

git worktree add ../repo-hotfix hotfix/bug
```

## Why Use

### Avoid Stash Dance
Without worktree:
```bash
git stash
git switch other-branch
# work
git switch back
git stash pop
```

With worktree: just `cd` to other worktree. Work on multiple branches simultaneously.

### Parallel Builds
- Worktree A: building latest
- Worktree B: running tests on different branch
- Independent

### Hot Fixes During Development
- Main worktree: feature work in progress
- Second worktree: quick hotfix without interrupting

## List

```bash
git worktree list
# /path/to/repo          abc1234 [main]
# /path/to/repo-feature  def5678 [feature/foo]
```

## Remove

```bash
git worktree remove ../repo-feature
```

Or delete dir + `git worktree prune` to clean up.

## Locked Worktrees

```bash
git worktree lock /path/to/wt
git worktree unlock /path/to/wt
```

Locked: won't be auto-removed by `git worktree prune`.

## Shared vs Per-Worktree

Shared (across worktrees):
- Objects (.git/objects/)
- Refs (.git/refs/, packed-refs)
- Config (.git/config) — mostly
- Hooks
- Stash

Per-worktree:
- HEAD
- Index (.git/index)
- Working files

## One Branch Per Worktree

A branch can be checked out in only ONE worktree at a time.

If you try:
```bash
git worktree add ../wt2 main      # error if main already checked out somewhere
```

Workaround: use a detached HEAD or different branch.

## Compared to Multiple Clones

Worktree: shares objects → smaller disk.
Multiple clones: independent → can diverge.

For local dev: worktree wins (less disk; same refs).

## Use Cases

### Long-Running Branches
```bash
# Day-to-day: main worktree on main
# Long feature: separate worktree at ../repo-feature
# No constant branch switching
```

### Compare Branches Side-by-Side
```bash
git worktree add ../repo-old v1.0
# Compare current with old version
```

### Build/Test While Coding
```bash
# Main worktree: actively coding
# Test worktree: CI-like build/test on same branch
```

## Subworktree (Linked Worktree)

The "secondary" worktrees are linked. The original is the "main" worktree.

Distinction in `git worktree list`:
- (bare): bare repo
- (detached HEAD)
- normal: branch name

## Configuration

```bash
# Global config: all worktrees
git config --global user.email "..."

# Per-worktree: only that worktree
git config user.email "alt@example.com"
```

## Bare Repos with Worktrees

Common setup:
```bash
git clone --bare url repo.git
cd repo.git
git worktree add ../main main
git worktree add ../feature feature/x
```

No "main" working directory; just worktrees.

## When NOT Use

- Tiny repo (overhead not worth)
- Single short-lived branch
- Team using IDE that doesn't handle worktree well

## Common Operations

```bash
git worktree list
git worktree add path branch
git worktree remove path
git worktree prune              # clean stale entries
git worktree move src dst       # rename/move
git worktree repair             # fix metadata
```

## Modern Editor Support

VS Code: open additional worktree as separate window.
JetBrains: each worktree as separate project.

## Interview Prep

**Mid**: "What's a worktree?"

**Senior**: "Use case for multiple worktrees."

**Staff**: "Worktree vs clone — when each?"

## Next Chapter

→ [C06 — Git at Scale](../C06/README.md)
