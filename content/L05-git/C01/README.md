# L05/C01 — Git Fundamentals

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Working-Dir-Staging.md) | Working Directory, Staging, Repository | 1 hr |
| [T02](T02-Object-Model.md) | Commits, Trees, Blobs (The Object Model) | 1.5 hr |
| [T03](T03-Refs-HEAD-Branches.md) | Refs, HEAD, Branches, Tags | 1 hr |
| [T04](T04-Remotes.md) | Remotes, fetch/pull/push | 1 hr |

## The Three Trees

```
Working Directory   Staging (Index)   Repository (.git)
        │                    │              │
        │ git add ─────────► │              │
        │                    │ git commit ► │
        │ ◄────── git checkout ──────────── │
        │ ◄── git reset HEAD - │            │
```

- **Working dir**: files on disk
- **Staging (index)**: what will be committed next
- **Repo**: committed history (.git directory)

## Object Model

Git stores 4 object types, all content-addressed by SHA-1 (transitioning to SHA-256):

```
Commit
├── tree:    <SHA of root tree>
├── parent:  <SHA of parent commit>
├── author:  Name <email> timestamp
├── committer: Name <email> timestamp
└── message: "..."

Tree (directory)
├── 100644 blob <SHA>  README.md
├── 100755 blob <SHA>  build.sh
└── 040000 tree <SHA>  src/

Blob (file content, no metadata)
└── <bytes>

Tag (annotated)
├── object: <commit SHA>
├── tagger: ...
└── message: "v1.0 release"
```

Everything is content-addressed: same content → same SHA.

```bash
# Inspect any object
git cat-file -p <SHA>        # pretty
git cat-file -t <SHA>        # type
git ls-tree HEAD
git log --pretty=fuller
```

## Refs

A ref is just a file containing a SHA:

```
.git/
├── HEAD                       → ref: refs/heads/main
├── refs/
│   ├── heads/
│   │   ├── main              → abc123...
│   │   └── feature/foo       → def456...
│   ├── tags/
│   │   └── v1.0              → ghi789...
│   └── remotes/
│       └── origin/
│           └── main          → abc123...
├── packed-refs               (compressed refs)
└── ...
```

- `HEAD` — current branch (or detached commit SHA)
- `refs/heads/*` — local branches
- `refs/tags/*` — tags
- `refs/remotes/<remote>/*` — remote-tracking branches

## Branches Are Cheap

A branch is just a pointer (40-byte file). Creating one is O(1):

```bash
git branch feature/foo            # create
git checkout feature/foo          # switch
git checkout -b feature/foo       # both
git switch feature/foo            # modern equivalent
git switch -c feature/foo         # create + switch
```

## HEAD Reality

```bash
git symbolic-ref HEAD     # what does HEAD point to (e.g., refs/heads/main)
cat .git/HEAD             # same info
git rev-parse HEAD        # SHA of current commit
```

Detached HEAD = HEAD points directly to a commit, not a branch.

## Remotes

A remote is a named URL pointing to another repo.

```bash
git remote -v
git remote add origin git@github.com:org/repo.git
git remote set-url origin git@gitlab.com:org/repo.git

# Fetch updates remote-tracking branches (refs/remotes/origin/*)
git fetch origin

# Pull = fetch + merge (or fetch + rebase if configured)
git pull origin main
git pull --rebase origin main

# Push
git push origin main
git push -u origin feature/foo    # set upstream
git push --force-with-lease       # safer force push
git push --delete origin oldbranch
```

### Tracking Branches

`feature/foo → origin/feature/foo` means:
- `git pull` fetches from origin/feature/foo and merges into feature/foo
- `git push` pushes feature/foo to origin/feature/foo

Set up: `git push -u origin feature/foo` or `git branch --set-upstream-to=origin/feature/foo`.

## .gitignore

```
# Patterns relative to repo root (unless leading /)
*.log              # all .log
build/             # directory anywhere
/build/            # only root-level build/
!important.log     # negation
**/tmp/            # tmp dirs at any depth
```

Already-tracked files aren't affected. Use `git rm --cached <file>` to untrack.

## Common Daily Commands

```bash
git status                       # what's changed
git diff                         # unstaged changes
git diff --staged                # staged
git log --oneline -20            # recent
git log --graph --oneline --all  # branches visualized
git show HEAD                    # latest commit detail
git stash                        # save changes temporarily
git stash pop                    # restore
git restore <file>               # discard unstaged changes
git restore --staged <file>      # unstage
git commit --amend               # modify last commit
git commit --amend --no-edit     # add staged to last commit without changing message
```

## Interview Themes

- "Explain the three trees of Git"
- "What does a commit object contain?"
- "Difference between merge and rebase" (next chapter)
- "What is a detached HEAD?"
- "How would you discard local changes safely?"
