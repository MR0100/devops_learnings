# L16/C03/T01 — .gitlab-ci.yml Anatomy

## Learning Objectives

- Write GitLab CI
- Use core features

## Sample

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  IMAGE: registry.example.com/myapp

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $IMAGE:$CI_COMMIT_SHA .
    - docker push $IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - pytest

deploy:
  stage: deploy
  script:
    - kubectl set image deploy/myapp myapp=$IMAGE:$CI_COMMIT_SHA
  only:
    - main
```

## Stages

```yaml
stages:
  - build
  - test
  - deploy
```

Jobs in same stage: parallel.
Jobs in next stage: wait for prev.

## Jobs

Each top-level key is a job:
```yaml
job_name:
  stage: build
  script:
    - command
```

## Script

```yaml
script:
  - echo "Hello"
  - make build
  - make test
```

## Image

```yaml
test:
  image: python:3.12
  script: ...
```

## Services

Like sidecar:
```yaml
test:
  image: python
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_PASSWORD: pass
```

For: integration tests with deps.

## Variables

```yaml
variables:
  GLOBAL_VAR: value

job:
  variables:
    JOB_VAR: value
```

Use:
```yaml
script:
  - echo $GLOBAL_VAR
```

## Rules

```yaml
deploy:
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: on_success
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: never
```

For: conditional.

## Only / Except (Legacy)

```yaml
deploy:
  only:
    - main
    - /^release\/.*$/
  except:
    - tags
```

For: branch filter. `rules` is modern.

## Cache

```yaml
job:
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
```

## Artifacts

```yaml
build:
  script:
    - make build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

Downstream jobs receive automatically.

## Dependencies

```yaml
deploy:
  dependencies:
    - build   # only this artifact, not all
  script: ...
```

## Needs (DAG)

```yaml
job_c:
  needs: [job_a]
  # Runs as soon as job_a done, regardless of stage
```

For: skip waiting for stage barrier.

## Manual Jobs

```yaml
deploy_prod:
  script: ...
  when: manual
  allow_failure: false
```

UI: button to trigger.

## Approval Required

```yaml
deploy_prod:
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
```

## Environments

```yaml
deploy_staging:
  stage: deploy
  script: ...
  environment:
    name: staging
    url: https://staging.example.com
```

Tracks deployments per env.

## Auto-Stop

```yaml
deploy_review:
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_COMMIT_REF_SLUG.example.com
    on_stop: stop_review

stop_review:
  script: ./stop.sh
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  when: manual
```

For: review apps.

## Include

```yaml
include:
  - local: '.gitlab/ci/build.yml'
  - project: 'org/templates'
    file: 'common.yml'
  - remote: 'https://example.com/ci.yml'
  - template: 'Auto-DevOps.gitlab-ci.yml'
```

For: composition.

## Extends

```yaml
.base:
  image: python
  before_script:
    - pip install -r requirements.txt

test_unit:
  extends: .base
  script: pytest tests/unit

test_int:
  extends: .base
  script: pytest tests/integration
```

For: shared config.

## Anchor (YAML)

```yaml
.default: &default
  image: python
  retry: 2

test:
  <<: *default
  script: ...
```

For: YAML-native reuse.

## Parallel

```yaml
test:
  parallel: 5   # run 5 instances
  script: ./run-tests.sh $CI_NODE_INDEX
```

For: sharding.

## Matrix

```yaml
test:
  parallel:
    matrix:
      - OS: [ubuntu, alpine]
        VERSION: ['3.10', '3.11']
  script: ...
```

## Workflow

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
```

Whole-pipeline conditions.

## CI Lint

```bash
# Validate
gitlab-runner exec docker job_name
```

Or GitLab UI: CI/CD → Pipelines → Editor → Validate.

## Secrets

```yaml
job:
  script:
    - echo $SECRET_KEY
```

Stored in: Settings → CI/CD → Variables.
Mark: Masked, Protected.

## Predefined Variables

- `$CI_COMMIT_SHA`
- `$CI_COMMIT_BRANCH`
- `$CI_PIPELINE_ID`
- `$CI_JOB_NAME`
- `$GITLAB_USER_EMAIL`
- many more

## Best Practices

- DAG with needs (faster)
- Cache deps
- Artifacts between stages
- Include shared
- Environments + auto-stop
- Manual gates prod

## Common Mistakes

- Sequential when DAG possible
- No cache
- Secrets not masked
- Globally-applied rules

## Quick Refs

```yaml
stages: [...]
variables: {...}
include: [...]

job:
  stage: ...
  image: ...
  script: [...]
  rules: [...]
  cache: {...}
  artifacts: {...}
  needs: [...]
  environment: {...}
```

## Interview Prep

**Junior**: "GitLab CI basics."

**Mid**: "Rules vs only/except."

**Senior**: "DAG with needs."

## Next Topic

→ [T02 — Runners](T02-Gitlab-Runners.md)
