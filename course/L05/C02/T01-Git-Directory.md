# L05/C02/T01 — The .git Directory Tour

## Learning Objectives

- Navigate `.git/` confidently
- Understand each file's purpose

## Layout

```
.git/
├── HEAD                    # current ref
├── config                  # local config
├── description             # cosmetic (gitweb)
├── index                   # staging area (binary)
├── objects/                # object database
│   ├── ab/cdef0123...      # loose objects
│   ├── info/
│   └── pack/
│       ├── pack-xxx.pack
│       └── pack-xxx.idx
├── refs/
│   ├── heads/              # local branches
│   ├── tags/
│   └── remotes/
├── packed-refs             # packed refs
├── hooks/                  # client hooks
├── info/exclude            # per-repo ignore (not committed)
├── logs/                   # reflog
└── (during ops) ORIG_HEAD, FETCH_HEAD, MERGE_HEAD
```

## HEAD

```bash
cat .git/HEAD
# ref: refs/heads/main
# or
# abc123...  (detached)
```

Points to current branch or commit.

## config

```bash
cat .git/config
# [core]
# 	repositoryformatversion = 0
# 	filemode = true
# 	bare = false
# 	logallrefupdates = true
# [remote "origin"]
# 	url = git@github.com:org/repo.git
# 	fetch = +refs/heads/*:refs/remotes/origin/*
# [branch "main"]
# 	remote = origin
# 	merge = refs/heads/main
```

Local repo config. Global at `~/.gitconfig`.

## index

Binary file: staging area state.

Plumbing access:
```bash
git ls-files --stage
# 100644 abc... 0 README.md
# 100755 def... 0 build.sh
```

Don't edit by hand.

## objects/

All data:
```bash
ls .git/objects/
# 00/ 01/ ... ff/ info/ pack/
```

Loose objects: one file per object, content-addressed.
Pack files: many objects bundled with delta compression.

```bash
git count-objects -v
```

## refs/

```bash
cat .git/refs/heads/main
# abc123...  (SHA of current commit)
```

Each ref = one file. Heavy repos pack them.

## packed-refs

After packing:
```bash
cat .git/packed-refs
# # pack-refs with: peeled fully-peeled sorted 
# abc123 refs/heads/old-branch
# def456 refs/tags/v0.9
```

## hooks/

Sample hooks. Make executable to enable.

```bash
ls .git/hooks/
# applypatch-msg.sample  pre-commit.sample  ... 
```

Enable: rename to remove `.sample`.

## logs/

Reflog data:
```bash
cat .git/logs/HEAD
# <SHA> <SHA> Author <email> <ts> <tz> action: comment
```

Used by `git reflog`.

## info/

```bash
cat .git/info/exclude
# Per-repo .gitignore, not committed
```

Useful for personal ignores not shared.

## Temporary State

During operations, Git creates:
- `MERGE_HEAD` — during merge in progress
- `CHERRY_PICK_HEAD`
- `REBASE_HEAD`, `rebase-merge/` dir
- `BISECT_LOG`, `BISECT_NAMES`

Cleared on completion or abort.

## Worktrees

Multiple worktrees share `.git/`:
```
main worktree: full .git/
secondary: small .git file pointing back
```

```bash
ls .git/worktrees/
# named-worktree/
```

## Bare Repos

For server / mirror; no working directory:
```bash
git clone --bare url repo.git
ls repo.git/                  # looks like .git/ contents
```

`bare = true` in config. No checkout, just objects + refs.

## Inspecting Live

```bash
git rev-parse --git-dir          # .git path
git rev-parse --show-toplevel    # repo root
git rev-parse --git-common-dir   # shared dir (for worktrees)
```

## Backups

The `.git/` directory IS the repo. Back it up to back up everything.

```bash
tar -czf repo-backup.tar.gz .git
```

## Common Operations

### Manual Edits (Don't, but...)
- Edit a ref: `echo "newSHA" > .git/refs/heads/main` (don't)
- Use proper commands instead

### Fix Corrupted Index
```bash
rm .git/index
git reset                     # rebuilds from HEAD
```

### View Pack
```bash
git verify-pack -v .git/objects/pack/pack-*.idx
```

## Common Mistakes

- Editing config by hand (use `git config`)
- Modifying refs files (use `git update-ref`)
- Deleting `.git/index` (wipes staging)
- Renaming `.git/` (breaks repo)

## Interview Prep

**Mid**: "What's in .git/objects?"

**Senior**: "What does .git/index hold?"

**Staff**: "Recover after .git/index corrupted."

## Next Topic

→ [T02 — Pack Files and Garbage Collection](T02-Pack-Files-GC.md)
