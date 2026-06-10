# L16/C02/T01 — GitHub Actions: Workflows, Jobs, Steps

## Learning Objectives

- Structure GitHub Actions
- Use core features

## Hierarchy

```
Workflow (.github/workflows/X.yml)
├─ Trigger (on:)
└─ Jobs
   └─ Steps
      └─ Actions or commands
```

## Workflow

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
      - run: make test
```

## Triggers

```yaml
on:
  push:
    branches: [main, 'release/*']
    paths: ['src/**']
    tags: ['v*']
  pull_request:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
    inputs:
      env:
        type: choice
        options: [dev, staging, prod]
  workflow_run:
    workflows: [CI]
    types: [completed]
```

## Jobs

Run in parallel by default:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]

  lint:
    runs-on: ubuntu-latest
    steps: [...]

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps: [...]
```

## Runners

```yaml
runs-on: ubuntu-latest          # GitHub-hosted
runs-on: ubuntu-22.04
runs-on: macos-latest
runs-on: windows-latest
runs-on: self-hosted             # custom
runs-on: [self-hosted, gpu]
```

## Steps

```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v4
    with:
      fetch-depth: 0

  - name: Setup Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.12'
      cache: pip

  - name: Install
    run: pip install -r requirements.txt

  - name: Test
    run: pytest
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Action Types

### Marketplace
```yaml
- uses: actions/checkout@v4
- uses: docker/build-push-action@v6
- uses: aws-actions/configure-aws-credentials@v4
```

### Composite
```yaml
# .github/actions/setup/action.yml
name: Setup
runs:
  using: composite
  steps:
    - run: npm ci
      shell: bash
```

```yaml
- uses: ./.github/actions/setup
```

### Docker Container
```yaml
runs:
  using: docker
  image: Dockerfile
```

### JS
TypeScript / JavaScript actions.

## Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python: ['3.10', '3.11', '3.12']
    exclude:
      - os: macos-latest
        python: '3.10'
```

6 - 1 = 5 jobs.

## Conditional

```yaml
- run: deploy.sh
  if: github.ref == 'refs/heads/main' && success()

- run: rollback.sh
  if: failure()
```

## Outputs

```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: echo "version=1.0.0" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

## Environment Vars

```yaml
env:
  GLOBAL: value

jobs:
  test:
    env:
      JOB_VAR: value
    steps:
      - run: echo $JOB_VAR
        env:
          STEP_VAR: value
```

## Secrets

```yaml
- run: deploy.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

Stored in repo / org / environment.

## Artifacts

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: dist/

- uses: actions/download-artifact@v4
  with:
    name: build
    path: dist/
```

For: share between jobs.

## Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

## Permissions

```yaml
permissions:
  contents: read
  packages: write
  id-token: write   # for OIDC
```

Limit scope.

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Cancel old runs on push.

## Manual Approval

```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://prod.example.com
    runs-on: ubuntu-latest
    steps: [...]
```

Configure `production` env: require reviewers.

## Reusable Workflows

```yaml
# .github/workflows/deploy.yml (callable)
on:
  workflow_call:
    inputs:
      env: { type: string }
```

```yaml
# Caller
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    with:
      env: staging
```

## Limits

GitHub-hosted:
- 6 hours per job
- 2000 minutes/mo free tier
- 20 concurrent jobs

Paid: more.

## Best Practices

- Use marketplace actions (don't reinvent)
- Pin action versions (commit SHA)
- Cache deps
- Parallel jobs
- Reuse workflows
- Secrets in vault
- OIDC for cloud

## Common Mistakes

- Unpinned actions (supply chain risk)
- Secrets in code
- No caching (slow)
- Sequential when parallel possible
- Permissions too broad

## Quick Refs

```yaml
on: [push, pull_request]
jobs:
  X:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: command
```

```bash
# Local
act -j JOB_NAME
```

## Interview Prep

**Junior**: "GitHub Actions basics."

**Mid**: "Workflows / jobs / steps."

**Senior**: "Reusable workflows."

## Next Topic

→ [T02 — Runners (GitHub-Hosted vs Self-Hosted)](T02-Runners.md)
