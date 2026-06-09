# L05/C02/T04 — Plumbing vs Porcelain Commands

## Learning Objectives

- Distinguish plumbing from porcelain
- Use plumbing for scripts
- Build complex automation

## The Distinction

- **Porcelain**: high-level, user-facing (`git commit`, `git push`)
- **Plumbing**: low-level building blocks (`git hash-object`, `git update-ref`)

Porcelain is built ON TOP of plumbing.

## Common Porcelain (you know these)

```bash
git add
git commit
git push
git pull
git fetch
git merge
git rebase
git checkout
git branch
git tag
git log
git show
git diff
```

## Common Plumbing

```bash
git hash-object            # compute SHA / store object
git cat-file               # inspect any object
git ls-tree                # list tree
git ls-files               # list index files
git update-index           # modify index
git write-tree             # write index → tree
git commit-tree            # tree → commit object
git update-ref             # set ref to commit
git symbolic-ref           # get/set symbolic ref
git rev-parse              # resolve refs to SHAs
git rev-list               # list commits
git for-each-ref           # iterate refs
git show-ref               # show refs
git diff-tree              # diff between trees
git diff-index             # diff index vs commit
```

## Build a Commit from Scratch

```bash
# Make a blob
echo "hello" | git hash-object -w --stdin
# c8da... (blob SHA)

# Add to index
git update-index --add --cacheinfo 100644 c8da... hello.txt

# Make tree from index
tree=$(git write-tree)

# Make commit
commit=$(echo "first" | git commit-tree $tree)

# Point a ref
git update-ref refs/heads/main $commit
```

That's what `git commit` does under the hood.

## Inspect Anything

```bash
git cat-file -t <SHA>          # type
git cat-file -p <SHA>          # pretty print
git cat-file -s <SHA>          # size

git ls-tree HEAD               # current root tree
git ls-tree -r HEAD            # recursive
git ls-tree -l HEAD            # with sizes
```

## Resolve Refs

```bash
git rev-parse HEAD             # commit SHA
git rev-parse main             # commit SHA of main
git rev-parse HEAD^{tree}      # tree SHA
git rev-parse v1.0^{commit}    # commit SHA from tag
git rev-parse @                # HEAD (shorthand)
git rev-parse @{upstream}      # upstream branch
git rev-parse @{push}          # where push would go
```

## Iterate Refs

```bash
git for-each-ref --format='%(refname:short) %(objectname:short)' refs/heads/
# main abc1234
# feature/foo def5678

git for-each-ref --sort=-committerdate --format='%(refname:short) %(committerdate:short)' refs/heads/
```

## Listing Commits

```bash
git rev-list HEAD              # all reachable from HEAD
git rev-list --count HEAD      # count
git rev-list main..HEAD        # in HEAD not main
git rev-list --since=1.week.ago HEAD
git rev-list --author='alice' HEAD
git rev-list -n 5 HEAD         # last 5
```

## Diff Plumbing

```bash
git diff-tree -p HEAD          # commit's changes
git diff-tree --no-commit-id -r --name-only HEAD
git diff-index --cached HEAD   # index vs HEAD
git diff-files                  # index vs working
```

## Scripting Examples

### Get author of HEAD
```bash
git rev-list --format='%an <%ae>' HEAD -n 1
# OR
git log -1 --format='%an'
```

### Count commits in branch
```bash
git rev-list --count main
git rev-list --count main..feature
```

### Files changed between branches
```bash
git diff-tree --name-only -r main feature
```

### Modified by author
```bash
git log --author='alice' --pretty=format:'%H' | head -10
```

### Hash of subtree
```bash
git rev-parse 'HEAD:src/foo'
```

## Build a Tag

```bash
sha=$(git rev-parse HEAD)
echo "object $sha
type commit
tag v1.0
tagger $(git config user.name) <$(git config user.email)> $(date +%s) +0000

Release 1.0" | git mktag
```

## Why Use Plumbing

For scripts:
- Stable output (porcelain may change format)
- Programmatic interfaces
- Composable

For tools:
- Build Git GUIs / web interfaces
- Implement custom workflows
- Integrate with CI

## When NOT to Use Plumbing

For everyday work: porcelain is fine. Plumbing is for scripts and tooling, not daily commits.

## Stable Output

Porcelain commands have user-friendly output that may change. Plumbing has stable, machine-parseable output.

```bash
git log --pretty=format:'%H %s'    # custom porcelain format
git rev-list --pretty=format:'%H' HEAD     # plumbing-style
```

## `--porcelain` Flag

Some porcelain commands have a `--porcelain` flag for stable output (for scripts):
```bash
git status --porcelain
# M file.txt
# ?? new.txt
```

vs human-readable default.

## Operations

```bash
# Show object size distribution
git rev-list --all --objects | git cat-file --batch-check --buffer | \
  awk '{print $3}' | sort -n | tail
```

## Interview Prep

**Mid**: "What's plumbing?"

**Senior**: "Build a commit by hand using plumbing."

**Staff**: "Why does Git have two layers (porcelain/plumbing)?"

## Next Chapter

→ [C03 — Branching & Merging](../C03/README.md)
