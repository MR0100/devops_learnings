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

## Interview Prep

**Mid**: "Hotfix workflow."

**Senior**: "Backport strategy across multiple release branches."

**Staff**: "Design release branch policy."

## Next Chapter

→ [C05 — Advanced Git](../C05/README.md)
