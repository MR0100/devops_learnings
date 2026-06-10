# L15/C08/T01 — Semantic Versioning

## Learning Objectives

- Apply SemVer
- Manage breaking changes

## SemVer

```
MAJOR.MINOR.PATCH
v1.2.3
```

- **MAJOR**: breaking changes
- **MINOR**: backward-compatible features
- **PATCH**: backward-compatible bug fixes

## Rules

- v0.x.y: anything goes (pre-stable)
- v1.0.0: stable; SemVer kicks in
- Increment major: backward incompatible
- Increment minor: new features
- Increment patch: bug fixes

## Pre-Release

```
v1.0.0-alpha
v1.0.0-beta.1
v1.0.0-rc.2
```

For: unstable; tested before stable.

## Build Metadata

```
v1.0.0+abc123
v1.0.0+20251204
```

For: build identifiers; ignored for precedence.

## Examples

```
v1.0.0 → v1.0.1: bug fix
v1.0.1 → v1.1.0: new endpoint added
v1.1.0 → v2.0.0: removed endpoint
```

## In Code

```yaml
# package.json
"version": "1.2.3"

# Cargo.toml
version = "1.2.3"

# pyproject.toml
version = "1.2.3"
```

## Git Tags

```bash
git tag v1.2.3
git push --tags
```

For: release pointer.

## API Versioning

REST:
```
/api/v1/users
/api/v2/users   (breaking changes)
```

Multiple versions live during transition.

## Library Consumers

```json
"dependencies": {
  "lib": "^1.2.3"   # 1.2.3 - 1.999.999
  "lib": "~1.2.3"   # 1.2.3 - 1.2.999
  "lib": "1.2.3"    # exact
  "lib": ">=1.2.3 <2.0.0"
}
```

For: trust SemVer.

## When Major

Breaking:
- Removed function
- Changed function signature
- Renamed export
- Different return type
- Different exception behavior

For: SemVer-mandated.

## When Minor

Compatible:
- New function
- New optional param
- New endpoint
- Backward-compat changes

## When Patch

Compatible bug fix:
- Bug behavior corrected
- Doc updates (sometimes)
- Internal refactor (no API change)

## Caveats

### Implicit Contracts
Even non-API changes can break:
- Performance degradation
- Memory increase
- Side effects

For: be conservative on minor; explicit on major.

### Bug-As-Feature
Code relies on bug. Fix = breaks.

Major if widely depended on.

## Conventional Commits

Drive SemVer from commits:
```
feat: new endpoint              # minor
fix: bug in parser              # patch
feat!: removed deprecated API   # major (breaking)
docs: README update            # no version change
```

Tools:
- semantic-release
- changesets
- release-please

## semantic-release

```yaml
- run: npx semantic-release
```

Reads commits since last tag:
- Computes next version
- Generates changelog
- Tags + publishes

## Changelogs

Auto from commits:
```
## v1.2.0 (2026-01-15)
### Features
- Add user profile endpoint
### Bug Fixes
- Fix race condition in cache
```

For: user-facing.

## Versioning Strategies

### SemVer
Library, public API.

### CalVer (Calendar)
```
v2026.01.15
v25.10
```

For: continuous deploy; OS releases.

### Hashed
```
v1.0.0-abc123
sha-abc123
```

For: ephemeral.

### Hybrid
SemVer for releases; sha for builds.

## Major Bump Cost

- Consumer must update
- Migration docs
- Deprecation period

For: avoid often.

## Deprecation

```
v1.5: feature deprecated; works but warns
v2.0: feature removed
```

For: smooth transition.

```python
@deprecated("Use new_func instead")
def old_func(): ...
```

## Multi-Version

For libraries:
- Maintain v1.x (bug fixes)
- Develop v2.x (new features)

For: enterprise consumers.

## API Versioning

```
GET /api/v1/users   ← still maintained
GET /api/v2/users   ← new
```

Sunset v1 after announcement window.

## In CI

```yaml
- name: Get version
  id: version
  run: echo "version=$(cat VERSION)" >> $GITHUB_OUTPUT

- name: Build with version
  run: docker build --build-arg VERSION=${{ steps.version.outputs.version }} -t myapp:${{ steps.version.outputs.version }} .
```

## Image Tags

```
myapp:1.2.3
myapp:1.2
myapp:1
myapp:latest
```

Convenience aliases.

## Multi-Repo

Same SemVer:
```
service-a: v1.0
service-b: v1.0
```

Independent versions.

## Mono-Repo

Per package:
```
packages/
  ui/package.json (v1.0)
  api/package.json (v2.5)
```

Tools: Changesets, Lerna.

## Public Libraries

SemVer mandatory:
- Users depend on it
- Trust matters

For npm, PyPI, etc.: SemVer essential.

## Internal Services

CalVer often OK:
- Continuous deploy
- No external consumers
- Date = trace

## Best Practices

- v1.0.0 when stable API
- Conventional commits
- Auto-version (semantic-release)
- Changelog
- Deprecation cycle
- Multi-version support if libraries

## Common Mistakes

- v0.x forever (when actually stable)
- Breaking changes in minor (consumer pain)
- No changelog
- No deprecation warnings
- Skip major when breaking

## Pre-1.0 Anti-Pattern

```
v0.99.0
v0.99.1
...
```

After years: clearly stable. Bump to v1.0.0.

## Versioning of Schemas

### Database
- Migration numbers (1, 2, 3, ...) or timestamps
- Tool: Flyway, Alembic

### Protobuf
- Field tags stable
- Backward compat
- Major when breaking

### JSON / GraphQL
- Optional fields = compatible
- Breaking removal: major

## Quick Refs

```
MAJOR: breaking
MINOR: new features (compat)
PATCH: bug fixes (compat)

semantic-release: auto
Conventional Commits:
- feat:
- fix:
- feat!: (breaking)
- BREAKING CHANGE: in body
```

## Interview Prep

**Junior**: "What's SemVer."

**Mid**: "When major."

**Senior**: "API versioning."

**Staff**: "Versioning strategy."

## Next Topic

→ [T02 — Release Trains](T02-Release-Trains.md)
