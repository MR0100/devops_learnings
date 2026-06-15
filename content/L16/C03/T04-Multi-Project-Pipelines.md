# L16/C03/T04 — Multi-Project Pipelines

## Learning Objectives

- Trigger downstream pipelines
- Orchestrate microservices

## Multi-Project Pipeline

Project A triggers Project B's pipeline:
```yaml
# Project A
trigger_project_b:
  stage: deploy
  trigger:
    project: my-group/project-b
    branch: main
    strategy: depend   # wait for it
```

For: microservices coordination.

## Parent-Child Pipeline

Same project; nested:
```yaml
# Parent
trigger_child:
  trigger:
    include:
      - local: '.gitlab/ci/child.yml'
```

For: complex single-project.

## Cross-Project Triggering

Via API:
```bash
curl -X POST -F token=TOKEN -F ref=main \
  https://gitlab.com/api/v4/projects/PROJ/trigger/pipeline
```

Or `trigger:` keyword.

## Variables Pass

```yaml
trigger_downstream:
  trigger:
    project: my-group/downstream
  variables:
    UPSTREAM_VERSION: $CI_COMMIT_SHA
```

Downstream gets variable.

## Strategy

- `strategy: depend`: wait for downstream
- (default): fire-and-forget

For sync: depend.

## Dynamic Child Pipelines

```yaml
# Parent
generate:
  script:
    - ./generate-ci.sh > generated.yml
  artifacts:
    paths:
      - generated.yml

trigger:
  trigger:
    include:
      - artifact: generated.yml
        job: generate
```

For: pipeline determined at runtime.

## Use Cases

### Microservices Coordination
Service A deploys → triggers B.

### Library Publish
Library changes → trigger consumer projects.

### Monorepo (Detect Changed)
Detect changed services → trigger child pipeline per service.

## Microservices Example

```yaml
# Library repo CI
publish:
  script: npm publish
  trigger:
    project: my-group/consumer
    branch: main
    variables:
      LIBRARY_VERSION: $VERSION
```

Consumer rebuilds + tests.

## Monorepo Example

```yaml
# Parent
generate_child_pipelines:
  script:
    - ./detect-changed.sh   # outputs YAML per service
  artifacts:
    paths:
      - generated/*.yml

trigger_services:
  needs: [generate_child_pipelines]
  parallel:
    matrix:
      - SERVICE: [api, web, worker]
  trigger:
    include:
      - artifact: generated/${SERVICE}.yml
        job: generate_child_pipelines
```

## Visualization

GitLab UI shows:
- Parent pipeline
- Child pipelines linked
- Status of each

## Cross-Pipeline Variables

```
UPSTREAM_CI_PIPELINE_ID
UPSTREAM_CI_PROJECT_NAME
UPSTREAM_CI_PROJECT_URL
```

Downstream knows upstream.

## Resource Locks

```yaml
deploy:
  resource_group: production-deploy
  script: deploy.sh
```

Only one job at a time in same resource group. Coordinate across projects.

## API Trigger

```yaml
trigger_external:
  script:
    - |
      curl -X POST \
        -F "token=$TRIGGER_TOKEN" \
        -F "ref=main" \
        -F "variables[VERSION]=$VERSION" \
        https://gitlab.com/api/v4/projects/PROJ_ID/trigger/pipeline
```

For: any external trigger.

## Webhooks

GitLab webhook → external service → trigger pipeline.

For: complex orchestration.

## Best Practices

- Use depend for sync requirements
- Pass minimal vars (loose coupling)
- Failure handling
- Test parent + child together
- Avoid cycles

## Common Mistakes

- Fire-and-forget when sync needed
- Tight coupling (downstream depends on upstream internals)
- Cycle (A → B → A)
- No failure propagation

## Failure Handling

```yaml
trigger:
  trigger:
    project: ...
    strategy: depend
  rules:
    - if: ...
  allow_failure: false
```

Parent fails if downstream fails.

## Quick Refs

```yaml
# Trigger
trigger:
  project: GROUP/PROJ
  branch: BRANCH
  strategy: depend
variables:
  X: VALUE

# Child
trigger:
  include:
    - local: .gitlab/ci/child.yml
```

## Interview Prep

**Mid**: "Multi-project pipelines."

**Senior**: "Microservices CI coordination."

**Staff**: "Pipeline orchestration."

## Next Topic

→ Move to [L16/C04 — CircleCI](../C04/README.md)
