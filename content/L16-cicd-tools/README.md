# L16 — CI/CD Tools

## Overview

This lecture covers the actual tools you'll use to implement L15's principles. Tool choices matter less than design — but you should be fluent in at least 2.

**10 chapters, 26 topics.**

## Chapter Map

### [C01](C01/) — Jenkins
- T01 Architecture (Controller / Agent)
- T02 Declarative vs Scripted Pipelines
- T03 Shared Libraries
- T04 Plugins Ecosystem (and Risks)
- T05 Configuration as Code (JCasC)

### [C02](C02/) — GitHub Actions
- T01 Workflows, Jobs, Steps
- T02 Runners (GitHub-Hosted vs Self-Hosted)
- T03 Reusable Workflows & Composite Actions
- T04 OIDC for Cloud Deploys
- T05 Secrets, Environments, Approvals

### [C03](C03/) — GitLab CI
- T01 .gitlab-ci.yml Anatomy
- T02 Runners
- T03 Auto DevOps
- T04 Multi-Project Pipelines

### [C04](C04/) — CircleCI
- T01 Orbs & Reusability

### [C05](C05/) — Tekton
- T01 Tasks, Pipelines, PipelineRuns
- T02 Cloud-Native CI on K8s

### [C06](C06/) — ArgoCD (Recap from L13)
- T01 Apps, ApplicationSets, Projects
- T02 Sync Hooks & Waves

### [C07](C07/) — Flux v2
- T01 Source, Kustomize, Helm Controllers

### [C08](C08/) — Spinnaker
- T01 Pipelines, Pipeline Templates
- T02 Multi-Cloud Deployments

### [C09](C09/) — Drone & Other CI Tools

### [C10](C10/) — Self-Hosted Runners at Scale
- T01 Karpenter-Backed Runners
- T02 ARC (Actions Runner Controller)
- T03 Security Considerations

## Tool Selection Matrix

| | Best For | Avoid When |
|---|---|---|
| Jenkins | Hybrid + heavily customized | Cloud-only modern stacks |
| GitHub Actions | GitHub-hosted code | Heavy plugin reliance |
| GitLab CI | All-in-one (Git + CI + Pages) | Just CI is needed |
| CircleCI | Mac builds, GPU | Cost-sensitive |
| Tekton | K8s-native CI on K8s | Non-K8s ops |
| ArgoCD | GitOps deploy (CD only) | Want CI too |
| Flux | GitOps purists | Want a UI |
| Spinnaker | Multi-cloud complex deploys | Small teams |

## GitHub Actions: Production Workflow

```yaml
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
      with:
        go-version: '1.22'
        cache: true
    - run: go test ./...

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # OIDC
      contents: read
    steps:
    - uses: actions/checkout@v4
    - uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
        aws-region: us-east-1
    - uses: docker/build-push-action@v5
      with:
        push: true
        tags: 123456789012.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}
```

## Self-Hosted Runners

For private repos and cost:
- ARC (Actions Runner Controller) on K8s — ephemeral runners per job
- GitLab runners on K8s — same pattern
- Jenkins agents on K8s (kubernetes plugin) or Karpenter

Security: separate runner namespaces per team; OIDC for cloud auth; no static secrets.

## Interview Themes

- "Compare CI tools you've used"
- "Walk me through a CI pipeline you've designed"
- "How do you handle CI for a monorepo?"
- "Self-hosted runners — what are the security concerns?"

## Next

→ [L17 — Monitoring & Observability](../L17-observability/README.md)
