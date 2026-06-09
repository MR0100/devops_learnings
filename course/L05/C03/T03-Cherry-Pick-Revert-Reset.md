# L05/C03/T03 — Cherry-Pick, Revert, Reset

## Learning Objectives

- Apply specific commits with cherry-pick
- Safely undo with revert
- Use reset modes correctly

## cherry-pick

Apply a specific commit to current branch.

```bash
git cherry-pick abc123                 # one commit
git cherry-pick abc123 def456          # multiple
git cherry-pick abc123..def456         # range (exclusive of abc)
git cherry-pick abc123^..def456        # range (inclusive)
git cherry-pick --no-commit abc123     # apply without committing
git cherry-pick -e abc123              # edit message
git cherry-pick -x abc123              # add "(cherry picked from commit ...)" note
```

### Use Case
Backport a fix from main to a release branch:
```bash
git switch release-1.0
git cherry-pick abc123      # the fix
git push
```

### Conflicts
If cherry-pick conflicts:
```bash
git status                  # see conflicts
# Resolve
git add resolved_file
git cherry-pick --continue
# or
git cherry-pick --abort
```

## revert

Create a NEW commit that undoes a previous one. Preserves history.

```bash
git revert abc123
# Creates commit "Revert <original message>"
# with the inverse changes
```

Safe for public/published branches (doesn't rewrite history).

### Revert Merge Commit
Merge commits have multiple parents; specify "mainline":
```bash
git revert -m 1 <merge-sha>
# -m 1 = keep changes from first parent
```

### Multiple Reverts
```bash
git revert abc..def
git revert --no-commit abc..def    # all in one
git commit -m "Revert several commits"
```

## reset

Move a branch ref backward (or forward). Can rewrite history.

### Three Modes

```bash
git reset --soft HEAD~1     # uncommit; KEEP changes staged
git reset --mixed HEAD~1    # uncommit + UNSTAGE (default)
git reset --hard HEAD~1     # uncommit + LOSE all changes
```

| Mode | Index | Working Dir |
|---|---|---|
| --soft | unchanged | unchanged |
| --mixed | reset to target | unchanged |
| --hard | reset | reset (DANGEROUS) |

### Use Cases

#### Soft Reset (Recommit)
```bash
git commit -m "wrong"
git reset --soft HEAD~1     # uncommit, files still staged
# Make changes
git commit -m "correct"
```

#### Mixed (Unstage)
```bash
git add wrong_file.py
git reset HEAD wrong_file.py    # unstage
# or
git restore --staged wrong_file.py  # modern equivalent
```

#### Hard (Wipe)
```bash
git reset --hard HEAD       # discard ALL local changes (DANGER)
git reset --hard origin/main  # match remote exactly
```

DANGER: hard reset loses uncommitted work.

## Reset vs Revert

| | Reset | Revert |
|---|---|---|
| Moves history | Backwards | Forward (adds new) |
| Preserves history | No | Yes |
| Safe on public | NO | YES |
| Use | Local cleanup | Undo public commits |

## Recovery

Lost commits from reset? `git reflog`:
```bash
git reflog
# def5678 HEAD@{0}: reset: moving to HEAD~3
# abc1234 HEAD@{1}: commit: lost work

git reset --hard abc1234
```

## Patterns

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Undo Several Commits, Recommit
```bash
git reset --soft HEAD~3      # uncommit 3
git commit -m "consolidated"  # one commit
```

### Match Remote
```bash
git fetch
git reset --hard origin/main
```

### Recover File from Earlier Commit
```bash
git checkout abc123 -- path/to/file
# or
git restore --source=abc123 path/to/file
```

## --hard vs Stash

Sometimes you want to put work aside, not lose it:
```bash
git stash                  # save work; clean working dir
git stash pop              # restore
git stash list             # see saved
```

Safer than `git reset --hard`.

## Reverting Merge Commit (Tricky)

```bash
git revert -m 1 <merge-sha>
# Creates commit undoing the merged changes
```

Beware: re-merging same feature later won't bring back the reverted changes. You may need to revert the revert first:
```bash
git revert <revert-sha>     # undo the undo
git merge feature           # now merge again
```

## Reset Author / Date

```bash
git commit --amend --reset-author    # fix author of last commit
git commit --amend --date="2026-01-01"  # change date
```

## Sample Patterns

### Reset Branch to Remote
```bash
git fetch origin
git switch main
git reset --hard origin/main
```

For when local main diverged from remote in bad way.

### Discard Working Changes (Specific File)
```bash
git checkout HEAD -- file.txt
# or modern
git restore file.txt
```

### Discard ALL Working Changes
```bash
git checkout .
# or
git restore .
git clean -fd        # also remove untracked
```

## When to Cherry-Pick vs Merge

- **Cherry-pick**: specific commits between branches
- **Merge**: all of a branch's commits

Cherry-pick is useful for:
- Backporting fixes
- Picking a feature out of an unmerged branch
- Reorganizing history

## Common Mistakes

- **Force pushing after `git reset` on published branches**: teammates' work lost
- **Hard reset losing work**: use stash first
- **Cherry-picking creates duplicates**: when later merged, may conflict
- **Revert without `-m`** on merge commit: error

## Interview Prep

**Junior**: "Undo last commit."

**Mid**: "Reset modes (soft/mixed/hard)."

**Senior**: "Cherry-pick — when?"

**Staff**: "Revert merge commit and re-merge later."

## Next Topic

→ [T04 — Resolving Conflicts at Scale](T04-Conflicts.md)
