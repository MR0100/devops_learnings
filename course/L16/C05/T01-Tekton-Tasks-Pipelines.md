# L16/C05/T01 — Tekton: Tasks, Pipelines, PipelineRuns

## Learning Objectives

- Use Tekton on K8s
- Build CI as CRDs

## Tekton

K8s-native CI:
- CRD-based
- Pods run jobs
- Composable
- No central server

For: K8s-first CI.

## Components

### Task
Sequence of steps:
```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build
spec:
  params:
    - name: image
  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      script: |
        /kaniko/executor --destination $(params.image)
```

### Pipeline
Compose tasks:
```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci
spec:
  params:
    - name: repo
    - name: image
  tasks:
    - name: clone
      taskRef:
        name: git-clone
      params:
        - name: url
          value: $(params.repo)
    - name: build
      taskRef:
        name: build
      runAfter: [clone]
      params:
        - name: image
          value: $(params.image)
```

### PipelineRun
Execution:
```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  name: ci-run-1
spec:
  pipelineRef:
    name: ci
  params:
    - name: repo
      value: https://github.com/me/repo
    - name: image
      value: registry/myapp:v1
```

## Install

```bash
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
```

## CLI

```bash
tkn pipeline list
tkn pipelinerun list
tkn pipelinerun logs ci-run-1
tkn pipeline start ci -p repo=... -p image=...
```

## Workspaces

Shared storage between tasks:
```yaml
spec:
  workspaces:
    - name: source
  tasks:
    - name: clone
      workspaces:
        - name: output
          workspace: source
    - name: build
      workspaces:
        - name: source
          workspace: source
```

PVC or emptyDir.

## Results

Tasks produce outputs:
```yaml
spec:
  results:
    - name: version
  steps:
    - script: |
        echo "1.0.0" > $(results.version.path)
```

Consume:
```yaml
- name: deploy
  params:
    - name: version
      value: $(tasks.build.results.version)
```

## When/Conditions

```yaml
- name: deploy-prod
  when:
    - input: $(params.branch)
      operator: in
      values: [main]
  taskRef: ...
```

## Triggers

EventListener watches:
- Webhooks (GitHub, GitLab)
- Custom triggers

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github
spec:
  triggers:
    - name: github-push
      interceptors:
        - ref:
            name: github
          params:
            - name: secretRef
              value:
                secretName: github-secret
                secretKey: token
      bindings:
        - ref: github-binding
      template:
        ref: ci-template
```

## Catalog

Tekton Hub: pre-built tasks:
- git-clone
- kaniko build
- pytest
- helm-deploy

```bash
tkn hub install task git-clone
```

## Pipelines Catalog

Pre-built pipelines.

## Dashboard

```bash
kubectl apply -f https://storage.googleapis.com/tekton-releases/dashboard/latest/release.yaml
```

Web UI.

## Pros

- K8s-native
- Highly composable
- Pod-based isolation
- Open source
- Multi-cloud

## Cons

- Verbose YAML
- Learning curve
- K8s-only
- Less polished UI

## When Tekton

- K8s-first
- Want CI on same cluster as deploys
- Custom CI logic
- No external CI dependency

## When Not

- Non-K8s
- Simpler tools work
- Less ops capacity

## OpenShift Pipelines

OpenShift bundle of Tekton.

## Tekton Chains

Sign artifacts; SLSA provenance:
- Attach attestations
- Cosign integration

For: supply chain.

## Best Practices

- Use catalog tasks
- Workspaces for shared data
- Results for pass values
- Triggers for events
- Chains for security

## Common Mistakes

- All custom tasks (catalog ignored)
- No workspaces (lose data)
- Forget cleanup (PipelineRuns pile up)
- Run dashboard publicly

## Cleanup

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
spec:
  pipelineSpec: ...
  # PipelineRuns auto-prune via:
```

```yaml
# Operator config
spec:
  pruner:
    keep: 100
    schedule: '0 0 * * *'
```

## Quick Refs

```yaml
# Task
kind: Task
spec:
  params: [...]
  steps: [...]
  results: [...]

# Pipeline
kind: Pipeline
spec:
  tasks: [...]

# PipelineRun
kind: PipelineRun
spec:
  pipelineRef: ...
  params: [...]
```

```bash
tkn task / pipeline / pipelinerun
```

## Interview Prep

**Mid**: "What's Tekton."

**Senior**: "Tekton vs GitHub Actions."

**Staff**: "K8s-native CI."

## Next Topic

→ [T02 — Cloud-Native CI on K8s](T02-K8s-Native-CI.md)
