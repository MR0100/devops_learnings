# L16/C02/T03 — Reusable Workflows & Composite Actions

## Learning Objectives

- DRY GitHub Actions
- Choose pattern

## Reusable Workflow

Whole workflow called from another:
```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
    secrets:
      DEPLOY_KEY:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh --env=${{ inputs.environment }}
        env:
          KEY: ${{ secrets.DEPLOY_KEY }}
```

## Caller

```yaml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
    secrets:
      DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}
```

Or cross-repo:
```yaml
uses: myorg/shared-workflows/.github/workflows/deploy.yml@v1
```

## Composite Action

Step-level reusable:
```yaml
# .github/actions/setup/action.yml
name: Setup Project
inputs:
  node-version:
    default: '20'

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - run: npm ci
      shell: bash
```

## Use Composite

```yaml
- uses: ./.github/actions/setup
  with:
    node-version: '22'
```

## Compare

| | Reusable Workflow | Composite Action |
|---|---|---|
| Scope | Whole workflow | Multi-step |
| Runners | Own | Inherited from caller |
| Secrets | Explicit | Inherited |
| Use case | End-to-end pipeline | Setup, deploy etc. |

## When Reusable Workflow

- Standard pipeline (CI for service type)
- Different runners per call
- Different secrets

## When Composite

- Common steps (setup, deploy)
- Inline within workflow
- Inherit context

## JavaScript Action

For complex:
```typescript
// action.ts
import * as core from '@actions/core';

async function run() {
  const input = core.getInput('name');
  console.log(`Hello, ${input}`);
}

run();
```

```yaml
# action.yml
name: Greet
runs:
  using: node20
  main: dist/index.js
```

## Docker Action

```yaml
runs:
  using: docker
  image: Dockerfile
```

```dockerfile
FROM alpine
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

## Share Patterns

### Org Repository
```
myorg/shared-workflows/
  .github/
    workflows/
      ci.yml
      deploy.yml
    actions/
      setup/
      test/
```

Other repos call.

### Per-Service Standard
```yaml
# Service repo uses:
jobs:
  ci:
    uses: myorg/shared-workflows/.github/workflows/service-ci.yml@v1
```

## Versioning

Pin:
```yaml
uses: myorg/shared/.github/workflows/X.yml@v1.0.0
uses: myorg/shared/.github/workflows/X.yml@SHA
uses: myorg/shared/.github/workflows/X.yml@main  # avoid
```

For: stability.

## Pass Outputs

```yaml
# Reusable
on:
  workflow_call:
    outputs:
      version:
        value: ${{ jobs.build.outputs.version }}

jobs:
  build:
    outputs:
      version: ${{ steps.v.outputs.version }}
    steps:
      - id: v
        run: echo "version=1.0.0" >> $GITHUB_OUTPUT
```

```yaml
# Caller
jobs:
  call:
    uses: ./.github/workflows/build.yml
  use-output:
    needs: call
    steps:
      - run: echo ${{ needs.call.outputs.version }}
```

## Best Practices

- Reusable workflows for standard pipelines
- Composite actions for common steps
- Pin versions
- Documented inputs
- Versioned releases
- Test in CI

## Common Mistakes

- @main pinning (drift)
- No documentation
- Too many parameters
- Reinvent existing

## Quick Refs

```yaml
# Reusable workflow caller
uses: owner/repo/.github/workflows/X.yml@vN
uses: ./.github/workflows/X.yml  # same repo

# Composite action
uses: owner/repo/.github/actions/X@vN
uses: ./.github/actions/X  # same repo
```

## Interview Prep

**Mid**: "Reuse in Actions."

**Senior**: "Reusable workflow vs composite."

## Next Topic

→ [T04 — OIDC for Cloud Deploys](T04-OIDC.md)
