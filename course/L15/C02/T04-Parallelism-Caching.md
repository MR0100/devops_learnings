# L15/C02/T04 — Parallelism & Caching

## Learning Objectives

- Optimize pipeline speed
- Use caches correctly

## Parallelism

Wall-clock = max(parallel jobs) + overhead.

For: speed.

## Caching

Store + retrieve artifacts:
- Dependencies
- Build outputs
- Test results
- Docker layers

For: skip recompute.

## GitHub Actions Cache

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

Key: when files change, key changes.
Restore-keys: fall back to older cache if exact miss.

## Caching Patterns

### Dependencies
```yaml
- uses: actions/setup-node@v4
  with:
    cache: 'npm'  # auto-caches node_modules
```

### Docker Layers
```yaml
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Go Modules
```yaml
- uses: actions/setup-go@v5
  with:
    cache: true
```

### Maven
```yaml
- uses: actions/setup-java@v4
  with:
    cache: maven
```

### pip
```yaml
- uses: actions/setup-python@v5
  with:
    cache: pip
```

## Cache Hierarchies

```
Layer 1: Exact key match (instant)
Layer 2: Restore key (close match)
Layer 3: No cache (rebuild)
```

For: graceful miss.

## Cache Invalidation

Key change → cache miss.

```yaml
key: ${{ hashFiles('package-lock.json') }}
```

Lock file change → new cache.

## Cache Size

GitHub Actions:
- 10 GB per repo
- Auto-evicted by LRU

For: manage carefully.

## Cache Distributed

For monorepo:
- Bazel remote cache (gRPC)
- Nx cache (cloud)
- Turborepo cache

Cross-CI-machine; even local-CI.

## Distributed Builds (Bazel)

```bash
bazel build --remote_cache=grpc://cache:8080 //service:image
```

Reuse build outputs across:
- Local dev
- CI machines
- Different branches

For: massive speedup.

## Hermetic Caching

Bazel-style:
- Build inputs declared
- Outputs deterministic
- Cache by hash of inputs

Same inputs = same output (skip).

For: Bazel, Nix, Buck2.

## Parallelism Limits

### Runner Concurrency
GitHub: 20 parallel jobs (free; more for paid).

For huge: self-hosted runners.

### Within Job
```bash
make -j8 test    # 8 parallel
```

CPU cores. Tune for runner.

### Test Frameworks
```bash
pytest -n auto    # parallel tests
jest --maxWorkers=4
```

## Self-Hosted Runners

```yaml
runs-on: self-hosted
```

For:
- Custom hardware
- Pre-warmed cache
- VPN access
- Avoid GitHub-hosted limits

Pro: control, speed.
Con: maintenance.

## Larger Runners (Paid)

GitHub: larger runners (more CPU/RAM).

For: build-heavy.

## Ephemeral Runners

Each job: fresh runner.

For: isolation.

Tools: Actions Runner Controller (K8s).

## Image-Based Runners

Pre-installed deps:
```yaml
runs-on: ubuntu-latest  # GitHub-managed image
```

Or custom:
```yaml
runs-on:
  - self-hosted
  - my-custom-image
```

For: avoid install time.

## Stages of Optimization

### 1. Sequential Baseline
Run everything serial. Measure.

### 2. Parallel
Identify independent. Run in parallel.

### 3. Cache
Identify recompute. Cache.

### 4. Skip
Skip if unchanged.

### 5. Shard
Split big sequential into parallel.

## Skip Unchanged

```yaml
- uses: dorny/paths-filter@v3
  id: changes
  with:
    filters: |
      backend:
        - 'backend/**'

- if: steps.changes.outputs.backend == 'true'
  run: test backend
```

For monorepos: skip irrelevant builds.

## Docker BuildKit Cache

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20

RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

Mount cache; persists across builds.

For: dramatic speedup.

## Layer Order

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

Package files first → npm cached if unchanged.

For: build cache hit.

## Cache Key Strategies

### File Hash
```yaml
key: ${{ hashFiles('lockfile') }}
```

### Date-Based
```yaml
key: ${{ runner.os }}-cache-${{ github.run_id }}
```

For: bust periodically.

### Branch + File
```yaml
key: ${{ github.ref }}-${{ hashFiles('...') }}
```

For: branch-specific.

## Cache Warming

```yaml
warm:
  schedule:
    - cron: '0 0 * * *'  # nightly
  steps:
    - run: build everything to warm cache
```

For: pre-warm; faster builds during day.

## Cache Hit Metrics

```yaml
- uses: actions/cache@v4
  id: cache
  with: ...
- run: echo "Cache hit: ${{ steps.cache.outputs.cache-hit }}"
```

For: track effectiveness.

## When NOT to Cache

- Tiny tasks
- Non-deterministic
- Security-sensitive (cache poison risk)
- Cache > rebuild cost

For: small builds, don't cache.

## Cache Poisoning

Malicious entity sets bad cache; subsequent builds use it.

Mitigations:
- Cache only trusted deps
- Verify checksums
- Don't cache from PRs (less trusted)

```yaml
- if: github.event_name == 'push'
  uses: actions/cache@v4
```

## Real Cost

Pipeline 30 min → 5 min:
- Engineer time saved (10×)
- Faster feedback
- More deploys/day

For: high ROI on caching.

## Best Practices

- Cache deps always
- Layer Dockerfile right
- Identify parallelizable
- Profile pipeline
- Self-hosted runners if scale
- Pre-warm overnight
- Monitor cache hit rate

## Common Mistakes

- No caching (slow)
- Wrong cache key (always miss)
- Cache too large (eviction)
- Parallel without independence (race conditions)
- Don't profile (don't know bottleneck)

## Profile Tools

- GitHub Actions: built-in timing
- Custom: emit timing logs

```yaml
- name: Time step
  run: |
    START=$(date +%s)
    make build
    END=$(date +%s)
    echo "Took $((END - START))s"
```

## Quick Refs

```yaml
# Cache
- uses: actions/cache@v4
  with:
    path: PATH
    key: KEY
    restore-keys: |
      FALLBACK

# Parallel
strategy:
  matrix: ...

# BuildKit
RUN --mount=type=cache,target=...

# Self-hosted
runs-on: self-hosted
```

## Interview Prep

**Mid**: "Caching strategies."

**Senior**: "Pipeline optimization."

**Staff**: "Build platform at scale."

## Next Topic

→ Move to [L15/C03 — Build Systems](../C03/README.md)
