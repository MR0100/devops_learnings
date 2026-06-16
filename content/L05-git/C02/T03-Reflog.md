# L05/C02/T03 — The Reflog (Your Safety Net)

## Learning Objectives

- Use reflog for recovery
- Understand reflog mechanics
- Recover "lost" commits

## What Reflog Is

Git records every change to refs locally. The reflog is a local history of where your branches and HEAD have been.

```bash
git reflog                          # for HEAD
git reflog show main                # for main branch
```

Sample:
```
abc1234 HEAD@{0}: commit: latest work
def5678 HEAD@{1}: reset: moving to HEAD~1
ghi9012 HEAD@{2}: rebase: my-feature
jkl3456 HEAD@{3}: checkout: moving from main to my-feature
```

## What's Tracked

Every operation that updates HEAD or a branch:
- commits
- checkouts
- rebases
- resets
- merges
- amends

## Reflog Syntax

`HEAD@{N}` — N entries ago
`HEAD@{1.day.ago}` — time-based
`main@{2}` — main 2 entries ago
`master@{yesterday}`

```bash
git show HEAD@{2}                   # what HEAD pointed to 2 actions ago
git reset --hard HEAD@{1}           # rewind to 1 action ago
git checkout HEAD@{2.hours.ago}     # checkout state from 2h ago
```

## Recover Lost Commits

Most common scenario: `git reset --hard HEAD~5` lost commits.

```bash
git reflog                          # find the SHA before reset
abc1234 HEAD@{1}: reset: moving to HEAD~5
def5678 HEAD@{2}: commit: important work    ← this!

git reset --hard def5678
```

## Recover Deleted Branch

```bash
git reflog | grep feature/foo
# Find SHA where branch was

git branch feature/foo <SHA>
```

If reflog expired, hard to recover.

## Reflog Expiry

By default:
- Reachable entries: 90 days
- Unreachable entries: 30 days

After expiry: `git gc` may delete the underlying objects.

```bash
git config gc.reflogExpire 90.days
git config gc.reflogExpireUnreachable 30.days
```

## Manual Expire

```bash
git reflog expire --expire=2.weeks.ago --all
git gc
```

## Specific Refs

```bash
git reflog show main
git reflog show feature/foo
git reflog show HEAD
```

## What Reflog Doesn't Cover

- Untracked file changes
- Working directory changes (no commit)
- Remote operations (reflog is local)

For uncommitted: no recovery if `git clean -fd` or shell `rm`.

## Push Reflog Entries Are Local

If you cloned a repo and made commits then deleted them, only YOUR machine has the reflog. Cloning doesn't bring reflog.

For team recovery: hope it's pushed somewhere, or look in someone's local reflog.

## Use Cases

### Undo amend
```bash
git commit --amend       # oops, wrong message
git reflog               # see previous commit
git reset --soft HEAD@{1}
# now staging area shows what was committed before amend
```

### Undo rebase
```bash
git rebase main          # had unexpected conflicts
git reset --hard ORIG_HEAD  # ORIG_HEAD is also set
# or
git reflog
git reset --hard HEAD@{N}
```

### Undo merge
```bash
git merge feature
# realize you don't want it merged
git reset --hard HEAD@{1}     # back before merge
```

### Recover stashed work
Stash entries shown:
```bash
git reflog show refs/stash
```

## Reflog vs git log

- `git log` shows committed history (ancestry)
- `git reflog` shows YOUR ACTIONS (branch movements)

```bash
git log              # commits via parent chain
git reflog           # what HEAD/refs pointed to over time
```

## Reflog Is Per Ref

```bash
git reflog show HEAD
git reflog show main
git reflog show stash
```

Each has its own.

## Stash via Reflog

If you `git stash pop` and lose changes:
```bash
git fsck --no-reflog | grep blob   # find dangling blobs
# Or check reflog
git reflog show refs/stash
```

Recovery possible if not yet GC'd.

## Auditing Local Activity

Useful for understanding "what did I do?":
```bash
git reflog --date=iso              # with timestamps
git reflog --date=relative
```

## Sample Recovery Script

```bash
# Find lost commit by message
git reflog | grep "important fix"
# def5678 HEAD@{42}: commit: important fix

git cherry-pick def5678            # apply to current branch
# or
git reset --hard def5678           # restore branch to that point
```

## Common Mistakes

- **Assuming reflog is forever**: 30/90 day expiry
- **Reflog is remote**: it's LOCAL only
- **Cleaning a repo without checking reflog**: may want unreachable

## Operations

```bash
# Save reflog as a list
git reflog --all > my-reflog.txt
```

Useful before risky operations.

## When NOT to Rely on Reflog

- After `git gc --prune=now --aggressive` (objects may be gone)
- After cloning fresh
- For shared/team recovery

## Best Practices

- Reach for the reflog *before* anything destructive — `git reset`, `git rebase`, `git commit --amend`, and force-pulls all leave recoverable entries here.
- Take a snapshot (`git reflog --all > reflog.txt` or a backup branch) before big rewrites, so you have an external record even if the reflog later expires.
- Recover by creating a new branch off the lost SHA (`git branch rescue <sha>`) rather than resetting in place, which preserves your current state while you verify.
- Know the expiry windows: reachable entries default to 90 days (`gc.reflogExpire`), unreachable to 30 (`gc.reflogExpireUnreachable`) — act promptly on lost work.
- Don't rely on the reflog for team or remote recovery; it is strictly local, so push important recovered commits somewhere durable immediately.

## Quick Refs

```bash
git reflog                            # HEAD's movement history
git reflog show <branch>              # one branch's reflog
git reflog --all                      # every ref's reflog

# Recovery recipes
git reset --hard HEAD@{1}             # undo last reset/rebase
git checkout -b rescue <sha>          # branch off a "lost" commit
git cherry-pick <sha>                 # replay a dropped commit
git branch <name> HEAD@{2}            # recover a deleted branch tip
```

`HEAD@{n}` = where HEAD was n moves ago. Default reflog retention: 90 days (reachable), 30 days (unreachable).

## Interview Prep

**Mid**: "Recover from `git reset --hard`."

**Senior**: "Where does reflog live?"

**Staff**: "Find an old commit by message in reflog."

## Next Topic

→ [T04 — Plumbing vs Porcelain Commands](T04-Plumbing-Porcelain.md)
