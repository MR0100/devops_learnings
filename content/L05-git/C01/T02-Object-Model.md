# L05/C01/T02 — Commits, Trees, Blobs (The Object Model)

## Learning Objectives

- Identify Git's 4 object types
- Read raw objects with plumbing
- Understand content addressing

## Four Object Types

1. **Blob** — file content
2. **Tree** — directory listing (filenames → blobs/trees)
3. **Commit** — pointer to tree + parents + metadata
4. **Tag** — annotated tag (pointer to commit + signature)

Each stored as a file under `.git/objects/`, addressed by SHA-1 (or SHA-256) of content.

## Content Addressing

```
SHA-1(content) → object ID
```

Same content → same ID. Different content → different ID (collision probability negligible).

```bash
echo "hello" | git hash-object --stdin
# ce01362
```

## Blob

Just file content. No metadata. No filename.

```bash
git cat-file -t ce01362            # blob
git cat-file -p ce01362            # hello
git cat-file -s ce01362            # 6 (size)
```

## Tree

Directory listing. Each entry: mode + type + SHA + name.

```bash
git cat-file -p HEAD^{tree}
# 100644 blob abc123 README.md
# 100755 blob def456 build.sh
# 040000 tree ghi789 src
```

Modes:
- `100644` regular file
- `100755` executable
- `120000` symlink
- `040000` directory (tree)
- `160000` submodule

## Commit

```bash
git cat-file -p HEAD
# tree abc123...
# parent def456...
# author Alice <alice@example.com> 1717920000 +0000
# committer Alice <alice@example.com> 1717920000 +0000
# 
# Commit message line 1
# 
# More detail
```

Contains:
- Pointer to one tree (root snapshot)
- Zero or more parent commits (zero for initial; two for merge commit)
- Author + timestamp
- Committer + timestamp
- Message

## Tag (Annotated)

```bash
git cat-file -p v1.0
# object abc123...
# type commit
# tag v1.0
# tagger Alice <alice@example.com> 1717920000 +0000
# 
# Release 1.0
```

Lightweight tags: just a ref pointing to a commit. No object.
Annotated tags: a tag object (signed if `-s`).

## Browse a Repo

```bash
# Get root tree of HEAD
git rev-parse HEAD                  # commit SHA
git cat-file -p HEAD                # commit content
git cat-file -p HEAD^{tree}         # root tree
git ls-tree HEAD                    # similar

# Navigate
git ls-tree HEAD path/to/dir
git cat-file -p HEAD:README.md      # blob for that path
```

## Storage

Initially as "loose objects" (one file per object):
```
.git/objects/ab/cdef0123456789abcdef0123456789abcdef
              └── first 2 chars of SHA = dir
                  rest = filename
```

Each file is zlib-compressed.

After `git gc`: packed into `.git/objects/pack/pack-*.pack`. Many objects in one file with delta compression.

## Same Content Deduplication

Two files with identical content → one blob. Two directories with identical content → one tree. Massive space saving.

## Tree Hashing Example

```bash
mkdir test && cd test && git init
echo "foo" > a.txt
echo "bar" > b.txt
git add .
git write-tree                      # produces tree SHA

git cat-file -p <tree-sha>          # shows the two blobs
```

## Build a Commit by Hand (Plumbing)

```bash
echo "hello" | git hash-object -w --stdin
# get blob SHA

# Build index entry
git update-index --add --cacheinfo 100644 <blob-sha> hello.txt

# Write tree
tree=$(git write-tree)

# Make commit
commit=$(git commit-tree $tree -m "first commit")

# Move branch
git update-ref refs/heads/main $commit
```

This is what `git commit` does internally.

## Pack Files

```bash
git gc                              # pack loose objects
git verify-pack -v .git/objects/pack/pack-*.idx | head
```

Delta compression: similar objects stored as deltas of a base. Massively reduces size for repos with many small changes.

## Object Lookup

```bash
git cat-file -p <SHA-or-prefix>
# Can use prefix as short as 4-7 chars if unique
```

## Counting Objects

```bash
git count-objects -v
# count: 1234       loose objects
# size: 567 KB      loose total
# in-pack: 89012    packed objects
# size-pack: 12 MB
```

## Garbage Collection

Unreachable objects (from no commit/ref) are eventually deleted:
```bash
git gc
git gc --prune=now                 # prune unreachable now
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Why This Matters

Understanding the object model:
- Makes Git internals clear
- Helps debug "lost" commits (they're still in objects/)
- Reflog recovers what you "lost"
- Pack files explain disk usage

## Common Mistakes

- Thinking a blob stores a filename — blobs store *only* content; the filename and mode live in the enclosing tree entry.
- Believing two commits with the same tree but different parent/author/timestamp can share a SHA — any byte change (including committer date) produces a new commit hash.
- Confusing a commit's SHA with its tree's SHA; `git cat-file -p HEAD` shows the commit pointing at a separate `tree <sha>`.
- Assuming `git gc` or a "lost" branch deletes objects immediately — unreachable objects survive in `objects/` until reflog/grace-period expiry, which is why recovery works.
- Treating short SHAs as permanent identifiers; a 7-char prefix that is unique today can become ambiguous as the repo grows, breaking scripts.
- Forgetting Git is content-addressed, not delta-addressed at the logical level: identical content anywhere in history deduplicates to one blob, so "copying a big file" costs nothing extra.

## Best Practices

- Use `git cat-file -p <sha>` and `git cat-file -t <sha>` to inspect objects directly when debugging — it removes guesswork about what Git actually stored.
- Reference commits by full 40-char SHA in scripts and automation; use short SHAs only interactively.
- Prefer annotated tags (`git tag -a`) for releases so you get a real tag object with tagger, date, and message rather than a lightweight ref.
- Reason about "where did my work go?" in terms of reachability: if an object exists, the reflog or `git fsck --lost-found` can usually surface it.
- When auditing repo bloat, remember the unit of storage is the blob — a large blob committed once stays in history forever until you rewrite it out.

## Quick Refs

```bash
# Identify and read any object
git cat-file -t <sha>            # type: blob | tree | commit | tag
git cat-file -p <sha>            # pretty-print contents
git cat-file -s <sha>            # size in bytes

# Hash content without storing / with storing
git hash-object <file>           # compute blob SHA
git hash-object -w <file>        # compute AND write to objects/

# Walk HEAD's tree
git cat-file -p HEAD             # see tree + parent + author lines
git ls-tree HEAD                 # list top-level tree entries
git ls-tree -r HEAD              # recurse into subtrees
git rev-parse HEAD^{tree}        # SHA of HEAD's root tree

# Build a commit entirely from plumbing
blob=$(git hash-object -w file.txt)
git update-index --add --cacheinfo 100644,$blob,file.txt
tree=$(git write-tree)
commit=$(echo "msg" | git commit-tree $tree -p HEAD)
git update-ref refs/heads/main $commit
```

| Object | Points to | Created by |
|--------|-----------|------------|
| blob | raw file content | `git add` / `hash-object -w` |
| tree | blobs + subtrees (names+modes) | `git write-tree` |
| commit | one tree + parent(s) + metadata | `commit-tree` / `git commit` |
| tag | one object + tag metadata | `git tag -a` |

## Interview Prep

**Mid**: "Four object types."

**Senior**: "Walk through what `git commit` does at the object level."

**Staff**: "Two files with same content — how is storage handled?"

## Next Topic

→ [T03 — Refs, HEAD, Branches, Tags](T03-Refs-HEAD-Branches.md)
