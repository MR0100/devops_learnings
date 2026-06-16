# L15/C01/T01 — Continuous Integration

## Learning Objectives

- Define CI properly
- Understand why CI matters

## CI

Practice of integrating code changes frequently:
- Commit to mainline often (daily+)
- Automated build + test on commit
- Fast feedback (< 10 min)
- Broken main = team stops, fixes

For: avoid "integration hell" of long-lived branches.

## Origin

Martin Fowler popularized; comes from Extreme Programming (XP).

## Why CI

Without CI:
- Long-lived branches diverge
- Merge conflicts massive
- Bugs found late
- Slow releases

With CI:
- Small integrations
- Bugs found minutes later
- Always release-ready
- Confidence to refactor

## CI Core Practices

### Single Source Repository
Everyone works in same repo; commit to main (or short-lived branch).

### Automated Build
One command (or push event) builds all.

### Self-Testing Build
Tests run on every commit. Pass = artifact good.

### Daily Commits (At Least)
Frequent integration.

### Main Always Green
Build broken? Team fixes immediately.

### Fast Build
< 10 min ideal. Slower → less use.

### Test in Production-Like
Staging mirrors prod.

### Easy to Get Latest Build
Artifacts accessible.

### Visible
Status visible to all (e.g. Slack channel).

### Automated Deploy
At least to staging.

## CI ≠ CD

CI: integrate code, run tests.
CD: deploy automatically (continuous delivery or deployment).

Many do CI without full CD.

## Trunk-Based Development

```
main (always green)
   ↑
short-lived feature branches (hours-days)
```

vs GitFlow (long-lived branches; integration debt).

For: high CI throughput.

## Branch by Abstraction

For long features without long-lived branches:
- Abstract behind flag/interface
- Implement incrementally
- Toggle when ready

For: trunk-based with big changes.

## Feature Flags

Deploy code disabled. Toggle on later.

For: deploy ≠ release.

## CI Pipeline Stages

```
1. Lint / static analysis (< 30 s)
2. Unit tests (< 2 min)
3. Build artifact (< 5 min)
4. Integration tests (< 5 min)
5. (optional) Security scans, SBOM
6. Push artifact to registry
```

Total: < 15 min ideal.

## CI Server

- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Buildkite
- TeamCity
- Travis CI (declining)

For: automate above.

## Trigger Events

- Push to branch
- PR opened / updated
- Tag pushed
- Schedule (nightly)
- Manual

## Build Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu, macos, windows]
    python: ["3.10", "3.11", "3.12"]
```

For: multiple environments per commit.

## Caching

- Dependencies (npm, pip, Maven)
- Docker layers
- Test results

For: speed.

## Parallel Jobs

```yaml
jobs:
  test-unit:
    runs-on: ubuntu-latest
    steps: ...
  test-integration:
    runs-on: ubuntu-latest
    steps: ...
  lint:
    runs-on: ubuntu-latest
    steps: ...
```

Run concurrently.

## Pull Request CI

```yaml
on:
  pull_request:
    branches: [main]
```

Run on every PR commit. Required for merge.

For: gate quality.

## Required Checks

```
GitHub branch protection:
- Require CI passes
- Require review
- Require up-to-date branch
```

For: enforce quality.

## Notifications

On failure:
- Slack
- Email
- PagerDuty (for prod issues)

For: visible failures.

## Test Coverage

Tools: Coveralls, Codecov.

Targets:
- Critical paths: 80%+
- All code: 60-80% typical

Don't game it.

## Static Analysis

- Linters (ESLint, Pylint, golangci-lint)
- Security (Semgrep, CodeQL)
- Style (Prettier, Black)

Fast; catches obvious.

## Build Optimization

- Cache deps
- Parallel
- Skip unchanged
- Distributed builds (Bazel)

For: < 5 min builds.

## Best Practices

- Main always green
- Fast pipeline (< 10 min)
- Self-service
- Required checks before merge
- Owner per failing test
- No retry of broken tests (fix instead)

## Common Mistakes

- Long-lived feature branches
- Slow tests
- Flaky tests ignored
- No required checks
- Broken main left for hours
- Manual quality gates

## Anti-Patterns

### "Mainline-Only" Without Discipline
Push directly without tests. Breaks main.

### "Integration Branch"
Merging features into integration branch first. Loses CI value.

### Long PRs
Reviews bottleneck. Aim < 400 lines.

### Skip CI for Hotfixes
Bypass = future incidents.

## Metrics

- Commits/day
- Build time
- Test pass rate
- Mean time to recovery (broken main)
- PR review time

For: improve over time.

## DORA Metrics

- Deployment frequency
- Lead time
- Change failure rate
- Mean time to restore

For: CI/CD maturity.

## Continuous Integration vs Trunk-Based Dev

- CI: integrate often + test
- TBD: short-lived branches + main

Closely related; usually together.

## Examples

### Google
Massive monorepo; thousands of commits/day; TBD; CI required.

### Facebook
Monorepo; trunk-based; CI on commit.

### GitHub
Trunk-based; CI required; small PRs.

## Tools Evolution

- 1990s: nightly builds
- 2000s: CruiseControl, Hudson/Jenkins
- 2010s: Travis CI, Circle CI
- 2020s: GitHub Actions, GitLab CI

For: cloud-native CI is standard.

## Quick Refs

```
CI core: integrate often, test always, main green
Trigger: push, PR, schedule, manual
Speed: < 10 min ideal
Gates: required checks
```

## Interview Prep

**Junior**: "What's CI."

**Mid**: "CI vs CD."

**Senior**: "CI principles."

**Staff**: "CI maturity at scale."

## Next Topic

→ [T02 — Continuous Delivery vs Continuous Deployment](T02-CD-vs-Deploy.md)
