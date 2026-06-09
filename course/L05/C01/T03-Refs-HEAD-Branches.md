# L05/C01/T03 — Refs, HEAD, Branches, Tags

## Learning Objectives

- Understand refs as pointers
- Navigate HEAD detachment
- Manage branches and tags

## Refs

A ref is a file containing a SHA (or symbolic ref pointing to another ref).

```
.git/refs/heads/main        ← branch
.git/refs/tags/v1.0         ← tag
.git/refs/remotes/origin/main  ← remote-tracking
.git/HEAD                   ← current branch/commit
```

## HEAD

Where you are.

```bash
cat .git/HEAD
# ref: refs/heads/main          ← attached to branch
# or
# abc123...                     ← detached HEAD (raw SHA)
```

```bash
git symbolic-ref HEAD          # show what HEAD points to
git rev-parse HEAD             # actual commit SHA
git rev-parse main             # commit SHA of main
```

## Branches

A branch is just a pointer (a file with a SHA).

```bash
ls .git/refs/heads/
# main, develop, feature/foo

cat .git/refs/heads/main
# abc123...
```

Creating: O(1) operation.

```bash
git branch                          # list local
git branch -r                       # remote-tracking
git branch -a                       # all
git branch feature/foo              # create
git branch -d feature/foo           # delete (safe; merged only)
git branch -D feature/foo           # force delete
git branch -m old new               # rename
git branch -m new                   # rename current branch
```

## Switching Branches

```bash
git checkout main                   # legacy
git switch main                     # modern (Git 2.23+)
git switch -c feature/foo           # create + switch
git checkout -b feature/foo         # legacy create + switch
```

`switch` is clearer; `checkout` does too many things.

## Detached HEAD

When HEAD points directly to a commit, not a branch:
```bash
git checkout abc123               # detached HEAD at abc123
```

Useful for inspection. Bad for commits (orphaned).

To save work from detached HEAD:
```bash
git switch -c new-branch          # creates branch at current commit
```

## Tags

### Lightweight
```bash
git tag v1.0                       # at current HEAD
git tag v1.0 abc123                # at specific commit
```

Just a ref. No object.

### Annotated
```bash
git tag -a v1.0 -m "Release 1.0"
git tag -s v1.0 -m "..."           # signed (GPG)
```

Creates a tag object with metadata.

### Tag Operations
```bash
git tag                            # list
git tag -l "v1.*"                  # filter
git show v1.0                      # show tag + commit
git push origin v1.0               # push specific tag
git push --tags                    # push all tags
git tag -d v1.0                    # delete local
git push origin :refs/tags/v1.0    # delete remote
```

## Symbolic Refs

`HEAD` is symbolic when attached:
```
ref: refs/heads/main
```

`refs/remotes/origin/HEAD` symbolizes the default branch on remote.

## Reference Sequences

```bash
HEAD                  # current
HEAD^                 # parent
HEAD^^                # grandparent
HEAD~3                # 3 commits back
HEAD~                 # = HEAD^
HEAD^2                # 2nd parent (for merge commits)
main..HEAD            # commits in HEAD but not main
HEAD@{1.day.ago}      # time-relative (uses reflog)
HEAD@{2}              # 2 reflog entries ago
```

## Refs to Commits

```bash
git rev-parse main                 # show SHA
git rev-parse HEAD~3
git rev-parse v1.0
```

Useful for scripting.

## ORIG_HEAD, FETCH_HEAD, MERGE_HEAD

Special refs Git maintains:
- `ORIG_HEAD` — HEAD before last big op (merge, rebase)
- `FETCH_HEAD` — last fetched ref
- `MERGE_HEAD` — during a merge (the other branch)

Useful for recovery: `git reset --hard ORIG_HEAD` undoes a botched rebase.

## packed-refs

After many refs, Git packs them:
```bash
cat .git/packed-refs
# abc123 refs/heads/old-branch
# def456 refs/tags/v0.9
```

Single file; faster to read than 1000 individual files.

## Reflog (Recap)

Git tracks every change to HEAD and branch tips:
```bash
git reflog                         # for HEAD
git reflog show main               # for main
git reset --hard HEAD@{2}          # rewind to 2nd reflog entry
```

Local only. Default expiry: 90 days for reachable, 30 for unreachable.

## Branch Tracking

A local branch can track a remote branch:
```bash
git branch --set-upstream-to=origin/main main
git push -u origin feature/foo     # push + set upstream
```

When tracking: `git pull` knows where; `git status` shows ahead/behind.

## Show Current Branch

```bash
git branch --show-current          # modern
git symbolic-ref --short HEAD
```

## Multiple Refs Same Commit

Many refs can point to same commit:
```bash
git tag v1.0
git branch release-1.0
# Both v1.0 and release-1.0 point to current commit
```

Useful for marking specific states.

## Operations

```bash
# List branches sorted by recent activity
git for-each-ref --sort=-committerdate refs/heads/

# Which commit am I on?
git rev-parse HEAD

# Branch contains commit?
git branch --contains abc123
```

## Common Mistakes

- **Commits on detached HEAD lost**: forget to create branch
- **Force delete unmerged branch**: lose commits (recover via reflog)
- **Push branch with wrong name**: use careful `git push origin local:remote`

## Interview Prep

**Junior**: "What's a branch in Git?"

**Mid**: "Detached HEAD — what is it?"

**Senior**: "Recover commits from a deleted branch."

## Next Topic

→ [T04 — Remotes, fetch/pull/push](T04-Remotes.md)
