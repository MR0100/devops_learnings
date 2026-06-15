# L05/C05/T02 — bisect for Finding Bugs

## Learning Objectives

- Use git bisect to find regression commits
- Automate bisect with a test script

## What bisect Does

Binary searches commit history for the one that introduced a bug.

O(log n): 1000 commits → 10 tests.

## Basic Usage

```bash
git bisect start
git bisect bad HEAD            # current state has the bug
git bisect good v1.0           # this was working

# Git checks out midpoint
# Test:
./run-tests.sh
# If broken:
git bisect bad
# If working:
git bisect good

# Git narrows further; repeat
# Eventually:
# "abc123 is the first bad commit"

git bisect reset               # done; return to original
```

## Automated Bisect

If you have a test script that exits 0 (good) or 1 (bad):

```bash
git bisect start HEAD v1.0
git bisect run ./test.sh
```

Git runs script at each midpoint. Done in minutes.

## Skip

If a commit can't be tested (build broken, etc.):
```bash
git bisect skip
```

Git tries nearby commits.

## Reset

When done:
```bash
git bisect reset                  # back to original HEAD
git bisect reset HEAD~5           # to specific commit
```

## Custom Terms

Default: good/bad. Customize:
```bash
git bisect start --term-old=working --term-new=broken
```

Useful for non-bug regressions (e.g., performance).

## Test Script

```bash
#!/bin/bash
# test.sh — exit 0 if good; 1 if bad; 125 to skip

cd /path/to/build
make || exit 125          # build broken; skip
./test || exit 1          # test fail = bad
exit 0                    # all good
```

Exit 125 = can't test (skip).
Exit 0 = good.
Exit 1-124 = bad.

## Real Example

```bash
git bisect start
git bisect bad                 # current state broken
git bisect good HEAD~50        # 50 commits ago was fine
git bisect run ./test-perf.sh

# Output:
# ...
# 7 steps remaining
# abc123 is the first bad commit
# commit abc123
# Author: ...
# Date:   ...
#
#     Refactor query builder
```

Now you know which commit and can review/revert.

## What If the Range Is Wrong

If "good" commit also fails: maybe bug always existed (different cause). Widen range.

If "bad" commit doesn't actually have the bug: re-investigate.

## Bisect Multiple Bugs

```bash
git bisect old/new
git bisect terms                 # show current terms
```

## Bisect Reflog

While bisecting, history changes:
```bash
git bisect log                   # see what's tested
git bisect replay log.txt        # replay from log
```

For sharing or resuming.

## Visualize

```bash
git bisect visualize             # gitk with bisect highlights
```

## Bisect with State Mutations

If tests change state (DB, files), each iteration needs fresh state:
```bash
#!/bin/bash
# test.sh
reset_state
make && ./test
```

## Real Use Cases

- Performance regression in last 100 commits
- Feature stopped working
- Test suite broken
- Browser test regression

## Bisect with Patch

If you find the bad commit and want to revert just that:
```bash
git revert abc123                # creates revert commit
```

Or rewrite history (carefully):
```bash
git rebase -i abc123^
# drop abc123
```

## Common Mistakes

- Marking the endpoints backwards (`good` on the broken commit, `bad` on the working one); bisect then converges on nonsense — the "bad" must be where the bug exists.
- Picking a `good` commit that's too recent (already contains the bug) so the true first-bad commit is outside the search window and bisect never finds it.
- Forgetting `git bisect reset` when done, leaving HEAD detached on a midpoint commit and confusing later work.
- Writing a `git bisect run` script that exits non-zero for build/setup failures, which bisect interprets as "bad" — use exit code 125 to mark a commit unskippable/untestable.
- Ignoring flaky tests: a non-deterministic test makes bisect mislabel commits and point at the wrong culprit; stabilize or isolate the signal first.
- Not cleaning build artifacts or untracked state between steps, so a stale binary makes a good commit look bad (or vice versa).

## Best Practices

- Automate with `git bisect run <script>`; a script returning 0 (good), 1-124 (bad), or 125 (skip) turns a 20-step hunt into one command.
- Pick the widest reliable `good`/`bad` bounds you're confident about — bisect is O(log n), so a large but correct range is cheap.
- Make the test script deterministic and self-contained: rebuild from scratch, reset mutable state, and check the exact symptom, not a proxy.
- Use `git bisect skip` (or exit 125) for commits that can't be tested (won't build, irrelevant) rather than guessing good/bad.
- Save a log with `git bisect log` so you can `git bisect replay` after a mistake instead of restarting the whole session.
- Always end with `git bisect reset` to return to your original branch.

## Quick Refs

```bash
git bisect start                 # begin a session
git bisect bad                   # current commit is broken
git bisect good <sha>            # this older commit worked
# git checks out the midpoint; test, then:
git bisect good                  # this one is fine
git bisect bad                   # this one is broken
git bisect skip                  # can't test this commit
git bisect reset                 # end, return to original HEAD

# Fully automated:
git bisect start HEAD <good-sha>
git bisect run ./test.sh         # script exits 0=good, 1-124=bad, 125=skip
```

It's a binary search: ~log2(N) steps to pin the first bad commit across N commits.

## Interview Prep

**Junior**: "What does git bisect do?"

**Mid**: "Walk through finding a regression."

**Senior**: "Automate bisect with test script."

## Next Topic

→ [T03 — Submodules vs Subtrees](T03-Submodules-Subtrees.md)
