# L05/C03 — Branching & Merging

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Fast-Forward.md) | Fast-Forward vs Three-Way Merge | 1 hr |
| [T02](T02-Rebase-vs-Merge.md) | Rebase vs Merge (The Real Tradeoffs) | 1.5 hr |
| [T03](T03-Cherry-Pick-Revert-Reset.md) | Cherry-Pick, Revert, Reset | 1 hr |
| [T04](T04-Conflicts.md) | Resolving Conflicts at Scale | 1 hr |

## Fast-Forward Merge

```
Before:                          After git merge feature (fast-forward):
main: A-B-C                      main: A-B-C-D-E
            \                                    ↑
        feature: D-E                            main now points here
```

Both `main` and `feature` move to the same commit. No merge commit.

## Three-Way Merge (non-fast-forward)

```
Before:                          After git merge feature:
main:     A-B-C-F                 main: A-B-C-F-M
                \                              \  ↑
            feature: D-E                        D-E (M is merge commit)
```

M has two parents (F and E). History is preserved but "noisier".

## Rebase

```
Before:                          After git rebase main (on feature):
main:     A-B-C-F                 main: A-B-C-F
                \                                \
            feature: D-E                          D'-E'
```

Replays D, E as NEW commits D', E' on top of F. Old commits are abandoned (will be GC'd).

Linear history. **But**: rewrites history; never rebase published branches.

## Rebase vs Merge — The Real Tradeoffs

| | Merge | Rebase |
|---|---|---|
| History | Preserved, can be messy | Linear, clean |
| Conflicts | Once | Per-commit possibly |
| Time-machine accuracy | Yes | No (commits "moved") |
| Published branches | Safe | DANGEROUS — rewrites |
| PR workflow | Merge commit per PR | Squash-and-merge OR fast-forward |

### When to Rebase
- Local feature branches BEFORE pushing
- "I want a clean PR with no merge commits"
- Pulling: `git pull --rebase`

### When to Merge
- Long-running shared branches
- After PR is reviewed and ready

### Never
- Rebase commits already pushed and shared with others (without coordination)

## The Three Cleanups

### cherry-pick
Apply a specific commit from elsewhere.

```bash
git cherry-pick <sha>
git cherry-pick <sha1>..<sha2>           # range
git cherry-pick --no-commit <sha>        # apply without committing
```

Use cases: backport a fix to a release branch.

### revert
Create a NEW commit that undoes a previous one. History-preserving.

```bash
git revert <sha>
git revert -m 1 <merge-sha>              # revert a merge
```

Safe for public branches.

### reset
Move a branch ref backward. Can rewrite history.

```bash
git reset --soft HEAD~1     # uncommit; keep changes staged
git reset --mixed HEAD~1    # uncommit + unstage (default)
git reset --hard HEAD~1     # discard everything (DANGEROUS)
git reset --hard <sha>      # go to specific commit
```

| Mode | Index | Working Dir |
|---|---|---|
| --soft | unchanged | unchanged |
| --mixed (default) | reset | unchanged |
| --hard | reset | reset |

## Conflicts

A conflict occurs when both branches modified the same lines.

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> feature/foo
```

Resolution:
```bash
# Edit file, remove conflict markers, pick the right version
git add file              # mark resolved
git commit                # finish merge
# or for rebase:
git rebase --continue
```

Useful flags:
```bash
git merge --abort         # cancel a merge
git rebase --abort
git rebase --skip         # skip current commit during rebase

git status                # which files have conflicts
git diff --name-only --diff-filter=U  # only conflicted files
```

## Conflict-Reducing Strategies

```bash
git config --global rerere.enabled true   # reuse recorded resolutions
git config merge.tool meld                # GUI merge tool
git mergetool                              # invoke

git rebase --interactive HEAD~5            # squash before merging
```

## Strategy Options

```bash
# Theirs/ours strategies
git merge -X theirs branch        # prefer theirs on conflict
git merge -X ours branch          # prefer ours

# Octopus merge (rare)
git merge branch1 branch2 branch3
```

## At Scale: Trunk-Based + Short-Lived Branches

The DORA-correlated practice:
- Branches live < 24 hours
- Merge frequently to trunk
- Feature flags for unfinished features
- Less conflict surface area

## Interview Themes

- "Difference between merge and rebase"
- "When NEVER rebase"
- "Walk me through revert vs reset"
- "How do you resolve conflicts at PR scale?"
- "How would you backport a fix from main to release/v1.2?"
