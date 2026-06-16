# L16/C05 — Tekton

## Topics

- **T01 Tasks, Pipelines, PipelineRuns** — Tekton is Kubernetes-native CI built on CRDs.
- **T02 Cloud-Native CI on K8s** — Runs entirely in K8s; each step a container.

## Concepts

- **Task**: a sequence of steps (containers)
- **Pipeline**: composition of tasks (DAG)
- **TaskRun**: an instance of a Task running
- **PipelineRun**: an instance of a Pipeline running
- **Workspace**: shared volume between tasks
- **Triggers**: webhook → PipelineRun

## Sample Task

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-image
spec:
  params:
    - name: imageUrl
      type: string
  workspaces:
    - name: source
  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      args:
        - --context=$(workspaces.source.path)
        - --destination=$(params.imageUrl)
        - --cache=true
```

## Pipeline

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci
spec:
  workspaces:
    - name: shared
  params:
    - name: imageUrl
  tasks:
    - name: clone
      taskRef: { name: git-clone }
      workspaces:
        - name: output
          workspace: shared
    - name: test
      taskRef: { name: go-test }
      runAfter: [clone]
      workspaces:
        - name: source
          workspace: shared
    - name: build
      taskRef: { name: build-image }
      runAfter: [test]
      params:
        - { name: imageUrl, value: $(params.imageUrl) }
      workspaces:
        - name: source
          workspace: shared
```

## PipelineRun

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: ci-run-
spec:
  pipelineRef: { name: ci }
  params:
    - { name: imageUrl, value: "ghcr.io/me/app:abc123" }
  workspaces:
    - name: shared
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources: { requests: { storage: 1Gi } }
```

## Why Tekton

- **K8s-native**: managed via CRDs, kubectl
- **Cloud-agnostic**: works on any K8s
- **Reusable Tasks**: Tekton Hub for community tasks
- **Composable**: build pipelines from tasks

## Why Not Tekton

- No native UI (use Dashboard or Tekton Results)
- Less polished than GitHub Actions UX
- Requires K8s
- Smaller community than mainstream CI

## Triggers (Webhook → Pipeline)

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
spec:
  triggers:
    - bindings:
        - ref: github-binding
      template:
        ref: github-pipeline-template
```

Exposed via Ingress; GitHub webhook posts; PipelineRun starts.

## When Tekton

- All-in K8s
- Want CI as code, K8s-resource-managed
- Building your own CI platform (OpenShift Pipelines is based on Tekton)

## Interview Themes
- "Tekton vs Jenkins"
- "Why K8s-native CI?"
- "Tekton Pipeline composition"
