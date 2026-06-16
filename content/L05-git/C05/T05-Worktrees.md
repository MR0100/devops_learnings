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

## Common Mistakes

- Trying to check out the same branch in two worktrees — Git refuses by default because both would compete to move the same ref; use a different branch or detach.
- Deleting a worktree directory with `rm -rf` instead of `git worktree remove`, leaving stale administrative entries that need `git worktree prune` to clean up.
- Expecting the index, stash, or `HEAD` to be shared across worktrees — those are per-worktree; only the object database and refs are shared.
- Moving or renaming a worktree directory in the filesystem and then finding broken metadata; use `git worktree move` (or `git worktree repair`) so Git updates its pointers.
- Forgetting uncommitted work in a secondary worktree and then `prune`-ing or removing it, losing changes that were never committed.
- Assuming worktrees give isolated config; most config is shared via the common `.git`, so per-worktree overrides need `git config --worktree` (with `extensions.worktreeConfig` enabled).

## Best Practices

- Use worktrees instead of multiple full clones when you need parallel checkouts of one repo — they share the object store, saving disk and fetch time.
- Always add and remove worktrees with `git worktree add` / `git worktree remove`, and run `git worktree prune` after any manual cleanup.
- Keep one branch per worktree; treat a worktree as "owning" its branch for the duration to avoid the same-branch conflict.
- For a clean multi-worktree setup, use a bare clone as the hub and attach worktrees to it, so no single worktree is "primary."
- Enable `extensions.worktreeConfig` and use `git config --worktree` when a worktree genuinely needs its own settings (e.g., a different signing key for a release worktree).
- Use a detached worktree (`git worktree add --detach`) for throwaway build/test checkouts you don't intend to commit on.

## Quick Refs

```bash
# Create / inspect / remove
git worktree add ../repo-feat feature/x   # new worktree on existing branch
git worktree add -b hotfix ../repo-hot main   # create branch + worktree
git worktree add --detach ../repo-test HEAD   # throwaway, no branch lock
git worktree list                             # all worktrees + their HEADs
git worktree remove ../repo-feat              # proper removal
git worktree prune                            # drop stale admin entries
git worktree move ../old ../new               # relocate safely
git worktree repair                           # fix metadata after manual moves

# Lock a worktree (e.g. on removable media) so prune won't drop it
git worktree lock --reason "USB drive" ../repo-feat
git worktree unlock ../repo-feat

# Per-worktree config
git config extensions.worktreeConfig true
git config --worktree user.signingkey <key>

# Bare-repo hub pattern
git clone --bare <url> repo.git
git -C repo.git worktree add ../main main
```

| Shared across worktrees | Per worktree |
|-------------------------|--------------|
| object database, refs/tags | `HEAD`, index, stash |
| most config | `--worktree` config overrides |
| hooks (common `.git`) | working directory contents |

## Interview Prep

**Mid**: "What's a worktree?"

**Senior**: "Use case for multiple worktrees."

**Staff**: "Worktree vs clone — when each?"

## Next Chapter

→ [C06 — Git at Scale](../C06/README.md)
