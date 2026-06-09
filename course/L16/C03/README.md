# L16/C03 — GitLab CI

## Topics

- **T01 .gitlab-ci.yml Anatomy** — YAML config; stages, jobs, scripts.
- **T02 Runners** — Shared (GitLab.com) or self-hosted; Docker, Shell, K8s executors.
- **T03 Auto DevOps** — Opinionated pipelines auto-discovered (build, test, deploy).
- **T04 Multi-Project Pipelines** — Trigger downstream pipelines in other projects.

## Anatomy

```yaml
stages: [build, test, deploy]

variables:
  REGISTRY: registry.gitlab.com

build:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  script:
    - docker build -t $REGISTRY/$CI_PROJECT_PATH:$CI_COMMIT_SHA .
    - docker push $REGISTRY/$CI_PROJECT_PATH:$CI_COMMIT_SHA
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

test:
  stage: test
  image: golang:1.22
  script: go test ./...
  coverage: '/coverage: \d+\.\d+/'

deploy:prod:
  stage: deploy
  image: bitnami/kubectl
  script:
    - kubectl set image deploy/app app=$REGISTRY/$CI_PROJECT_PATH:$CI_COMMIT_SHA
  environment:
    name: production
    url: https://prod.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
```

## Predefined Variables

```
CI_COMMIT_SHA
CI_COMMIT_REF_NAME
CI_PIPELINE_ID
CI_PROJECT_PATH
CI_DEFAULT_BRANCH
CI_REGISTRY_USER, CI_REGISTRY_PASSWORD
```

## Rules vs Only/Except

Modern uses `rules`:
```yaml
rules:
  - if: $CI_COMMIT_BRANCH == "main"
    when: always
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    when: always
  - when: never
```

## Runners

### Executors
- **Docker** (most common)
- **Shell**
- **Kubernetes** (per-job pod)
- **Docker Machine** (auto-scaling)

### Self-Hosted on K8s
```yaml
runners:
  config: |
    [[runners]]
      [runners.kubernetes]
        namespace = "gitlab-runners"
        cpu_limit = "1"
        memory_limit = "2Gi"
```

Each job = ephemeral pod.

## Includes & Templates

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - project: 'myorg/ci-templates'
    file: '/build.yml'
    ref: main
```

## Auto DevOps

GitLab analyzes repo; runs build/test/deploy via Auto DevOps templates. Useful for teams without CI expertise; less control.

## Multi-Project Pipelines

```yaml
trigger-downstream:
  trigger:
    project: other/repo
    branch: main
    strategy: depend          # wait for it
```

## When GitLab CI

- Already on GitLab (Git + CI in one)
- Want OSS option (self-hostable)
- Pages + Container Registry + CI bundled
- Tight integration with merge requests

## Interview Themes

- "Walk me through .gitlab-ci.yml"
- "GitLab CI vs GitHub Actions"
- "Runners — Docker vs K8s executor"
- "Multi-project pipelines"
