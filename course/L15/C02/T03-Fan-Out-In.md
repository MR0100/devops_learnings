# L15/C02/T03 — Fan-Out / Fan-In Patterns

## Learning Objectives

- Parallelize pipelines
- Aggregate results

## Fan-Out

One job → many parallel jobs:
```
       ┌─ test-unit
build ─┼─ test-integration
       ├─ test-e2e
       └─ security-scan
```

For: parallel work; faster total.

## Fan-In

Many jobs → one job:
```
test-unit       ─┐
test-integration ┼─ deploy
test-e2e        ─┘
```

Wait for all; then proceed.

For: synchronization point.

## GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: ...

  test-unit:
    needs: build
    runs-on: ubuntu-latest
    steps: ...

  test-integration:
    needs: build
    runs-on: ubuntu-latest
    steps: ...

  test-e2e:
    needs: build
    runs-on: ubuntu-latest
    steps: ...

  deploy:
    needs: [test-unit, test-integration, test-e2e]
    runs-on: ubuntu-latest
    steps: ...
```

`needs`: dependency. Deploy waits for all three tests.

## GitLab CI

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build

test-unit:
  stage: test
  needs: [build]

test-int:
  stage: test
  needs: [build]

deploy:
  stage: deploy
  needs: [test-unit, test-int]
```

## Matrix Fan-Out

```yaml
test:
  strategy:
    matrix:
      os: [ubuntu, macos, windows]
      python: ["3.10", "3.11", "3.12"]
  runs-on: ${{ matrix.os }}
```

9 jobs from one definition.

## Dynamic Fan-Out

```yaml
detect:
  outputs:
    matrix: ${{ steps.set.outputs.matrix }}
  steps:
    - id: set
      run: |
        echo "matrix=$(./find-services.sh | jq -R . | jq -s -c)" >> $GITHUB_OUTPUT

test:
  needs: detect
  strategy:
    matrix:
      service: ${{ fromJSON(needs.detect.outputs.matrix) }}
  steps:
    - run: test.sh ${{ matrix.service }}
```

For: change-driven; only test changed services.

## Aggregate Results

```yaml
results:
  needs: [test-unit, test-integration]
  if: always()
  runs-on: ubuntu-latest
  steps:
    - run: |
        if [ "${{ needs.test-unit.result }}" = "success" ] && \
           [ "${{ needs.test-integration.result }}" = "success" ]; then
          echo "All passed"
        else
          exit 1
        fi
```

For: explicit aggregation.

## fail-fast vs continue

```yaml
strategy:
  matrix: ...
  fail-fast: false   # don't cancel on first failure
```

For: see all results.

`true` (default): one fails → cancel rest. Fast feedback.

## Shard

```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:
    - run: pytest --shard=${{ matrix.shard }}/4
```

Split test suite into 4 shards. 4x faster.

## Pipeline DAG

```
       build
      /  |  \
   test1 test2 test3
      \  |  /
       deploy
```

Topology = DAG.

For: visualize dependencies.

## Conditional Fan-Out

```yaml
deploy:
  strategy:
    matrix:
      env: [staging, prod]
      include:
        - env: prod
          approval: required
  if: |
    github.ref == 'refs/heads/main' &&
    (matrix.env == 'staging' || github.event_name == 'push')
```

For: stage-aware promotion.

## Multi-Region Fan-Out

```yaml
deploy:
  strategy:
    matrix:
      region: [us-east-1, eu-west-1, ap-southeast-1]
  steps:
    - run: deploy.sh --region=${{ matrix.region }}
```

Deploy to all regions in parallel.

## Rolling Fan-Out (Sequential)

```yaml
deploy-us-east:
  steps:
    - run: deploy us-east-1

deploy-eu-west:
  needs: deploy-us-east
  steps:
    - run: deploy eu-west-1

deploy-ap:
  needs: deploy-eu-west
  steps:
    - run: deploy ap-southeast-1
```

For: progressive rollout.

## Concurrency Limits

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false
```

Only one deploy at a time per ref.

For: prevent racing deploys.

## Workflow Dispatch (Manual Fan-In)

```yaml
on:
  workflow_dispatch:
    inputs:
      build_id:
        type: string
```

For: artifacts from other workflow.

## Long-Running Aggregation

For builds that depend on many upstream:
```yaml
- uses: convictional/trigger-workflow-and-wait@v1
  with:
    workflow_file_name: upstream.yml
```

Trigger and wait.

## Fan-Out Cost

Each parallel job = runner minute.

For 100 shards × 5 min = 500 runner-min vs 1 × 500 min.

Same total; different wall-clock.

## Pipeline Time vs Cost

- Faster wall-clock: more parallelism
- Lower cost: less parallelism
- Trade-off

Optimize for engineer time (parallelism wins).

## Real Examples

### Monorepo Tests
Detect changed → fan-out test per changed service.

### Multi-Cloud
Build artifact → fan-out deploy to AWS + GCP + Azure.

### Test Matrix
Fan-out OS × language version → ensure compatibility.

### Multi-Region
Build → fan-out deploy per region.

## Best Practices

- Fan-out where independent
- Fan-in for sync points
- fail-fast for fast feedback (most cases)
- continue-on-error for "see all failures"
- Concurrency limits for deploys
- Cost vs wall-clock awareness

## Common Mistakes

- Sequential when parallel possible
- Fan-out too much (cost spike)
- No fail-fast (waste compute on doomed runs)
- Missing dependencies (race conditions)

## Quick Refs

```yaml
# Fan-out
strategy: { matrix: ... }
# or multiple jobs depending on same parent

# Fan-in
needs: [job1, job2, job3]

# Shard
matrix: { shard: [1,2,3,4] }

# Cost control
fail-fast: true

# Sync
concurrency: { group: ... }
```

## Interview Prep

**Mid**: "Fan-out vs fan-in."

**Senior**: "Parallelize pipeline."

**Staff**: "Pipeline performance."

## Next Topic

→ [T04 — Parallelism & Caching](T04-Parallelism-Caching.md)
