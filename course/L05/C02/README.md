# L05/C02 — Git Internals

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Git-Directory.md) | The .git Directory Tour | 1 hr |
| [T02](T02-Pack-Files-GC.md) | Pack Files and Garbage Collection | 1 hr |
| [T03](T03-Reflog.md) | The Reflog (Your Safety Net) | 0.5 hr |
| [T04](T04-Plumbing-Porcelain.md) | Plumbing vs Porcelain Commands | 1 hr |

## .git Directory

```
.git/
├── HEAD                  # current ref (symbolic to a branch or commit)
├── config                # local config (remotes, branches, user)
├── description           # cosmetic (gitweb)
├── index                 # staging area (binary)
├── objects/              # the object database
│   ├── ab/
│   │   └── cdef0123...   # SHA-named loose objects
│   ├── info/
│   └── pack/             # packed objects (compressed)
│       ├── pack-XXX.pack
│       └── pack-XXX.idx
├── refs/                 # branches, tags
│   ├── heads/
│   ├── tags/
│   └── remotes/
├── packed-refs           # packed refs (when many)
├── hooks/                # client hooks (templates here)
├── info/
│   └── exclude           # per-repo ignore (not committed)
├── logs/                 # reflog
│   └── refs/
└── ORIG_HEAD, FETCH_HEAD, MERGE_HEAD  (temp during operations)
```

## Loose Objects vs Packs

- Loose: each object is a file under `.git/objects/AB/CDEF...` (zlib-compressed)
- Pack: many objects bundled with delta compression in `.git/objects/pack/`

`git gc` packs loose objects. Repos with many commits become huge without packing.

## Garbage Collection

```bash
git gc                          # standard
git gc --aggressive             # heavier delta search
git gc --prune=now              # prune unreachable objects now
git count-objects -v            # see object stats
git fsck                        # check repo integrity
```

GitHub/GitLab auto-pack frequently. Self-hosted may need cron.

## Reflog (Your Time Machine)

Every ref change is logged. You can recover almost anything that was ever in a commit.

```bash
git reflog                      # for HEAD
git reflog show feature/foo     # for a branch
git reset --hard HEAD@{2}       # go back 2 changes
git checkout HEAD@{1.day.ago}   # time-relative
```

### Recovering a "Deleted" Commit

```bash
# I just did:
git reset --hard HEAD~5    # OOPS — lost commits

# Recover via reflog:
git reflog                 # find SHA of pre-reset HEAD
git reset --hard <sha>
```

Reflog is **local** — not pushed. It also expires (90 days reachable, 30 unreachable, by default).

## Plumbing vs Porcelain

- **Porcelain**: high-level user commands (`git commit`, `git push`)
- **Plumbing**: low-level commands (`git hash-object`, `git update-ref`)

Plumbing is how you compose Git for scripts. Examples:

```bash
git hash-object -w file.txt        # store as blob, get SHA
git update-index --add --cacheinfo 100644 <SHA> path/to/file
git write-tree                     # snapshot index → tree object
git commit-tree <tree> -p <parent> -m "msg"
git update-ref refs/heads/main <commit-SHA>

# Inspect
git cat-file -p <SHA>              # contents
git cat-file -t <SHA>              # type
git ls-tree -r HEAD                # all files in commit
git rev-parse HEAD                 # SHA of HEAD
git rev-list HEAD --count          # number of commits
```

## Building a Commit by Hand (Plumbing)

```bash
# Make a blob
echo "hello" | git hash-object -w --stdin
# c8da...

# Stage it
git update-index --add --cacheinfo 100644 c8da... hello.txt

# Make a tree
git write-tree
# 5b8...

# Commit
git commit-tree 5b8... -m "first commit"
# abc...

# Point a ref
git update-ref refs/heads/main abc...
```

This is what `git commit` does under the hood.

## Pack File Internals

Packs use delta compression: similar objects are stored as deltas of a base.

```bash
git verify-pack -v .git/objects/pack/pack-*.idx | head
```

Shows: SHA, type, size, packed size, base SHA (for deltas).

## SHA-1 to SHA-256 Migration

Git is transitioning from SHA-1 to SHA-256 (collision-resistance). Not yet default but available:

```bash
git init --object-format=sha256
```

Most ecosystems still on SHA-1; migration is gradual.

## Interview Themes

- "Walk me through the Git object model"
- "How does Git compress storage?"
- "Recover a commit lost by reset --hard"
- "What's plumbing vs porcelain?"
- "Why does .git get so big?"
