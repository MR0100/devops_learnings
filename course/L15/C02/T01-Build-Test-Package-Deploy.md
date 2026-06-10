# L15/C02/T01 — Build → Test → Package → Deploy Phases

## Learning Objectives

- Structure pipeline phases
- Optimize each

## Phases

```
1. Build:    compile / transpile / bundle
2. Test:    verify functionality
3. Package: container / archive / installer
4. Deploy:  to environment
```

Each: clear inputs/outputs.

## Build Phase

Inputs:
- Source code
- Dependencies

Outputs:
- Compiled binary
- Bundled JS
- Built artifact

```yaml
- name: Build
  run: |
    npm ci
    npm run build
```

## Optimization

### Cache deps
```yaml
- uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
```

### Parallel builds
For monorepo: build only changed.

### Incremental
Bazel / Buck2 / Gradle: only what changed.

### Distributed
Bazel remote cache; reuse across CI machines.

## Test Phase

Layered:
```
Unit (fast, isolated)
Integration (slower, multi-component)
E2E (slowest, full stack)
Performance / load (separate, longer)
```

## Run in Order of Speed

Unit first (5 min). Fail fast.
Integration (15 min).
E2E (30 min+).

If unit fails: skip rest.

## Parallel Test Suites

```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - run: pytest --shard=${{ matrix.shard }}/4
```

Split tests across runners. 4x speedup.

## Test Output

Tools that emit JUnit XML / Cobertura:
- pytest, JUnit, jest

CI parses; shows summary.

```yaml
- run: pytest --junitxml=test-results.xml
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.xml
```

## Coverage

```yaml
- run: coverage run -m pytest
- run: coverage report --fail-under=80
```

For: quality gate.

## Package Phase

Inputs:
- Built artifact
- Resources (configs, static)
- Dockerfile (or equivalent)

Outputs:
- Container image
- JAR / WAR
- Tarball

```yaml
- name: Build image
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker push registry/myapp:${{ github.sha }}
```

## Tag Strategy

```
Commit SHA: 7af2c8e3
Version: v1.2.3
Tag: latest (avoid in prod)

For prod: digest pin (sha256:abc...)
```

## Multi-Arch

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
```

For: AMD + ARM in single tag.

## SBOM Generation

```yaml
- uses: anchore/sbom-action@v0
  with:
    image: myapp:${{ github.sha }}
```

For: supply chain.

## Sign Image

```yaml
- uses: sigstore/cosign-installer@v3
- run: cosign sign --yes registry/myapp:${{ github.sha }}
```

## Deploy Phase

Per environment:
- Dev
- Staging
- Prod

```yaml
- name: Deploy to staging
  run: |
    kubectl set image deploy/myapp myapp=registry/myapp:${{ github.sha }} -n staging
    kubectl rollout status deploy/myapp -n staging
```

## Deploy Methods

### Push Model
CI runs `kubectl apply`.

For: simple.

### Pull Model (GitOps)
CI updates Git. ArgoCD applies.

For: declarative.

```yaml
- name: Update manifest
  run: |
    yq -i ".spec.template.spec.containers[0].image = \"registry/myapp:${{ github.sha }}\"" deploy.yaml
    git commit -am "Deploy ${{ github.sha }}"
    git push
```

## Post-Deploy Smoke

```yaml
- name: Smoke test
  run: |
    curl -f https://staging.example.com/health
    curl -f https://staging.example.com/api/version
```

If fail: rollback.

## Rollback

```yaml
- name: Rollback on failure
  if: failure()
  run: kubectl rollout undo deploy/myapp -n staging
```

For: forward fix or rollback path.

## Stages with Dependencies

```yaml
jobs:
  build:
    ...
  test:
    needs: build
    ...
  package:
    needs: test
    ...
  deploy:
    needs: package
    ...
```

For: orchestration.

## Conditional

```yaml
deploy-prod:
  if: github.ref == 'refs/heads/main'
  needs: deploy-staging
```

Only main → prod.

## Caching Strategy

```
Build deps:    cache (per-OS-lockfile)
Test results:  artifacts (display)
Built artifact: registry (durable)
```

Different lifetime per type.

## Environment Promotion

```
[CI build][test]
   ↓ artifact: registry/app:abc123
[Deploy dev]
   ↓ verify
[Deploy staging]
   ↓ verify
[Deploy prod]
```

Same artifact through.

## Parallel Deploys

For multi-region:
```yaml
deploy:
  strategy:
    matrix:
      region: [us-east-1, eu-west-1, ap-southeast-1]
  steps:
    - run: deploy.sh --region=${{ matrix.region }}
```

Faster total.

## Drift Detection

After deploy:
```yaml
- run: terraform plan -detailed-exitcode
  # exit 0 = no change; non-0 = drift
```

For: catch drift.

## Pipeline Times

Aim:
- Build + test: < 10 min
- Package + deploy: < 5 min
- Total: < 15 min

Long pipeline = less use.

## Optimize Order

```
Fast checks first:
- Lint (30 s)
- Syntax (10 s)
- Unit (2 min)

Then expensive:
- Integration (5 min)
- E2E (10 min)
- Perf (15 min)
```

Fail fast.

## When Phases Skip

```yaml
- if: github.event.head_commit.modified contains 'docs/'
  run: echo "Skipping build"
```

For: docs-only PRs.

## Multi-Repo Coordination

For monorepo: detect changed services; build only those.

```yaml
- id: changes
  uses: dorny/paths-filter@v3
  with:
    filters: |
      service-a:
        - 'services/a/**'
      service-b:
        - 'services/b/**'

- if: steps.changes.outputs.service-a == 'true'
  run: build service-a
```

## Best Practices

- Fast feedback per phase
- Build once; promote artifact
- Parallel where possible
- Cache aggressively
- Smoke post-deploy
- Rollback automation
- Clear pipeline diagram

## Common Mistakes

- Build per environment (drift)
- Sequential everything
- No cache (slow)
- No rollback
- Skip phases without intent

## Quick Refs

```yaml
# Phases
jobs:
  build: ...
  test: { needs: build }
  package: { needs: test }
  deploy-staging: { needs: package }
  deploy-prod: { needs: deploy-staging, if: ... }

# Optimization
strategy:
  matrix: ...

# Cache
uses: actions/cache@v4
```

## Interview Prep

**Mid**: "Pipeline phases."

**Senior**: "Optimization strategies."

**Staff**: "Pipeline at scale."

## Next Topic

→ [T02 — Pipeline as Code](T02-Pipeline-as-Code.md)
