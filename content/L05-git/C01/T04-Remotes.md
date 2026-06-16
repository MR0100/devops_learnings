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

## Common Mistakes

- Using bare `git push --force`, which overwrites the remote even if a teammate pushed in between; `--force-with-lease` refuses unless your view of the remote is current.
- Treating `git pull` as harmless — by default it merges (or rebases) and can create surprise merge commits or replay conflicts; people often want `git fetch` + a deliberate integrate.
- Forgetting that `git fetch` updates `origin/*` remote-tracking refs but does NOT move your local branch — `origin/main` advancing is not the same as `main` advancing.
- Pushing a local branch under a different remote name by accident; without a refspec, `git push origin feature` creates `origin/feature` even if you meant `main`.
- Running `git pull` with local uncommitted changes and hitting a "would be overwritten" abort, or worse, a messy partial merge — stash or commit first.
- Assuming a shallow clone (`--depth 1`) behaves like a full one; many history operations (blame across old commits, `git log` deep, some merges) fail until you `--unshallow`.

## Best Practices

- Default to `git fetch` then inspect with `git log --oneline @..@{u}` before integrating, so you see what's incoming instead of blindly merging.
- Configure `pull.ff only` (or `pull.rebase true` per team policy) so `git pull` fails loudly rather than silently creating merge commits.
- Always use `--force-with-lease` instead of `--force`; pair it with `--force-if-includes` on modern Git for even safer rewrites.
- Set upstream tracking with `git push -u` on first push so ahead/behind status and argument-free pull/push work correctly.
- For forks, add `upstream` as a second remote and sync via `git fetch upstream && git merge upstream/main` (or rebase), keeping `origin` as your fork.
- Authenticate with SSH or a credential helper rather than embedding tokens in remote URLs, which leak into `.git/config` and shell history.

## Quick Refs

```bash
# Inspect remotes and tracking
git remote -v                       # fetch/push URLs
git remote show origin              # tracked branches, ahead/behind, stale refs
git branch -vv                      # local branches + upstream + ahead/behind
git log --oneline @{u}..            # local commits not yet pushed
git log --oneline ..@{u}            # upstream commits not yet pulled

# Safe sync flow
git fetch origin
git log --oneline main..origin/main # preview incoming
git merge --ff-only origin/main     # or: git rebase origin/main

# Force safely
git push --force-with-lease origin <branch>

# Fork upstream sync
git remote add upstream <url>
git fetch upstream
git rebase upstream/main            # or merge

# Set tracking / push to a differently-named remote branch
git push -u origin HEAD
git push origin localname:remotename

# Prune deleted remote branches locally
git fetch --prune
```

| Want | Use |
|------|-----|
| See incoming, decide later | `git fetch` |
| Fetch + integrate now | `git pull` (configure ff/rebase!) |
| Overwrite remote safely | `git push --force-with-lease` |
| Remove stale `origin/*` refs | `git fetch --prune` |

## Interview Prep

**Junior**: "fetch vs pull."

**Mid**: "Safer force push."

**Senior**: "Sync fork with upstream."

**Staff**: "Set up multiple remotes for cross-platform mirroring."

## Next Chapter

→ [C02 — Git Internals](../C02/README.md)
