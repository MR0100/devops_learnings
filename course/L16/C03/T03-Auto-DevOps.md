# L16/C03/T03 — Auto DevOps

## Learning Objectives

- Understand Auto DevOps
- Customize

## Auto DevOps

GitLab's pre-built pipeline:
- Detects language
- Builds + tests + scans + deploys
- K8s deploy
- Minimal config

For: greenfield, conventions over config.

## Enable

```yaml
# .gitlab-ci.yml
include:
  - template: Auto-DevOps.gitlab-ci.yml
```

Or: project settings → Auto DevOps.

## Stages

```
Build → Test → Code Quality → Security Scans → Deploy → Performance → ...
```

## Detection

- Detects Dockerfile or Buildpack
- Builds image
- Pushes to registry

## Scans

- SAST (Static Application Security Testing)
- DAST (Dynamic)
- Dependency Scanning
- Container Scanning
- License Compliance

For: built-in security.

## Deploy

To K8s:
- Auto Deploy via Helm
- Per-environment
- Review apps per MR
- Production

## Review Apps

Per merge request:
- Deploy to ephemeral env
- URL in MR
- Auto-cleanup on close

For: PR review with running app.

## Customize

```yaml
variables:
  AUTO_DEVOPS_PLATFORM: "kubernetes"
  PRODUCTION_REPLICAS: 3
  POSTGRES_ENABLED: "true"
```

Many vars to tune.

## Override Stages

```yaml
include:
  - template: Auto-DevOps.gitlab-ci.yml

# Override test
test:
  image: my-custom
  script: my-tests.sh
```

For: customize while keeping Auto DevOps.

## Disable Stages

```yaml
variables:
  CODE_QUALITY_DISABLED: "true"
  DAST_DISABLED: "true"
```

## Helm Chart

Default chart: gitlab-auto-deploy.

Custom:
```yaml
variables:
  AUTO_DEVOPS_CHART: my-chart
  AUTO_DEVOPS_CHART_REPOSITORY: https://chart.example.com
```

## Pros

- Quick start
- Sensible defaults
- Security baked in
- Best practices encoded

## Cons

- Opinionated (sometimes wrong)
- Hard to customize beyond vars
- K8s assumed
- Magic (hidden)

## When Auto DevOps

- Greenfield apps
- Want conventions
- Small team
- K8s ready

## When Not

- Existing pipeline
- Complex deploy
- Non-K8s
- Want control

## Per-Stage Override

```yaml
include:
  - template: Auto-DevOps.gitlab-ci.yml

build:
  stage: build
  image: my-builder
  script: my-build.sh
```

Replaces Auto DevOps build.

## Real Use

- Small/medium teams getting started
- Demos / POCs
- Internal tools

Less common at FAANGM (custom usually).

## Security Findings

Auto DevOps surface:
- MR widget
- Security dashboard
- Vulnerabilities

For: integrated workflow.

## Performance Testing

Built-in:
- k6-based
- Run per deploy
- Tracks regression

## Best Practices

- Try for new projects
- Customize via vars
- Read template to understand
- Disable features not needed
- Migrate out if outgrow

## Common Mistakes

- Adopt then fight (heavy customization)
- All features (cost, noise)
- Skip understanding template

## Quick Refs

```yaml
include:
  - template: Auto-DevOps.gitlab-ci.yml

variables:
  PRODUCTION_REPLICAS: 3
  CODE_QUALITY_DISABLED: "false"
  POSTGRES_ENABLED: "true"
```

## Interview Prep

**Mid**: "What's Auto DevOps."

**Senior**: "Customize Auto DevOps."

## Next Topic

→ [T04 — Multi-Project Pipelines](T04-Multi-Project-Pipelines.md)
