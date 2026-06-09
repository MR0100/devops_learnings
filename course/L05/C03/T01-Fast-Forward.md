# L05/C03/T01 — Fast-Forward vs Three-Way Merge

## Learning Objectives

- Distinguish fast-forward from three-way merge
- Choose merge strategy
- Recognize when each happens

## Fast-Forward Merge

When target branch has no new commits since the source branched.

```
Before merge of feature into main:

main:    A - B - C
                  \
feature:           D - E

main is ancestor of feature (no diverged history).
```

`git merge feature` (from main):
```
main:    A - B - C - D - E  ← both refs move here
```

Just advances `main` pointer. No new commit created. "Fast-forward" because main "fast-forwards" to feature.

## Three-Way Merge

When BOTH branches have new commits.

```
main:    A - B - C - F   (F added after branching)
              \
feature:       D - E
```

Now there's no linear path. Git creates a merge commit M with two parents:
```
main:    A - B - C - F ---- M
              \             /
feature:       D - E -------
```

`M` contains the merged result + has parents F and E.

## Default Behavior

`git merge` defaults to:
- Fast-forward if possible
- Three-way merge otherwise

Force one or the other:
```bash
git merge --ff feature           # fast-forward if possible (default)
git merge --no-ff feature        # always create merge commit
git merge --ff-only feature      # only fast-forward; fail otherwise
```

## --no-ff (Always Merge Commit)

```bash
git merge --no-ff feature
```

Creates a merge commit even if FF would work. Used to:
- Preserve "this PR was merged" record
- Group commits of a feature
- Make rollback easier (revert one merge commit)

GitHub's "Create a merge commit" option does `--no-ff`.

## --ff-only (Strict)

```bash
git merge --ff-only origin/main
```

Refuses to merge if branches diverged. Useful for `git pull --ff-only` to detect surprise diverges.

## Three-Way Merge Algorithm

How does Git resolve conflicting changes?

1. Find COMMON ANCESTOR (merge base): C
2. Compare changes on each side since C:
   - main: F (changes from C → F)
   - feature: D, E (changes from C → E)
3. If different files: auto-merge
4. If same file, different lines: auto-merge
5. If same lines: conflict → human resolves

## Merge Base

```bash
git merge-base main feature      # find common ancestor
```

## When Conflicts

```
<<<<<<< HEAD
main version
=======
feature version
>>>>>>> feature
```

Resolve manually; `git add`; `git commit` (or `git merge --continue`).

## Squash Merge

Combine all of feature into ONE commit on main:
```bash
git merge --squash feature
git commit -m "Add feature"
```

No merge commit; feature commits collapsed. Loses feature history.

GitHub's "Squash and merge" does this.

## Octopus Merge

Merge >2 branches at once:
```bash
git merge feature1 feature2 feature3
```

Used rarely; auto-detection only.

## Recursive Merge (Default)

Git uses "recursive" or newer "ort" merge strategy by default:
- Handles renames
- Common-ancestor consensus

```bash
git merge -s recursive feature   # explicit
git merge -s ours feature         # accept ours; ignore feature changes
git merge -s theirs feature       # opposite (not built-in; use checkout)
```

## --strategy-option

Fine-tune:
```bash
git merge -X ours feature        # prefer "our" side on conflict
git merge -X theirs feature      # prefer "their" side
git merge -X ignore-all-space feature
```

## Aborting

```bash
git merge --abort                # cancel a merge in progress
```

Restores to before the merge.

## Merge Commit Message

Default:
```
Merge branch 'feature' into main
```

`git merge --edit` opens editor. `--no-edit` accepts default.

## Visualizing

```bash
git log --graph --oneline --all
git log --graph --oneline main feature
```

Shows branch + merge structure.

## When Fast-Forward Hides History

```
main:    A - B - C
                  \
feature:           D - E
```

After FF: log shows `A B C D E` linear. Did D and E come from feature? Lost.

`--no-ff` keeps merge commit; preserves info.

## Choosing

| Need | Strategy |
|---|---|
| Clean linear history | Rebase + FF only |
| Preserve PR boundaries | --no-ff |
| Quick personal work | FF (default) |
| Squash feature into single | --squash |

## Sample Workflow

```bash
# On feature branch
git pull --rebase origin main      # update with main's changes
# Resolve conflicts; finish rebase

# Push
git push --force-with-lease

# Open PR; merge via GitHub
# (GitHub does --no-ff if "Create merge commit" chosen)
```

## Interview Prep

**Junior**: "What's fast-forward?"

**Mid**: "When use --no-ff?"

**Senior**: "Explain three-way merge."

## Next Topic

→ [T02 — Rebase vs Merge (The Real Tradeoffs)](T02-Rebase-vs-Merge.md)
