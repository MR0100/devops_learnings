# L16/C02 — GitHub Actions

## Topics

- **T01 Workflows, Jobs, Steps** — Workflow = YAML in `.github/workflows/`; one or many jobs; each job many steps.
- **T02 Runners (GitHub-Hosted vs Self-Hosted)** — Hosted: free quota + paid; ephemeral. Self-hosted: your infra, your scale.
- **T03 Reusable Workflows & Composite Actions** — `workflow_call` for orchestration; composite actions for step bundles.
- **T04 OIDC for Cloud Deploys** — Short-lived tokens to AWS/GCP/Azure; no static credentials.
- **T05 Secrets, Environments, Approvals** — Environment-scoped secrets; required reviewers for prod.

## Workflow Anatomy

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read
  id-token: write    # OIDC

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true
      - run: go test ./...

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-deployer
          aws-region: us-east-1
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: 123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - run: kubectl set image deployment/app app=123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com    # Required reviewers gate here via env settings
    steps:
      - run: kubectl set image deployment/app app=...
```

## OIDC to AWS

In AWS IAM, the role's trust policy:
```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
    }
  }
}
```

Workflow gets short-lived AWS creds. No long-lived secrets in GitHub.

## Reusable Workflows

```yaml
# .github/workflows/build.yml (reusable)
on:
  workflow_call:
    inputs:
      env:
        type: string
        required: true
jobs:
  build: { ... uses input.env ... }

# Caller
jobs:
  build:
    uses: ./.github/workflows/build.yml
    with: { env: prod }
```

## Composite Actions

Reusable steps:
```yaml
# .github/actions/setup/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-go@v5
      with: { go-version: '1.22' }
    - uses: actions/cache@v4
      ...
```

Use:
```yaml
- uses: ./.github/actions/setup
```

## Self-Hosted Runners

For private repos and cost. Run on K8s via ARC (Actions Runner Controller):
- Ephemeral runners per job (security)
- Auto-scale (Karpenter-backed)
- Per-repo or per-org runner sets

## Environments

- Scoped secrets
- Required reviewers (manual approval gate)
- Deployment branches restriction
- Wait timer

## Strengths
- Tight GitHub integration
- Massive Action marketplace
- Free for public repos; generous for OSS
- OIDC for cloud is clean

## Weaknesses
- Tied to GitHub
- Action supply chain (3rd-party Actions can be risky)
- Cost can grow with self-hosted complexity

## Interview Themes

- "GitHub Actions vs Jenkins"
- "OIDC for AWS — walk me through"
- "Self-hosted runners on K8s — design"
- "Action supply chain security"
- "Reusable workflows vs composite actions"
