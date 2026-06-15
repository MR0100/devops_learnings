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

## Best Practices

- Always clone/pull submodule-using repos with `--recurse-submodules` (or set `git config submodule.recurse true`) so submodule trees aren't left empty.
- Pin submodules to a specific committed SHA and review bumps deliberately; the parent repo records the exact submodule commit, so updating means committing the new pointer.
- For subtrees, always use `--squash` on pull unless you genuinely want the upstream's full history merged into yours, which bloats the repo.
- Choose subtree when consumers must clone with zero extra steps (no submodule init); choose submodule when you need an explicit, auditable pin to an external repo's exact commit.
- Document the chosen approach in the README — submodule vs subtree workflows are different enough that contributors need to know which one they're in.
- Ensure CI runs `git submodule update --init --recursive` (or the subtree equivalent) so builds match what developers see.

## Quick Refs

```bash
# ---- Submodules ----
git submodule add <url> path/           # add + create .gitmodules
git clone --recurse-submodules <url>    # clone repo AND its submodules
git submodule update --init --recursive # populate after a plain clone
git submodule update --remote path/     # fetch upstream + move pointer
git -C path/ checkout <branch>          # work inside submodule (avoid detached HEAD)
git add path/ && git commit             # record new submodule SHA in parent
git config submodule.recurse true       # auto-recurse on pull/checkout

# ---- Subtrees ----
git subtree add    --prefix=lib <url> main --squash
git subtree pull   --prefix=lib <url> main --squash   # update from upstream
git subtree push   --prefix=lib <url> contrib         # push local changes back
```

| Concern | Submodule | Subtree |
|---------|-----------|---------|
| Clone steps | needs `--recurse-submodules` | none (just clone) |
| History | separate, pinned by SHA | merged into parent |
| Push upstream | direct, in submodule | `git subtree push` |
| Best when | explicit external pin | seamless for consumers |

## Interview Prep

**Mid**: "Submodule vs subtree."

**Senior**: "Why isn't submodule popular?"

**Staff**: "Monorepo vs many repos with subtrees."

## Next Topic

→ [T04 — Git LFS for Large Files](T04-Git-LFS.md)
