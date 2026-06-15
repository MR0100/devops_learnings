# L16/C05/T02 — Cloud-Native CI on K8s

## Learning Objectives

- Run CI on K8s
- Compare patterns

## Why K8s-Native CI

- Reuse K8s infra
- Auto-scale CI
- Same cluster as production
- No external CI service

## Tekton

Primary choice (covered).

## Argo Workflows

K8s-native workflow engine:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: ci-
spec:
  entrypoint: pipeline
  templates:
    - name: pipeline
      dag:
        tasks:
          - name: build
            template: build-task
          - name: test
            dependencies: [build]
            template: test-task

    - name: build-task
      container:
        image: builder
        command: [build.sh]
```

For: more general workflow (not just CI).

## Argo Events

Triggers:
- Webhook
- S3 event
- Kafka
- Cron

```yaml
apiVersion: argoproj.io/v1alpha1
kind: EventSource
metadata:
  name: github
spec:
  github:
    push:
      events: [push]
```

## Choose

| | Tekton | Argo Workflows |
|---|---|---|
| Focus | CI/CD | General workflow |
| Steps | Pods | Pods |
| Composition | Tasks → Pipelines | Templates → DAG |
| Triggers | EventListener | Argo Events |
| Maturity | High | High |

For pure CI: Tekton.
For ML / data: Argo Workflows.

## Comparison to External CI

| | K8s-native | External (GitHub Actions) |
|---|---|---|
| Where | K8s cluster | SaaS |
| Cost | Cluster | Per-min |
| Maintenance | You | Vendor |
| Speed | Cluster-dependent | Fast (pre-warmed) |
| Integration | K8s tight | Repo tight |
| K8s deploys | Same cluster | External |

## Hybrid

GitHub Actions:
- Source control trigger
- Run light tests
- Tekton handles deploy + integration

For: best of both.

## CI Workload Patterns

### Build in K8s
Kaniko / BuildKit pod:
```yaml
- name: build
  container:
    image: gcr.io/kaniko-project/executor
    command: [/kaniko/executor]
    args: [--destination, registry/app:v1]
```

### Test in K8s
Pod runs test framework.

### Deploy in K8s
kubectl / Helm in pod.

## Storage

PVC for shared workspace:
```yaml
workspaces:
  - name: source
    persistentVolumeClaim:
      claimName: ci-workspace
```

Or emptyDir per Pipeline.

## Secrets

```yaml
- secret:
    secretName: registry-creds
```

K8s secrets mounted.

## Auth

ServiceAccount:
```yaml
spec:
  serviceAccountName: ci-sa
```

RBAC for what CI can do.

## Network Policies

Restrict CI pods:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  podSelector:
    matchLabels:
      ci: tekton
  egress:
    - to:
        - namespaceSelector: ...
```

For: limit blast radius.

## Resource Limits

```yaml
spec:
  resources:
    requests: { cpu: 1, memory: 2Gi }
    limits: { cpu: 4, memory: 8Gi }
```

## Auto-Scaling CI

HPA on Tekton controller; Karpenter for nodes.

CI bursts: scale.
Idle: scale down.

## Best Practices

- Namespace isolation
- RBAC strict
- NetworkPolicy
- Resource limits
- Cleanup old PipelineRuns
- Monitor CI cluster usage

## Common Mistakes

- Same cluster as prod (security risk)
- No cleanup (storage bloat)
- Wide RBAC
- No resource limits (DoS cluster)
- Cluster-admin in CI

## Separate Cluster

For prod safety:
- CI cluster separate from prod
- Deploys reach prod via API
- Blast radius limited

For: best practice.

## Monitoring

```bash
kubectl top pods -n tekton-pipelines
```

Prometheus:
- Pipeline durations
- Failure rate
- Resource usage

## When K8s-Native CI

- K8s-heavy org
- Want infra consistency
- Strong K8s ops
- Cost (large CI)

## When External

- Smaller team
- Less K8s ops
- Want polish
- Multi-platform builds (mac, windows)

## Real Examples

- Many enterprises with K8s use Tekton
- Argo Workflows in ML / data engineering

## Quick Refs

```yaml
# Tekton
kind: Task / Pipeline / PipelineRun

# Argo Workflows
kind: Workflow / EventSource / Sensor
```

## Interview Prep

**Mid**: "K8s-native CI."

**Senior**: "Tekton vs external."

**Staff**: "CI platform strategy."

## Next Topic

→ Move to [L16/C06 — ArgoCD](../C06/README.md)
