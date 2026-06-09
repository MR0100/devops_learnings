# L15/C08 — Release Engineering

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-SemVer.md) | Semantic Versioning | 0.5 hr |
| [T02](T02-Release-Trains.md) | Release Trains | 0.5 hr |
| [T03](T03-Hotfix.md) | Hotfix Workflows | 0.5 hr |

## Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  │     │     └── Backward-compatible bug fixes
  │     └──────── Backward-compatible new functionality
  └────────────── Breaking changes
```

Examples:
- `1.2.3 → 1.2.4`: bug fix
- `1.2.3 → 1.3.0`: new feature, compatible
- `1.2.3 → 2.0.0`: breaking change

Pre-release: `1.0.0-alpha`, `1.0.0-beta.1`, `1.0.0-rc.1`.

Build metadata: `1.0.0+sha.abc123`.

### Why It Matters
- Communicates impact of upgrade
- Dependency managers can solve constraints (`^1.2.3`, `~1.2.3`)
- API consumers know what to expect

### When to Bump

| Change | Bump |
|---|---|
| Added feature, didn't break | MINOR |
| Bug fix, no API change | PATCH |
| Removed/changed a public API | MAJOR |
| Added optional config field | MINOR |
| Changed default behavior | MAJOR (debatable) |
| Internal refactor (no API change) | PATCH or none |

## Automated SemVer via Conventional Commits

```
feat(api): add new endpoint           → MINOR bump
fix(api): handle null in foo          → PATCH bump
feat(api)!: rename old endpoint       → MAJOR bump (! = breaking)
feat(api): rename old endpoint

BREAKING CHANGE: old endpoint removed  → MAJOR bump
```

Tools:
- **semantic-release** (Node)
- **release-please** (Google, language-agnostic)
- **goreleaser** (Go)

These read commit history, infer version, generate changelog, tag, and publish.

## Release Trains

Schedule-based release cadence.

```
Train: every Tuesday at 14:00 UTC
   - Branch from main at 14:00 Mon
   - Test all week
   - Release Tue 14:00
   - Hotfixes go in next train (or via hotfix branch)
```

### When Useful
- Predictability for downstream consumers
- Coordinated multi-service deploys
- Regulated industries (audit trail per release)

### Trade-Off
- Lower deploy frequency
- Higher batch size = higher CFR risk
- Counter to "trunk-based + continuous delivery"

Modern web: skip release trains; continuous delivery. Periodic releases for: packaged SDKs, mobile apps (App Store), regulated software.

## Hotfix Workflow

Production bug found. Cherry-pick fix to release branch.

### Versioned Product
```
main:           A — B — C — D
                    \
release/1.0:        v1.0.0 — (hotfix) — v1.0.1
```

1. Fix on main (commit X)
2. Cherry-pick X to release/1.0 branch
3. Tag v1.0.1
4. Build + release
5. Update changelog
6. Communicate to customers

### Continuous Delivery (no release branches)
- Fix on main
- Deploy ASAP
- No back-port needed (only one supported version)

## Release Notes

What goes in:
- New features (with examples or links)
- Bug fixes (with issue links)
- Breaking changes (highlighted, with migration steps)
- Deprecations (with timeline)
- Security fixes (with CVE if assigned)
- Acknowledgments (contributors)

### Tools
- **release-please** auto-generates from commits
- **semantic-release** similar
- **Reno** (OpenStack) for manual + auto-mixed
- **Towncrier** (Python world)

## Communicating Releases

- Email/Slack to internal users
- Status page entry
- API consumers: changelog API or RSS
- Customer-facing: blog post
- Mobile/desktop: App Store / Microsoft Store update note

## Pre-releases & Channels

Multi-channel for software:
- **Stable** — production
- **Beta** — opt-in early users
- **Alpha / Nightly** — for testing

Examples: Chrome, VS Code, Docker Desktop.

Each channel can have its own pipeline + release cadence.

## Version Pinning vs Floating

Dependency strategies:
- **Pin exact** (`1.2.3`) — most stable; manual upgrades
- **Pin minor** (`~1.2.3` = `>=1.2.3 <1.3.0`) — get patches
- **Pin major** (`^1.2.3` = `>=1.2.3 <2.0.0`) — get features + patches
- **Floating** (`*` or `latest`) — risky for production

Production: prefer pinning + automated updates via Renovate / Dependabot.

## Multi-Version Support

If you support multiple versions:
- N-1 policy (current + previous)
- N-2 (current + two previous)
- Long-term support (LTS) — e.g., Node 20 LTS

Each version has its own release branch + maintenance workflow.

## Release Engineering Practices at Scale

- **Release Manager** rotation (weekly)
- **Release dashboard** with go/no-go status
- **Pre-release readiness** checklist
- **Rollback rehearsal** during release week
- **Post-release verification** (smoke tests, business KPIs)
- **Release retros** (what went well, what didn't)

## Interview Themes

- "SemVer — when bump major?"
- "Release trains vs continuous delivery"
- "Hotfix workflow"
- "Automated release tooling — what do you use?"
- "Multi-version support — strategy"
