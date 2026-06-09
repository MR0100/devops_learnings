# L05/C05 — Advanced Git

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Interactive-Rebase.md) | Interactive Rebase, Squash, Fixup | 1 hr |
| [T02](T02-Bisect.md) | bisect for Finding Bugs | 0.5 hr |
| [T03](T03-Submodules-Subtrees.md) | Submodules vs Subtrees | 0.5 hr |
| [T04](T04-Git-LFS.md) | Git LFS for Large Files | 0.5 hr |
| [T05](T05-Worktrees.md) | Worktrees | 0.5 hr |

## Interactive Rebase

The most powerful Git command. Rewrites history.

```bash
git rebase -i HEAD~5
```

Opens an editor:
```
pick abc123 Add feature
pick def456 Fix typo
pick ghi789 Add tests
pick jkl012 More fixes
pick mno345 Polish

# Commands:
# p, pick = use commit
# r, reword = change message
# e, edit = pause to amend
# s, squash = meld into previous (keep both messages)
# f, fixup = meld into previous (discard this message)
# d, drop = remove commit
# x, exec = run a command
# b, break = pause here
# l, label = name this point
# r, reset = move to that point
# m, merge = recreate merge
```

### Typical Patterns

```
pick abc Add feature
fixup def    ← merges fix into above silently
squash ghi   ← merges with combined message
pick jkl Polish
drop mno     ← removes
```

### Fixup with autosquash

```bash
# Commit pointing at a target
git commit --fixup=abc123 -m "..."
git commit --fixup=abc123       # editor opens
git commit --squash=abc123 -m "..."

# Then rebase will auto-arrange
git rebase -i --autosquash HEAD~10
```

## git bisect

Binary search for the commit that introduced a bug.

```bash
git bisect start
git bisect bad HEAD              # current is broken
git bisect good v1.0             # this was working

# Git checks out a midpoint
./run-tests.sh
git bisect good                  # or `bad`
# ... repeat

git bisect reset                 # done; back to original branch
```

### Automated

```bash
git bisect start HEAD v1.0
git bisect run ./test.sh         # auto-runs, exit 0=good, 1=bad, 125=skip
```

Finds bug in O(log n) commits.

## Submodules

A repo nested inside another. Tracks specific commit of the inner repo.

```bash
git submodule add https://github.com/org/lib lib
git submodule init               # after clone
git submodule update             # checkout pinned commit
git submodule update --init --recursive   # combined
git clone --recurse-submodules <url>
```

Pain points:
- Confusing for newcomers
- Detached HEAD inside submodule
- Branch tracking is manual
- Easy to commit "wrong" submodule SHA

## Subtrees (alternative to submodules)

```bash
git subtree add --prefix=lib https://github.com/org/lib main --squash
git subtree pull --prefix=lib https://github.com/org/lib main --squash
git subtree push --prefix=lib https://github.com/org/lib main
```

No special clone behavior — the subtree is just files in your repo.

## Git LFS (Large File Storage)

For binary files (images, videos, ML weights):
- File content stored on LFS server
- Pointers in Git history
- `git lfs track "*.psd"` adds to `.gitattributes`

```bash
git lfs install
git lfs track "*.bin"
git add .gitattributes
git add big.bin
git commit -m "add big.bin"
```

## Worktrees

Multiple working directories sharing one .git database.

```bash
git worktree add ../repo-feature feature/foo
cd ../repo-feature                # work on feature

git worktree list
git worktree remove ../repo-feature
git worktree prune
```

Use cases:
- Build one branch while working on another
- Avoid the dance of stashing + switching
- Run tests on multiple branches in parallel

## Other Useful

```bash
# Find a string in history
git log -S "needle" --all                 # commits adding/removing "needle"
git log -G "regex" --all                  # commits with diff matching regex

# Blame
git blame -L 10,20 file
git log -L 10,20:file                     # history of line range

# Find when a file was deleted
git log --all --full-history -- path/to/deleted

# Cleanup
git clean -fd                              # remove untracked files + dirs
git clean -fdx                             # also ignored

# Sparse checkout (huge monorepos)
git sparse-checkout init
git sparse-checkout set frontend/
```

## Interview Themes

- "How do you use git bisect?"
- "Submodules vs subtrees"
- "When would you use worktrees?"
- "Rebase -i: what would you use it for?"
- "Find when a bug was introduced — walk me through"
