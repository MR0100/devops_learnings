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

## Interview Prep

**Junior**: "What does git bisect do?"

**Mid**: "Walk through finding a regression."

**Senior**: "Automate bisect with test script."

## Next Topic

→ [T03 — Submodules vs Subtrees](T03-Submodules-Subtrees.md)
