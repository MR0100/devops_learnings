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

## Interview Prep

**Junior**: "Three states of files."

**Mid**: "Difference: git diff vs git diff --staged."

**Senior**: "Modify last commit message."

## Next Topic

→ [T02 — Commits, Trees, Blobs (The Object Model)](T02-Object-Model.md)
