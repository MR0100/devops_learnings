# L05/C02/T02 — Pack Files and Garbage Collection

## Learning Objectives

- Understand pack files
- Run garbage collection
- Inspect pack contents

## Why Pack Files

Loose objects: one file per object. Lots of small files. Inefficient for filesystem and network.

Pack files bundle many objects into one large compressed file with **delta compression**: similar objects stored as deltas of a base.

```
Before packing:
.git/objects/ab/cdef...     (zlib-compressed file content)
.git/objects/12/3456...     (similar content)
.git/objects/78/9abc...     (...)
... thousands of files

After packing:
.git/objects/pack/pack-XXX.pack    (all objects, delta-compressed)
.git/objects/pack/pack-XXX.idx     (index for fast lookup)
```

## Run GC

```bash
git gc                          # standard
git gc --aggressive             # heavier delta search; slow
git gc --prune=now              # prune unreachable now
git gc --auto                   # only if "too many" loose
```

After `git gc`: loose objects → packs. Refs → packed-refs.

## Auto GC

Git runs `gc --auto` after operations when loose object count exceeds threshold:
```bash
git config gc.auto 6700         # default threshold
git config gc.auto 0            # disable
```

GitHub / GitLab handle GC server-side. Self-hosted needs cron or similar.

## Inspect Pack

```bash
git verify-pack -v .git/objects/pack/pack-*.idx | head
```

Shows per object:
- SHA
- type (commit, tree, blob, tag)
- size (uncompressed)
- packed size
- offset in pack
- "delta of" SHA (if delta)

## Delta Compression

```
Base object: full content
Delta object: "from base, change bytes X-Y to Z"
```

If a 1 MB file is mostly unchanged in 100 commits:
- Without delta: 100 MB
- With delta: 1 MB + ~tiny deltas

Massive space savings.

## Pack vs Loose

| | Loose | Pack |
|---|---|---|
| Files | 1 per object | 1 per pack |
| Compression | zlib per object | zlib + delta |
| Size | Larger | Much smaller |
| Speed | Fast individual | Fast lookup via index |

## Generations

Multiple pack files accumulate:
```bash
ls .git/objects/pack/
# pack-a.pack pack-b.pack pack-c.pack
```

`git gc --aggressive` consolidates into one optimal pack.

## Reachability

Objects "reachable" from a ref (branch, tag) are kept. Unreachable:
- Made by abandoned commits
- After rebase / amend / reset
- Cleaned by `git gc --prune=now`

But reflog keeps them reachable for default 90 days (reachable) / 30 days (unreachable).

## Truly Delete an Object

To wipe sensitive data:
```bash
# Rewrite history (BFG or git-filter-repo)
git filter-repo --invert-paths --path secrets.txt

# Force GC
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (if pushed)
git push --force --all
```

Even then: GitHub/GitLab may keep refs in their forks/copies.

## Pack File Limits

- Max pack size 4 GiB (theoretical 2 GiB practical)
- Repos with huge binary files: split or use Git LFS

## fsck

Check repo integrity:
```bash
git fsck
git fsck --full
git fsck --unreachable      # list unreachable objects
```

Shouldn't find anything bad on healthy repos.

## Repacking

Force re-pack:
```bash
git repack -ad             # all-into-one, delete-old
git repack -ad --depth=50 --window=250    # tune
```

`-d` deletes redundant packs.

## Common Issues

### Repo Too Large
```bash
du -sh .git
git count-objects -v
git verify-pack -v ... | sort -k 3 -n | tail   # largest objects
```

Find big files; consider LFS or filter-repo to remove.

### Repo Slow
- Many loose objects → run `git gc`
- Many small packs → `git repack -ad`

### Clone Slow
- Use `--depth=1` (shallow)
- Use `--filter=blob:none` (partial clone, GitHub supports)

## Pack Index Files

`pack-*.idx` provides O(log n) lookup by SHA. Without it: full scan.

```bash
git index-pack pack-XXX.pack   # rebuild index if missing
```

## Promisor / Partial Clone

Modern Git can fetch objects lazily:
```bash
git clone --filter=blob:none url    # no blobs
git clone --filter=tree:0 url       # no trees or blobs
# blobs/trees fetched on demand
```

GitHub supports. Used by VS Code's remote development.

## Operations

```bash
# Disk usage
du -sh .git

# Stats
git count-objects -v

# Periodic maintenance
git maintenance start              # daily/weekly auto-maintenance (Git 2.30+)
git maintenance run --task=gc
```

## Interview Prep

**Mid**: "Why does git gc?"

**Senior**: "Delta compression — how it works."

**Staff**: "Repo is 5 GB; trim it."

## Next Topic

→ [T03 — The Reflog (Your Safety Net)](T03-Reflog.md)
