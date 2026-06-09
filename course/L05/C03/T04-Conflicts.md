# L05/C03/T04 — Resolving Conflicts at Scale

## Learning Objectives

- Resolve merge conflicts efficiently
- Use tools to help
- Reduce conflict frequency

## What Conflicts Look Like

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> feature
```

Git inserts conflict markers around disputed sections.

## Resolution Process

1. Edit file: remove markers, keep correct content
2. `git add <file>`
3. Continue: `git merge --continue` or `git rebase --continue`

## Useful Tools

### git status
```bash
git status
# Unmerged paths:
#   both modified: file.py
```

### List Conflicts Only
```bash
git diff --name-only --diff-filter=U
```

### Configure Merge Tool
```bash
git config --global merge.tool meld         # or vimdiff, kdiff3, etc.
git mergetool                                # invoke
```

GUI tools (Meld, KDiff3, Beyond Compare): three-pane view (BASE, OURS, THEIRS).

### VS Code
Built-in conflict markers + "Accept Current/Incoming/Both" buttons. Most modern editors do similar.

## Strategy Options

```bash
git merge -X theirs feature    # auto-prefer their side on conflict
git merge -X ours feature      # auto-prefer our side
git merge -X ignore-all-space feature   # ignore whitespace
```

Use cases:
- Reformatting branch: `-X theirs` if their formatting is canonical
- Code generation: `-X ignore-all-space` for whitespace-only conflicts

## Conflict Types

### Content
Same line changed differently. Manual review needed.

### Whitespace
Same line, different whitespace. `-X ignore-all-space` resolves.

### Delete-Modify
One side deleted, other modified. Git asks: keep or delete.

### Rename-Rename
Different renames of same file. Resolve manually.

### Both Added
Both branches added same file with different content. Need manual merge.

## Reducing Conflicts

### Smaller, More Frequent Merges
- Pull (or rebase) from main often
- Don't let feature branches age (< 24h ideal)

### Communication
- Coordinate big refactors
- "I'm working on file X" → others avoid

### Code Organization
- Smaller files
- Modular code (touch fewer files per change)
- Avoid all-in-one mega-files

### Auto-Formatters
- `gofmt`, `black`, `prettier`
- Consistent formatting → no whitespace conflicts
- Pre-commit hooks enforce

## rerere (Reuse Recorded Resolution)

Git can remember how you resolved a conflict and auto-apply same resolution:
```bash
git config rerere.enabled true
```

When same conflict happens again: auto-resolved. Especially useful for long rebases with recurring conflicts.

## Conflict Markers

Default:
```
<<<<<<< HEAD
ours
=======
theirs
>>>>>>> feature
```

With merge.conflictStyle = "diff3":
```
<<<<<<< HEAD
ours
||||||| merged common ancestors
original
=======
theirs
>>>>>>> feature
```

Shows the common ancestor — more context.

```bash
git config --global merge.conflictstyle diff3
```

## Abort

```bash
git merge --abort               # cancel merge
git rebase --abort              # cancel rebase
git cherry-pick --abort
```

Restores to pre-merge state.

## Continue After Resolve

```bash
git add <resolved-files>
git merge --continue            # or commit (auto-message)
git rebase --continue
```

## Conflict Markers Stuck in Code

If you forgot to remove markers and committed: bad. Find them:
```bash
git grep -n '^<<<<<<<\|^=======\|^>>>>>>>'
# Should be empty in normal commits
```

Add to pre-commit hook:
```bash
if git grep -n '^<<<<<<<' HEAD; then
    echo "conflict markers in code"
    exit 1
fi
```

## Practical Patterns

### Rebase Feature on Main
```bash
git fetch origin
git rebase origin/main
# Conflicts per commit:
# Resolve
# git add . && git rebase --continue
```

### Merge Main into Feature
```bash
git fetch origin
git merge origin/main
# Conflicts once:
# Resolve
# git add . && git commit
```

### Squash Then Resolve Once
```bash
git rebase -i HEAD~N
# Squash all commits
# Then rebase on main
git rebase origin/main
# One commit's worth of conflicts
```

## Large Rebases

For long-lived branch with many conflicts:
```bash
git rebase -i origin/main --autosquash
# rerere enabled? auto-resolves repeats
```

If overwhelming: consider merging instead. Linear history isn't worth excessive pain.

## Three-Way View

Some tools show OUR / THEIR / BASE side by side. BASE = common ancestor; shows what original looked like; helps decide intent.

## Conflicting Renames

```
File X renamed to Y on main
File X renamed to Z on feature
```

Resolution:
```bash
git rm Y                    # if Z wins
git mv X Y                  # restore + rename
```

Manual; can't auto-merge.

## Operations

```bash
# After conflict, see what's still conflicting
git status

# Show original (common ancestor) of conflicted file
git show :1:file.py

# Show "our" version (HEAD)
git show :2:file.py

# Show "their" version
git show :3:file.py

# Pick a side wholly
git checkout --ours file.py
git checkout --theirs file.py
```

## Interview Prep

**Junior**: "How resolve a merge conflict?"

**Mid**: "rerere — what is it?"

**Senior**: "Reduce conflict frequency on a team."

**Staff**: "Long-running feature branch with many conflicts — strategy."

## Next Chapter

→ [C04 — Workflows](../C04/README.md)
