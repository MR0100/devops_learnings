# L16/C09/T01 — Drone & Other CI Tools

## Learning Objectives

- Know alternative CI tools
- Pick for niche

## Drone

Container-native CI:
```yaml
# .drone.yml
kind: pipeline
name: default

steps:
- name: test
  image: golang:1.22
  commands:
  - go test ./...

- name: build
  image: golang:1.22
  commands:
  - go build -o myapp

- name: deploy
  image: alpine
  commands:
  - ./deploy.sh
  when:
    branch: [main]
```

Pros: container-first, simple.
Cons: smaller community.

## Buildkite

Hybrid: SaaS controller + your runners:
```yaml
# .buildkite/pipeline.yml
steps:
  - label: ":hammer: Build"
    command: make build

  - wait

  - label: ":rocket: Deploy"
    command: deploy.sh
    branches: "main"
```

Pros:
- Self-hosted runners (security + cost)
- SaaS coordination
- Fast UI
- Plugins (Bash)

For: medium-large orgs.

## Travis CI

Once-dominant; declining:
```yaml
# .travis.yml
language: python
python: '3.12'
script: pytest
```

For: legacy.

Most projects migrated to GitHub Actions.

## TeamCity

JetBrains:
- UI-driven
- Build chains
- Build pool
- Enterprise

For: heavy customization, JetBrains shops.

## Bamboo

Atlassian:
- Jira integration
- Bitbucket integration

For: Atlassian shops.

Declining outside Atlassian.

## Bitbucket Pipelines

Atlassian SaaS:
```yaml
# bitbucket-pipelines.yml
image: python:3.12
pipelines:
  default:
    - step:
        script:
          - pytest
```

For: Bitbucket users.

## Azure Pipelines

Microsoft:
```yaml
# azure-pipelines.yml
pool:
  vmImage: ubuntu-latest

steps:
- script: pip install -r requirements.txt
- script: pytest
```

For: Azure DevOps users.

## AWS CodeBuild / CodePipeline

```yaml
# buildspec.yml
version: 0.2
phases:
  build:
    commands:
      - make build
      - make test
```

For: AWS-native.

Pros: IAM integration, low cost.
Cons: Less ecosystem.

## Cloud Build (GCP)

```yaml
# cloudbuild.yaml
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-t', 'gcr.io/PROJECT/myapp', '.']
- name: gcr.io/cloud-builders/docker
  args: ['push', 'gcr.io/PROJECT/myapp']
```

For: GCP-native.

## Concourse CI

Pipelines as YAML:
```yaml
jobs:
- name: test
  plan:
  - get: src
  - task: run-tests
    file: src/ci/tasks/test.yml
```

Niche but powerful for complex flows.

## Woodpecker CI

Drone fork; open source:
- Compatible with Drone configs
- Active community

For: self-hosted; OSS preference.

## Gerrit

Code review + CI integration:
- Verified label
- Buildbot integration

For: Linux kernel, Android.

## Nightly Builds / Cron

Many systems support cron:
- Build at off-peak
- Regression testing
- Dependency checks

```yaml
schedule:
  - cron: '0 0 * * *'
```

## Choosing

| Need | Tool |
|---|---|
| GitHub-native | GitHub Actions |
| GitLab-native | GitLab CI |
| K8s-native | Tekton |
| Multi-cloud CD | Spinnaker |
| GitOps | ArgoCD / Flux |
| Mac heavy | CircleCI |
| Container-first OSS | Drone / Woodpecker |
| Enterprise UI | TeamCity / Bamboo |
| Bitbucket | Bitbucket Pipelines |
| Azure | Azure Pipelines |
| AWS-native | CodeBuild |
| GCP-native | Cloud Build |

## Migration

Common: Jenkins → GitHub Actions or GitLab CI.

Reasons:
- Simpler
- Cloud-native
- Less ops

Plan:
1. Audit current
2. Pick replacement
3. Migrate job by job
4. Decommission

## Multi-Tool

Sometimes:
- CI: GitHub Actions
- CD: ArgoCD
- Specialized: Tekton

For: each strength.

## Trends

### Growing
- GitHub Actions
- GitLab CI
- Tekton
- ArgoCD

### Stable
- Jenkins (huge install base)
- CircleCI

### Declining
- Travis
- Bamboo (outside Atlassian)
- Drone (slower)
- Bitbucket Pipelines

## Best Practices

- One CI tool primary
- Pipeline as code
- Self-hosted runners for sensitive
- OIDC for cloud auth
- Cache aggressively
- Monitor pipeline time

## Common Mistakes

- Multiple CI tools (cognitive load)
- UI-configured (no version control)
- Long pipelines (slow feedback)
- No reuse

## Quick Refs

```
GitHub Actions: .github/workflows/
GitLab CI: .gitlab-ci.yml
Jenkins: Jenkinsfile
Drone: .drone.yml
Buildkite: .buildkite/pipeline.yml
Azure Pipelines: azure-pipelines.yml
Cloud Build: cloudbuild.yaml
AWS CodeBuild: buildspec.yml
CircleCI: .circleci/config.yml
```

## Interview Prep

**Mid**: "CI tool landscape."

**Senior**: "Tool selection."

**Staff**: "CI platform strategy."

## Next Topic

→ Move to [L16/C10 — Self-Hosted Runners at Scale](../C10/README.md)
