# L05/C05/T01 — Interactive Rebase, Squash, Fixup

## Learning Objectives

- Use interactive rebase to clean history
- Squash and fixup commits

## Basic Interactive Rebase

```bash
git rebase -i HEAD~5
```

Opens editor:
```
pick abc123 Add feature
pick def456 Fix typo in feature
pick ghi789 Add tests
pick jkl012 More work
pick mno345 Polish

# Commands:
# p, pick = use commit
# r, reword = change message
# e, edit = pause to amend
# s, squash = combine into prev (keep messages)
# f, fixup = combine; drop this message
# d, drop = remove commit
# x, exec = run shell command
```

Save + close → Git replays each line.

## Common Operations

### Reword
```
pick abc123 Add feature
reword def456 Fix typo in feature
```
Git pauses; you change message.

### Squash
```
pick abc123 Add feature
squash def456 Fix typo
squash ghi789 More fixes
```
Three commits → one. Combined message editor.

### Fixup
```
pick abc123 Add feature
fixup def456 Fix typo
```
Same as squash but discards def456's message. Use for "amend later" style.

### Drop
```
drop abc123 Add feature
```
Removes the commit.

### Reorder
Just change order of lines:
```
pick jkl012 Polish
pick abc123 Add feature
pick ghi789 Add tests
```

## --autosquash

If you make commits with `--fixup` flag:
```bash
git commit --fixup=abc123
git commit --fixup=abc123
git rebase -i --autosquash HEAD~10
```

Fixup commits auto-positioned for squashing. Saves manual editor work.

## --root

Rebase from beginning:
```bash
git rebase -i --root
```

For very early history rewrites.

## After Rebase: Force Push

```bash
git push --force-with-lease
```

If pushed before. Don't push to shared branches.

## Stop and Edit

```
edit abc123 Big commit
```

Git pauses at that commit:
```bash
# Stuff that takes setup
git reset HEAD^                    # uncommit but keep changes
# Make multiple smaller commits
git commit -m "part 1"
git commit -m "part 2"
git rebase --continue
```

Splits one commit into multiple.

## Useful Patterns

### Combine WIP into Coherent Story
Many small "wip" commits → polished sequence:
```bash
git rebase -i HEAD~20
# Squash trivial fixups; reword others
```

### Drop Bad Commit
Realized commit ghi789 was wrong:
```bash
git rebase -i HEAD~5
# drop ghi789
```

### Re-author
Wrong email on a commit:
```bash
git rebase -i HEAD~5
# edit the commit
git commit --amend --author="Real Name <real@example.com>"
git rebase --continue
```

### Sign Old Commits
GPG-sign retrospectively:
```bash
git rebase -i HEAD~5
# Mark each as 'edit'; at each pause:
git commit --amend --no-edit -S
git rebase --continue
```

## Conflicts During Rebase

```bash
# Conflict; resolve manually
git add resolved-files
git rebase --continue

# Or skip this commit
git rebase --skip

# Or abort
git rebase --abort
```

## Risks

- Rewriting public history breaks teammates
- Lose original commits (unless reflog still has them)
- Conflicts compound across many commits

## When To Interactive Rebase

- Before pushing: clean up local history
- After PR feedback: amend commits
- Before merging: squash to one commit

## When NOT

- After push to shared branch
- When unsure what state you'll end up in
- For very long history without practice

## Safety: Backup Branch

```bash
git branch backup-name        # current state
git rebase -i HEAD~10
# If something goes wrong:
git reset --hard backup-name
```

## Interview Prep

**Junior**: "What does interactive rebase do?"

**Mid**: "Squash multiple commits into one."

**Senior**: "Add a commit between two existing commits."

**Staff**: "Re-author historical commits without losing parents."

## Next Topic

→ [T02 — bisect for Finding Bugs](T02-Bisect.md)
