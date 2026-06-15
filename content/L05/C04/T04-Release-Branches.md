# L05/C04/T04 — Release Branches & Hotfixes

## Learning Objectives

- Maintain release branches
- Backport hotfixes
- Coordinate multi-version support

## When You Need Release Branches

- Packaged software (mobile, desktop)
- Multiple versions supported simultaneously (1.x, 2.x)
- Slow release cycles
- Regulated industries

If you're a SaaS that deploys 10× per day: skip this. Trunk-based.

## Pattern

```
main:    A - B - C - D - E - F - G
              \
release/1.0:  v1.0.0 - v1.0.1 - v1.0.2
                ↑         ↑
              tag       hotfix
```

main is forward development. Release branches are stable per version.

## Creating a Release Branch

```bash
git switch main
git switch -c release/2.0
# Bug fixes, polish
git tag v2.0.0
```

## Backporting Hotfix

Bug found in production 1.0 (running release/1.x):

```bash
# Fix on main first
git switch main
# code fix; commit X
git push

# Cherry-pick to release branch
git switch release/1.x
git cherry-pick X
git tag v1.0.1
git push
git push --tags

# Build, release, deploy
```

## Why Cherry-Pick

- Keep release branch stable
- Don't pull main's other changes
- Selective backports

## Multiple Versions Support

```
main:        A - B - C - D - E
              \         \
release/1.x:  ...        ...
                          \
release/2.x:               ...
```

Hotfixes may need backport to multiple release branches.

```bash
git cherry-pick X    # to release/2.x
git cherry-pick X    # to release/1.x
```

(Cherry-pick same commit to each.)

## EOL (End of Life)

Each release branch eventually retires:
- Stop accepting backports
- Mark in changelog: "v1.x is EOL"
- Delete branch (or archive)

Communicate clearly to users.

## Trunk-Based + Releases

Some teams hybrid:
- Develop on main (trunk-based)
- Periodically: tag main as release
- For hotfix: branch from tag

```bash
git tag v2.0.0
# Later, bug in v2.0
git switch -c hotfix-v2.0.1 v2.0.0
git cherry-pick X     # fix from main
git tag v2.0.1
```

## Versioning + Branches

Semver:
- Major: incompatible (new release branch typically)
- Minor: new compatible features
- Patch: backward-compatible fixes (hotfix on release branch)

## Automated Backporting

Tools that auto-create backport PRs:
- **Mergify**: rule-based actions
- **GitHub Actions** with backport label
- **release-please**: handles release PRs

```yaml
# Label PR with "backport-1.x"; bot creates PR to release/1.x
```

## Backport Conflicts

When cherry-pick conflicts:
- Resolve manually
- Sometimes the fix needs to be different on older branch
- Document the resolution

## Tags as Anchors

For libraries: every release is a tag.
- Users pin to versions
- Bugs reported with version
- Fix; bump version; tag

```bash
git tag -a v1.2.3 -m "..."
git push --tags
```

## Hotfix Process Template

```markdown
1. Identify affected versions (1.x, 2.x)
2. Reproduce in main
3. Write fix on main
4. Test on main
5. Cherry-pick to each release branch
6. Test on release branch
7. Tag release branches (v1.x.Y, v2.x.Y)
8. Build + release artifacts
9. Update changelog
10. Communicate to users
```

## Time Cost

Maintaining N release branches: N× test/release work per fix.

Cost rises with old supported versions. Limit explicit support range.

## Modern Web SaaS: Skip This

For a website / API:
- Only one version live (the current)
- Hotfix is just a normal PR
- No release branches needed

## Tools

- **release-please**: automated release PRs
- **semantic-release**: based on conventional commits
- **GoReleaser**: for Go projects
- **CHANGELOG.md** + **GitHub Releases**: documentation

## Real Example

Linux kernel:
- main (Linus's tree)
- LTS branches (5.4, 5.10, 5.15, etc.) for years
- Stable maintainers backport fixes from main

Large project; many branches.

## Common Mistakes

- Fixing a bug only on the release branch and forgetting to land it on `main`, so the next release reintroduces the same bug (fix forward on `main` first, then backport).
- Backporting by re-typing the change instead of `git cherry-pick -x`, losing the link to the original commit and making audits and conflict resolution harder.
- Maintaining release branches forever; without a published EOL policy you accumulate an unbounded backport burden.
- Forgetting to tag the release commit, leaving no durable anchor for the version and breaking `git describe`.
- Cherry-picking a commit whose dependencies (earlier commits) aren't on the release branch, producing a broken or non-compiling backport.
- Spinning up release branches for a single continuously-deployed SaaS that has exactly one live version — pure overhead with no supported old versions to maintain.

## Best Practices

- Fix on `main` first, then cherry-pick the merged fix into each supported release branch with `-x` so the source SHA is recorded.
- Tag every release with an annotated, signed tag (`git tag -s vX.Y.Z`) and treat tags, not branches, as the immutable version anchors.
- Publish a clear support/EOL matrix (which versions get fixes, until when) so backport scope is bounded and known.
- Automate backporting where possible (label-driven bots that open backport PRs) and only fall back to manual cherry-pick when conflicts require judgment.
- Keep release branches change-frozen except for fixes — no new features — so they stay stable and easy to reason about.
- For pure SaaS with a single live version, skip release branches entirely and ship from the trunk.

## Quick Refs

```bash
# Create a release branch from a known-good point
git switch -c release/1.4 v1.4.0        # or from main at the freeze point

# Fix-forward on main, then backport
git switch main
# ...commit fix X...
git switch release/1.4
git cherry-pick -x <X>                   # -x records the original SHA
# resolve conflicts if cherry-pick stops, then:
git cherry-pick --continue

# Tag and ship
git tag -s v1.4.1 -m "Hotfix 1.4.1"
git push origin release/1.4 v1.4.1

# Backport a range
git cherry-pick -x <A>^..<B>             # ^ includes A

# Find which release branches already have a fix
git branch -r --contains <fix-sha>

# Describe current build relative to last tag
git describe --tags
```

| Step | Command |
|------|---------|
| Branch a release | `git switch -c release/X.Y <tag-or-main>` |
| Backport one fix | `git cherry-pick -x <sha>` |
| Tag the release | `git tag -s vX.Y.Z` |
| See where a fix landed | `git branch -r --contains <sha>` |

## Interview Prep

**Mid**: "Hotfix workflow."

**Senior**: "Backport strategy across multiple release branches."

**Staff**: "Design release branch policy."

## Next Chapter

→ [C05 — Advanced Git](../C05/README.md)
