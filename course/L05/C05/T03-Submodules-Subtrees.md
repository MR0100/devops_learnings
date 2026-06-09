# L05/C05/T03 — Submodules vs Subtrees

## Learning Objectives

- Use submodules for nested repos
- Compare to subtrees
- Recognize tradeoffs

## Submodules

A repo nested inside another. Parent tracks specific commit of nested repo.

```bash
git submodule add https://github.com/org/lib lib
# Creates .gitmodules + lib/ (linked to other repo)
```

`.gitmodules`:
```
[submodule "lib"]
    path = lib
    url = https://github.com/org/lib
```

## Cloning with Submodules

```bash
git clone url repo
git submodule init               # configure
git submodule update             # checkout pinned commit

# Or combined:
git clone --recurse-submodules url repo
git submodule update --init --recursive
```

## Updating Submodule

```bash
cd lib
git pull origin main             # or specific tag
cd ..
git add lib                      # stage new SHA
git commit -m "Update lib"
```

Parent commit now references new SHA of lib.

## Submodule Pain Points

- Detached HEAD inside submodule (always at pinned SHA)
- "Forgot to update submodules" common
- Cloning forgets `--recurse-submodules`
- CI sometimes misses submodule changes
- Easy to commit wrong submodule state

## Subtrees

Subtree merges another repo's content into your repo's history.

```bash
git subtree add --prefix=lib https://github.com/org/lib main --squash
```

`lib/` now contains the other repo's files. No `.gitmodules`. Looks like normal directory.

## Updating Subtree

```bash
git subtree pull --prefix=lib https://github.com/org/lib main --squash
```

Pulls latest from upstream into your repo.

## Push Back

```bash
git subtree push --prefix=lib https://github.com/org/lib branch
```

Sends back to original repo.

## Comparison

| | Submodule | Subtree |
|---|---|---|
| Storage | Reference (link) | Files in main repo |
| Clone | Need init/update | Just clone |
| History | Separate | Merged into parent |
| Repo size | Smaller parent | Larger |
| Newcomer experience | Confusing | Normal |
| Cross-repo PRs | Awkward | Possible (with subtree push) |
| Version pinning | Explicit (SHA) | Less explicit |

## When Submodules

- Library used by multiple parent repos
- Need precise version pinning
- Team comfortable with submodule workflow
- Vendor lib unchanged frequently

## When Subtrees

- One-off integration
- Don't want submodule complexity
- Want history merged (good or bad)
- Newcomer-friendly

## Alternative: Monorepo

If you have many libs across your team:
- Merge into one big repo
- No submodules / subtrees needed
- Atomic changes across libs
- Requires good build tooling (Bazel, Nx, Turborepo)

## Alternative: Package Manager

For language libs:
- npm / Go modules / PyPI / Maven / Cargo
- Versioned releases
- Standard tooling
- Most common solution

Submodules used to be popular; package managers replaced for most use cases.

## When Each Today

| | Use |
|---|---|
| Submodule | OS-style dep (e.g., kernel modules); pinned vendor lib; rare |
| Subtree | One-off vendor; doesn't change much |
| Monorepo | Many internal libs; same team |
| Package manager | Standard libraries; default |

## Operations

### Submodules
```bash
git submodule status
git submodule foreach 'git pull origin main'
git submodule deinit -f lib    # remove
git rm lib
```

### Subtrees
Stored in normal Git; no special commands needed after add/pull.

## CI Considerations

### Submodules
```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive    # IMPORTANT
```

Otherwise: missing submodule content.

### Subtrees
Normal checkout works.

## Common Mistakes

- Forgot `--recurse-submodules` → empty submodule dirs
- Updated submodule but didn't commit parent SHA change
- CI missing submodule update
- Detached HEAD work lost inside submodule

## Operations

```bash
# Move submodule
git submodule deinit -f old/path
git rm old/path
git submodule add url new/path

# Show submodule URLs
git submodule status
git config -f .gitmodules --get-regexp url
```

## Interview Prep

**Mid**: "Submodule vs subtree."

**Senior**: "Why isn't submodule popular?"

**Staff**: "Monorepo vs many repos with subtrees."

## Next Topic

→ [T04 — Git LFS for Large Files](T04-Git-LFS.md)
