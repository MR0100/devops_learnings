# L05/C01/T01 — Working Directory, Staging, Repository

## Learning Objectives

- Understand Git's three trees
- Move files between states
- Use status effectively

## Three Trees

```
Working Directory (your files)
       ↓ git add
Staging Area (Index)
       ↓ git commit
Repository (.git/objects)
       ↑ git checkout / restore
       ↑ git reset
```

## Working Directory

Your actual files on disk. What you edit.

## Staging Area (Index)

Files prepared for the next commit. A "draft" of what the next snapshot will look like.

`.git/index` is a binary file holding this state.

## Repository

Committed history. `.git/` directory. Contains:
- All commits ever made
- All tree (directory) snapshots
- All blob (file content) objects
- Refs (branches, tags)

## Status Workflow

```bash
git status
# On branch main
# Changes to be committed:
#   modified: foo.txt              ← staged
# Changes not staged for commit:
#   modified: bar.txt              ← unstaged in working dir
# Untracked files:
#   newfile.txt                    ← not yet known to git
```

Three states:
- Untracked: new files
- Modified: changed since last commit
- Staged: ready for next commit

## Moving Between States

```bash
# Working → Staging
git add foo.txt
git add .                          # all changes in current dir
git add -p                         # interactive (hunk by hunk)

# Staging → Repository
git commit -m "message"
git commit                         # opens editor for longer message

# Repository → Working (overwrite local)
git checkout file.txt              # discard local changes
git restore file.txt               # modern (Git 2.23+)

# Staging → Working (unstage but keep changes)
git reset HEAD file.txt
git restore --staged file.txt      # modern

# Working → Discard
git restore file.txt
git clean -fd                      # remove untracked files
```

## Inspecting Differences

```bash
git diff                           # working vs staging
git diff --staged                  # staging vs last commit
git diff --cached                  # same as --staged
git diff HEAD                      # working vs last commit
git diff main feature              # between branches
git diff abc123..def456            # between commits
```

## Status Shortcuts

```bash
git status -s                      # short format
git status -b                      # show branch
```

Short:
```
 M foo.txt    ← modified, not staged
M  bar.txt    ← modified, staged
A  newfile    ← added, staged
?? untracked
```

Two columns: staging | working. Both spaces = no change.

## Add Patterns

```bash
git add .                          # current dir
git add -A                         # all (incl. deletes)
git add -u                         # only tracked files
git add *.py                       # glob
git add -p                         # interactive hunks
```

`-p` is excellent for cleaning up commits: stage related changes together.

## Commit

```bash
git commit -m "msg"                # simple
git commit                          # opens editor
git commit -a                       # auto-stage tracked changes
git commit --amend                  # modify last commit
git commit --amend --no-edit        # same; reuse message
git commit -m "fix" --signoff       # add Signed-off-by
```

## .gitignore

```
# Comment
*.log                                # all .log files anywhere
build/                               # any directory named build
/dist                                # only top-level dist
*.tmp                                # all .tmp
!important.tmp                       # except this one
**/cache                             # cache at any depth
```

Already-tracked files: `.gitignore` doesn't affect. Use `git rm --cached <file>`.

## Global Gitignore

```bash
git config --global core.excludesfile ~/.gitignore_global
```

For OS-specific stuff (.DS_Store, Thumbs.db, etc.).

## Common Patterns

### Commit Only Some Changes
```bash
git add -p file.txt                # interactive
# y/n per hunk
git commit -m "specific change"
git stash                           # set aside rest
```

### Unstage
```bash
git restore --staged file.txt
```

### Discard All Local Changes
```bash
git restore .
git clean -fd                       # remove untracked
```

**Dangerous**: lose all local work.

### See What Will Be Committed
```bash
git diff --staged
```

## Hands-On

```bash
mkdir test && cd test
git init
echo "hello" > file.txt
git status                          # untracked
git add file.txt
git status                          # staged
git commit -m "first"
git status                          # clean
echo "world" >> file.txt
git status                          # modified, not staged
```

## Common Mistakes

- Using `git reset --hard` to "clean up" without realizing it silently discards uncommitted working-directory changes with no reflog entry to recover them.
- Confusing `git checkout -- file` / `git restore file` (discards working-dir changes) with `git restore --staged file` (only unstages, keeps changes) — picking the wrong one loses edits.
- Assuming `git add .` captures everything; it skips files matched by `.gitignore` and (in older Git) deletions — leaving the index out of sync with the working tree.
- Committing then discovering a file was already tracked despite a later `.gitignore` entry — `.gitignore` only affects *untracked* files; you must `git rm --cached` to stop tracking.
- Running `git commit -a` expecting it to add brand-new untracked files; `-a` only stages modifications and deletions to already-tracked files.
- Reading `git diff` and thinking it shows what will be committed — it shows working-dir vs index; staged changes need `git diff --staged`.

## Best Practices

- Run `git status` and `git diff --staged` immediately before every commit to confirm exactly what is going in.
- Stage in logical hunks with `git add -p` so each commit is a single coherent change rather than a dump of unrelated edits.
- Keep a project `.gitignore` plus a global excludes file (`core.excludesFile`) for editor/OS cruft, so personal noise never reaches shared ignore rules.
- Prefer the modern `git restore` / `git restore --staged` verbs over overloaded `git checkout` to make intent unambiguous.
- Treat the staging area as a feature, not a hurdle: use it to review and curate, not just as a mandatory step before commit.

## Quick Refs

```bash
# State transitions (cheat sheet)
git add <f>                 # working  → index
git restore --staged <f>    # index    → working (unstage, keep edits)
git restore <f>             # discard working-dir edits (DESTRUCTIVE)
git commit                  # index    → repository
git checkout HEAD -- <f>    # repo     → working+index (overwrite local)

# Inspect
git diff                    # working vs index (unstaged)
git diff --staged           # index vs HEAD (what commit will record)
git diff HEAD               # working+index vs HEAD (everything)
git status -sb              # short status + branch line

# Curate
git add -p                  # stage selected hunks interactively
git reset -p                # unstage selected hunks
git stash -k                # stash only unstaged, keep staged for commit

# Stop tracking a file already committed (but keep on disk)
git rm --cached <f> && echo "<f>" >> .gitignore
```

| Goal | Command |
|------|---------|
| See what's staged | `git diff --staged` |
| Unstage but keep edits | `git restore --staged <f>` |
| Throw away edits | `git restore <f>` (or `git checkout -- <f>`) |
| Untrack but keep file | `git rm --cached <f>` |

## Interview Prep

**Junior**: "Three states of files."

**Mid**: "Difference: git diff vs git diff --staged."

**Senior**: "Modify last commit message."

## Next Topic

→ [T02 — Commits, Trees, Blobs (The Object Model)](T02-Object-Model.md)
