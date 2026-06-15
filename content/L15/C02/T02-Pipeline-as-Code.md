# L15/C02/T02 — Pipeline as Code

## Learning Objectives

- Define pipelines in code
- Version pipeline changes

## Pipeline as Code

CI config in repo (not UI clicks):
- YAML or DSL
- Versioned (Git)
- Reviewed
- Tested
- Reused

## Why

- History
- Code review
- Reproducible
- Portable
- Templated

## Examples

### GitHub Actions
```yaml
# .github/workflows/ci.yml
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test
```

### GitLab CI
```yaml
# .gitlab-ci.yml
test:
  script: make test
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
```

### Jenkins (Declarative)
```groovy
// Jenkinsfile
pipeline {
  agent any
  stages {
    stage('Test') {
      steps { sh 'make test' }
    }
  }
}
```

### CircleCI
```yaml
# .circleci/config.yml
version: 2.1
jobs:
  test:
    docker:
      - image: ubuntu:24.04
    steps:
      - checkout
      - run: make test
```

## Reuse via Templates

### GitHub Reusable Workflows
```yaml
# .github/workflows/reusable.yml
on:
  workflow_call:
    inputs:
      env: { type: string }

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh --env=${{ inputs.env }}
```

```yaml
# Caller
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable.yml
    with:
      env: staging
```

### GitLab CI Includes
```yaml
include:
  - project: 'org/templates'
    file: 'common.yml'
```

### Jenkins Shared Libraries
```groovy
@Library('shared-lib') _
mylib.standardPipeline()
```

For: DRY across teams.

## Testing Pipelines

### Local Runners
- `act` (GitHub Actions local)
- `gitlab-runner exec` (GitLab)

```bash
act -j test
```

For: validate before push.

### Pipeline of Pipelines
Pipeline that validates other pipelines.

```yaml
- run: yamllint .github/workflows/
- run: action-validator .github/workflows/*.yml
```

## Lint

```bash
# GitHub Actions
actionlint .github/workflows/*.yml

# GitLab
gitlab-ci-lint .gitlab-ci.yml
```

## Pipeline Versioning

Pipeline change → PR → review → merge.

For: prevent broken pipelines.

## Secrets

NOT in pipeline code:
```yaml
- run: deploy.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

Secrets in CI vault (GitHub Secrets, GitLab Variables).

## Environment Vars

```yaml
env:
  NODE_ENV: production
  REGION: us-east-1
```

Per-job or workflow-level.

## Conditionals

```yaml
- if: github.event_name == 'pull_request'
  run: echo "PR build"
- if: github.ref == 'refs/heads/main'
  run: echo "Main build"
```

For: branching logic.

## Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu, macos]
    node: ["20", "22"]
  fail-fast: false
```

Multiple configs.

## Reusable Steps

### Composite Actions
```yaml
# .github/actions/setup/action.yml
name: Setup
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
    - run: npm ci
      shell: bash
```

Use:
```yaml
- uses: ./.github/actions/setup
```

## Custom Actions

Reusable across repos:
- Docker action
- JavaScript action
- Composite

Publish to Marketplace.

## DRY Patterns

### Org Templates
```
.github/workflow-templates/
  ci.yml
  cd.yml
```

New repo: use template.

### Common Steps
```yaml
- &setup
  uses: ./.github/actions/setup
```

### Centralized Config
Settings in org repo; teams reference.

## Pipeline Patterns

### Standard Service
```
Lint → Test → Build → Deploy
```

### Library
```
Lint → Test → Publish to artifact repo
```

### Mobile
```
Lint → Test → Build IPA/APK → Upload to TestFlight/Play
```

### Documentation
```
Lint → Build site → Deploy to S3 / Pages
```

## Pipeline as Code Anti-Patterns

### Click Ops Mixed In
Pipeline defined in code; secrets / settings in UI.

For: prefer fully declarative.

### Single Huge File
1000-line pipeline. Split into reusable.

### No Tests
Pipeline never tested. Breaks at worst time.

### Branching Logic in YAML
Complex if/else. Move to scripts.

## Scripts vs Inline

### Inline
```yaml
- run: |
    npm ci
    npm test
    npm build
```

OK for short.

### Scripts
```yaml
- run: ./ci/test.sh
```

Better for complex:
- Test locally
- Reuse outside CI
- Easier to read

For: > 5 lines → script.

## Pipeline Engine Choice

| | Strength | Weakness |
|---|---|---|
| GitHub Actions | Easy, marketplace, GitHub-tight | GitHub-only |
| GitLab CI | Built-in, full DevOps | Less ecosystem |
| Jenkins | Mature, flexible | Old, complex |
| CircleCI | Fast, polished | Paid plans |
| Buildkite | Self-hosted runners, fast | Smaller mindshare |

## Monorepo Pipelines

```yaml
jobs:
  detect:
    outputs:
      services: ${{ steps.changes.outputs.changes }}
    steps:
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            api: 'services/api/**'
            web: 'services/web/**'

  test-changed:
    needs: detect
    strategy:
      matrix:
        service: ${{ fromJSON(needs.detect.outputs.services) }}
    steps:
      - run: cd services/${{ matrix.service }} && make test
```

For: build only changed.

## Pipeline as Code for IaC

```yaml
- name: Terraform plan
  run: terraform plan -out=tfplan
- name: PR comment with plan
  uses: marocchino/sticky-pull-request-comment@v2
  with:
    message: ${{ steps.plan.outputs.stdout }}
```

For: visibility on infra changes.

## Auditing

Git log = pipeline history.
Each change reviewed.

For: compliance.

## Migration to Pipeline as Code

From Jenkins UI / CircleCI UI:
1. Export current config
2. Translate to YAML
3. Commit
4. Validate
5. Decommission UI config

## Best Practices

- All pipeline in repo
- Reusable workflows / composite actions
- Lint pipelines
- Test locally (act)
- Document inputs / outputs
- Secrets in vault
- Scripts > inline for complex

## Common Mistakes

- Inline 100 lines
- No reuse (copy-paste)
- Secrets in YAML
- No lint
- Pipeline breaks on every refactor

## Quick Refs

```yaml
# GitHub
.github/workflows/*.yml

# GitLab
.gitlab-ci.yml + include:

# Jenkins
Jenkinsfile

# CircleCI
.circleci/config.yml

# Linters
actionlint, yamllint, gitlab-ci-lint
```

## Interview Prep

**Junior**: "What's pipeline as code."

**Mid**: "Why version it."

**Senior**: "Pipeline reuse."

**Staff**: "Pipeline platform strategy."

## Next Topic

→ [T03 — Fan-Out / Fan-In Patterns](T03-Fan-Out-In.md)
