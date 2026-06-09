# L05/C01/T04 — Remotes, fetch/pull/push

## Learning Objectives

- Manage multiple remotes
- Distinguish fetch, pull, push
- Set tracking branches

## Remote

A named URL pointing to another repo.

```bash
git remote -v
# origin  git@github.com:org/repo.git (fetch)
# origin  git@github.com:org/repo.git (push)

git remote add upstream git@github.com:other/repo.git
git remote set-url origin git@gitlab.com:org/repo.git
git remote rename origin github
git remote remove upstream
```

## fetch

Update remote-tracking branches; don't merge into local.

```bash
git fetch                     # current remote
git fetch origin              # specific remote
git fetch --all               # all remotes
git fetch --prune             # delete refs for deleted remote branches
```

After fetch, `origin/main` reflects current remote state. Local `main` unchanged.

## pull

`fetch` + `merge` (or `rebase`).

```bash
git pull
git pull origin main
git pull --rebase             # use rebase instead of merge
git pull --ff-only            # fast-forward only; fail if would merge
```

### Recommended Default
```bash
git config --global pull.rebase true     # always rebase
# or
git config --global pull.ff only         # fast-forward only
```

Avoids accidental merge commits.

## push

Send local commits to remote.

```bash
git push                              # current branch (if upstream set)
git push origin main                  # explicit
git push -u origin feature/foo        # set upstream
git push --force                      # DANGER
git push --force-with-lease           # safer force (checks remote)
git push --delete origin oldbranch    # delete remote branch
git push origin :oldbranch            # same (old syntax)
git push --tags                       # push tags
git push origin v1.0                  # push specific tag
```

## Force Push

Rewrites remote history. Dangerous on shared branches.

```bash
# Bad
git push --force                       # blindly overrides; may overwrite teammates' work

# Better
git push --force-with-lease             # only if remote matches your view
```

Never force-push to `main` or shared release branches.

## Tracking Branches

```bash
# Push current branch and set tracking
git push -u origin feature/foo

# Configure later
git branch --set-upstream-to=origin/feature/foo

# After: git pull / git push work without arguments
```

## Inspecting Remote State

```bash
git remote show origin                # detailed
git ls-remote origin                  # all refs on remote
git log origin/main                    # log of remote's main
git log main..origin/main              # commits on remote not in local
git log origin/main..main              # commits on local not on remote
```

## Multi-Remote Workflows

### Fork Pattern
```bash
git clone fork-url       # your fork
git remote add upstream original-url  # upstream

# Sync with upstream
git fetch upstream
git rebase upstream/main main

# Push to your fork
git push origin main
```

### Mirror
```bash
git remote add mirror git@gitlab.com:org/repo.git
git push --mirror mirror               # push all refs
```

Useful for keeping backups or migrating.

## Refspec (Advanced)

```bash
git push origin local-branch:remote-branch
```

Push `local-branch` to remote as `remote-branch` (different name).

```bash
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
```

Force-update remote-tracking refs.

## Shallow Clone

For large repos, save space:
```bash
git clone --depth=1 url           # only last commit
git clone --depth=10 url          # last 10 commits
git clone --filter=blob:none url  # no blobs initially (lazy fetch)
```

CI often uses `--depth=1` for speed.

## Sparse Checkout

For huge monorepos:
```bash
git sparse-checkout init --cone
git sparse-checkout set apps/frontend libs/shared
```

Only specified paths populate in working dir.

## Common Workflows

### Pull Latest
```bash
git fetch
git rebase origin/main             # or merge
```

### Update Feature Branch from Main
```bash
git fetch
git rebase origin/main feature/foo
```

### Sync Fork
```bash
git fetch upstream
git switch main
git rebase upstream/main
git push                           # push to your fork
```

### Delete Local Branches Already Merged
```bash
git fetch --prune
git branch --merged | grep -v "main\|^\*" | xargs git branch -d
```

## Common Errors

### "diverged"
Your branch and remote both have new commits.
```bash
git pull --rebase             # rebase yours on top
# or
git merge origin/main         # creates merge commit
```

### "non-fast-forward"
Trying to push but remote has different commits.
- Pull + rebase + push, OR
- `--force-with-lease` if intentional

### "no upstream"
Push without `-u`:
```bash
git push --set-upstream origin feature/foo
```

## Operations

```bash
# Show what would happen
git push --dry-run

# Show ahead/behind
git status                    # shows for current branch
git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads/
```

## Credential Storage

```bash
git config --global credential.helper cache          # in memory
git config --global credential.helper store          # plaintext on disk
git config --global credential.helper osxkeychain    # macOS
git config --global credential.helper manager        # Windows

# SSH key auth (preferred)
ssh-keygen -t ed25519
# add to GitHub/GitLab as SSH key
```

## Interview Prep

**Junior**: "fetch vs pull."

**Mid**: "Safer force push."

**Senior**: "Sync fork with upstream."

**Staff**: "Set up multiple remotes for cross-platform mirroring."

## Next Chapter

→ [C02 — Git Internals](../C02/README.md)
