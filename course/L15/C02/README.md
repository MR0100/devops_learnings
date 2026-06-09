# L15/C02 — Pipeline Design

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Build-Test-Deploy.md) | Build → Test → Package → Deploy Phases | 1 hr |
| [T02](T02-Pipeline-as-Code.md) | Pipeline as Code | 0.5 hr |
| [T03](T03-Fan-Out-Fan-In.md) | Fan-Out / Fan-In Patterns | 0.5 hr |
| [T04](T04-Parallelism-Caching.md) | Parallelism & Caching | 1 hr |

## Reference Pipeline

```
[Commit]
   ↓
[Setup] — checkout, restore caches
   ↓
[Static Analysis] — lint, format, type check  (< 30s)
   ↓
[Unit Tests] — fast, isolated, mocked  (< 2 min)
   ↓
[Build Artifact] — compile, container image  (< 5 min)
   ↓
[Security Scan] — Trivy/Snyk, SBOM, OPA  (< 2 min)
   ↓
[Integration Tests] — real DB, real deps  (< 5 min)
   ↓
[Push to Registry] — tagged with commit SHA + version
   ↓
[Deploy to Staging]
   ↓
[E2E Tests in Staging]
   ↓
[Manual approval] (or automatic for continuous deploy)
   ↓
[Deploy to Prod] — canary 1% → 10% → 50% → 100%
   ↓
[Monitor SLOs] — auto-rollback on burn
```

Total: < 30 min commit-to-production for a mature team.

## Phase Details

### Build
- Compile source
- Resolve dependencies (cache!)
- Produce immutable artifact (binary, image)
- Tag with commit SHA + semver
- Push to artifact store

### Test
- Unit (fast, many)
- Integration (medium, fewer, real deps)
- Contract (between services)
- E2E (slow, expensive, fewer)
- Performance (smoke level in pipeline; deep in dedicated runs)
- Security (SAST, secrets scan)

### Package
- Containerize (multi-stage Dockerfile)
- Generate SBOM
- Sign image (Cosign)
- Push to registry

### Deploy
- Pull artifact (NOT rebuild)
- Apply manifests / Helm / Kustomize
- Progressive rollout (canary)
- Monitor + auto-rollback

## Pipeline as Code

Definition in repo. Every team's:

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22', cache: true }
      - run: go test ./...

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha
          aws-region: us-east-1
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: 123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Fan-Out / Fan-In

Run multiple jobs in parallel; merge before next stage.

```yaml
jobs:
  lint:       { runs-on: ubuntu-latest, ... }
  unit:       { runs-on: ubuntu-latest, ... }
  integration:{ runs-on: ubuntu-latest, ... }
  security:   { runs-on: ubuntu-latest, ... }

  build:
    needs: [lint, unit, integration, security]
    ...
```

Total time = max of parallel jobs, not sum.

## Matrix Strategies

```yaml
test:
  strategy:
    matrix:
      go: ['1.21', '1.22']
      os: [ubuntu-latest, macos-latest]
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/setup-go@v5
      with: { go-version: ${{ matrix.go }} }
```

4 combos run in parallel.

## Caching

The #1 speedup. Cache:
- Dependency manager downloads (npm, pip, go mod, Gradle)
- Build outputs (Bazel, Buck2)
- Docker layers (BuildKit + cache mounts)

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
```

Cache key based on lockfile hash. Cache valid until lockfile changes.

### Docker BuildKit Cache
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

Or push cache to registry:
```yaml
    cache-from: type=registry,ref=user/app:buildcache
    cache-to: type=registry,ref=user/app:buildcache,mode=max
```

## Test Sharding

Split tests across runners:

```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

8-minute test suite → 4 shards = 2 minutes (plus overhead).

## Pipeline Anti-Patterns

- **Slow tests blocking PRs** — split into smoke + nightly
- **Flaky tests retried silently** — quarantine, fix
- **Wall of UI clicks** — convert to code
- **No artifacts** — log lost forever
- **No cache** — wasted CI minutes
- **Sequential when parallel possible** — slow feedback
- **Deploy from CI runner** with credentials — use OIDC + dedicated deployer

## Cost Awareness

CI minutes are real:
- GitHub Actions hosted: $0.008/min Linux (free tier first)
- Self-hosted runners: pay for compute (potentially cheaper)
- Parallelism = more minutes, faster feedback (worth it)
- Test sharding helps even on free tier (parallelism limits)

## Interview Themes

- "Design a CI/CD pipeline"
- "Optimize a slow pipeline"
- "Build once, deploy many — design"
- "Caching strategy"
- "When parallelism isn't worth it"
- "Pipeline as code — what does it enable?"
