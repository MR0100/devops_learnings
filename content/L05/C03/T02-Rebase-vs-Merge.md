# L05/C03/T02 — Rebase vs Merge (The Real Tradeoffs)

## Learning Objectives

- Choose between rebase and merge
- Recognize "never rebase published" rule
- Combine techniques

## Rebase

Replays your commits ON TOP of another branch.

```
Before:
main:     A - B - C - F
              \
feature:       D - E

After git rebase main (on feature):
main:     A - B - C - F
                      \
feature:               D' - E'
```

D' and E' are NEW commits (different SHAs) with same content.

## Merge

Creates a merge commit joining two histories:
```
After git merge main (on feature) — non-FF:
main:     A - B - C - F
              \         \
feature:       D - E --- M
```

M has parents E and F.

## Side by Side

| | Rebase | Merge |
|---|---|---|
| History | Linear | Preserves branching |
| Commits | New (rewritten) | Original |
| Merge commit | No | Yes |
| Conflicts | Per commit possibly | Once at the end |
| Safe on shared branches | NO | Yes |
| Easier review | Yes (linear) | More context |

## When Rebase

- Local feature branch (not pushed)
- "Catch up" with main before opening PR
- Clean up commits before pushing
- Personal workflow

## When Merge

- Long-running shared branches
- Want to preserve "this branch worked on X"
- Multiple people on same branch
- Public/published branches

## The Golden Rule

**Never rebase commits already pushed and shared.**

Why: rebase rewrites commits (new SHAs). Others have the OLD SHAs. Pushing forces them to deal with the rewrite — conflicts, force pushes, lost work.

```bash
# Bad
git push origin feature
# Teammate pulls
git rebase main
git push --force      # teammate's clone now broken
```

## Rebase Workflow

```bash
# On feature, before pushing
git fetch origin
git rebase origin/main

# Resolve conflicts per commit
# Each conflict:
git add resolved_file
git rebase --continue

# Done; push
git push --force-with-lease    # safe-ish force
```

## Interactive Rebase

```bash
git rebase -i HEAD~5
```

Opens editor:
```
pick abc123 Add feature
pick def456 Fix typo
pick ghi789 Add tests
pick jkl012 More work
pick mno345 Polish

# Commands:
# p, pick = use commit
# r, reword = change message
# e, edit = pause to amend
# s, squash = combine into previous
# f, fixup = squash; discard message
# d, drop = remove
```

Re-order, drop, squash, edit. Powerful but rewrites.

## Conflict Resolution

### Rebase
- Conflict at each commit replay
- Resolve; `git add`; `git rebase --continue`
- May see same conflict multiple times if not rebasing properly

### Merge
- All conflicts at once
- Resolve in single commit (merge commit)

## --autosquash

Combined with `--fixup` commit type, autosquash auto-arranges:
```bash
# Commit a fixup pointing at earlier commit
git commit --fixup=abc123

# Rebase with autosquash
git rebase -i --autosquash HEAD~10
# Fixup commits auto-positioned to merge into target
```

## Sample: Rebase Workflow on Pull Request

1. Create feature branch from main
2. Make commits
3. Periodically: `git fetch && git rebase origin/main`
4. Resolve any conflicts
5. `git push --force-with-lease`
6. Open PR
7. Repeat 3-5 as main advances
8. PR merged (squash, rebase, or merge commit per team policy)

## Squash Rebase (Combine into One)

```bash
git rebase -i HEAD~5
# Mark all but first as 'squash' or 'fixup'
```

Result: 5 commits → 1 commit.

GitHub "Squash and merge" is equivalent.

## Rebase Onto

Move a branch onto a different base:
```bash
git rebase --onto new-base old-base feature
# Take feature's commits since old-base, replay onto new-base
```

Used in complex history surgery.

## Merge vs Rebase Religion

Both work. Don't get religious. Pick a team policy and follow it.

Common policies:
- **Trunk-based**: rebase + FF only (linear history)
- **GitHub Flow**: PR with "Create merge commit" (preserve PR boundaries)
- **Squash merge**: combine into one commit per PR

## My Recommendation

For most teams:
- **Local work**: rebase to clean up before pushing
- **PRs**: squash merge (one commit per PR; clean main)
- **Hotfixes**: cherry-pick or merge

## Common Mistakes

- Force-pushing to main
- Rebasing public branches
- Squashing too aggressively (lose useful intermediate states)
- Not squashing (PRs as 50-commit messes)

## Best Practices

- Follow the Golden Rule: only rebase commits that live solely on your machine; never rebase branches others have based work on.
- Rebase your feature onto the latest target before opening or updating a PR so reviewers see a clean, conflict-free diff and CI runs on the real merge state.
- After a rebase, push with `--force-with-lease`, never plain `--force`, so you don't clobber a teammate who pushed in the meantime.
- Use `git config pull.rebase true` (or `--rebase`) for keeping local feature branches current without polluting history with "Merge branch main" noise.
- Use `--autosquash` with `fixup!`/`squash!` commit prefixes to keep an in-progress branch tidy without manual reordering.
- Pick a team-wide merge policy (rebase-and-merge, squash-merge, or merge-commit) and enforce it in the host's branch protection so history stays consistent.

## Quick Refs

```bash
# Rebase basics
git rebase main                       # replay current branch onto main
git rebase -i HEAD~5                  # edit/reorder/squash last 5 commits
git rebase --onto newbase oldbase     # move a slice onto a different base
git rebase --autosquash main          # auto-position fixup!/squash! commits

# During a rebase
git rebase --continue                 # after resolving a conflict + git add
git rebase --skip                     # drop the current patch
git rebase --abort                    # restore pre-rebase state

# Merge alternative
git merge --no-ff feature             # explicit merge commit

# Safe publish after rewrite
git push --force-with-lease

# Recover a botched rebase
git reflog                            # find pre-rebase HEAD
git reset --hard HEAD@{N}             # or ORIG_HEAD
```

| Want | Use |
|------|-----|
| Linear, clean history | rebase |
| Preserve exact "what happened when" | merge |
| Combine a messy branch into one commit | `rebase -i` (squash) or squash-merge |
| Update local branch with main | `git pull --rebase` |

## Interview Prep

**Junior**: "Rebase vs merge."

**Mid**: "When NEVER rebase."

**Senior**: "Interactive rebase use cases."

**Staff**: "Team policy for handling PR merges."

## Next Topic

→ [T03 — Cherry-Pick, Revert, Reset](T03-Cherry-Pick-Revert-Reset.md)
