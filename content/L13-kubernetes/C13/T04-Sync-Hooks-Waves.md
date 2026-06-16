# L13/C13/T04 — Sync Strategies, Hooks, Waves

## Learning Objectives

- Use sync hooks
- Order resources with waves

## Sync Strategies

### Manual
User triggers via UI / CLI:
```yaml
syncPolicy: {}    # nothing automated
```

### Automated
ArgoCD syncs on Git change:
```yaml
syncPolicy:
  automated:
    prune: true       # delete removed
    selfHeal: true    # revert manual changes
```

### Automated + Manual Overrides
Sometimes auto; sometimes pause:
```bash
argocd app set my-app --sync-policy none
# ... do manual work
argocd app set my-app --sync-policy automated
```

## Sync Options

```yaml
syncOptions:
- CreateNamespace=true
- PrunePropagationPolicy=foreground
- PruneLast=true
- ApplyOutOfSyncOnly=true
- ServerSideApply=true
- Validate=false
- RespectIgnoreDifferences=true
```

Per app sync behavior.

### CreateNamespace
Create namespace if missing.

### PruneLast
Prune (delete) after other resources synced.

### ServerSideApply
Use K8s server-side apply (3-way merge by field ownership).

### Validate
Server-side validation before apply.

## Sync Hooks

Resources annotated as hooks; run at specific phases:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
```

## Hook Phases

- **PreSync**: before main sync
- **Sync**: during main sync
- **PostSync**: after main sync
- **SyncFail**: if sync fails

## Hook Delete Policies

- **HookSucceeded**: delete if hook succeeded
- **HookFailed**: delete if hook failed
- **BeforeHookCreation**: delete previous before creating new

## Use Cases

### DB Migration (PreSync)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: my-app:v1
        command: ['./migrate']
      restartPolicy: Never
```

Migrate DB before deploying new app version.

### Smoke Test (PostSync)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  annotations:
    argocd.argoproj.io/hook: PostSync
spec:
  template:
    spec:
      containers:
      - name: test
        image: smoke-tester
        command: ['./test.sh']
      restartPolicy: Never
```

Validate deploy after sync.

### Cleanup on Fail (SyncFail)
```yaml
annotations:
  argocd.argoproj.io/hook: SyncFail
```

Notify, revert config, etc.

## Sync Waves

Order resources within Sync phase:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
```

Lower wave number = earlier.

Default: 0.

## Example Order

```yaml
# Wave -2: CRDs
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-2"
kind: CustomResourceDefinition

# Wave -1: Namespace, ConfigMaps, Secrets
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"

# Wave 0: Default for everything
kind: Deployment
kind: Service

# Wave 1: Ingress (after Service ready)
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
kind: Ingress
```

For: dependencies.

## Resource Hooks vs Wave Within Sync

- Hooks: lifecycle phases (PreSync, PostSync, etc.)
- Waves: order within Sync phase

Combined:
- PreSync hook with wave 1
- PreSync hook with wave 2 (runs after wave 1)

For sequenced setup.

## Pruning

Delete resources removed from Git:
```yaml
syncPolicy:
  automated:
    prune: true
```

Without: orphans accumulate.

Per-resource prevent prune:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-options: Prune=false
```

For: critical resources you don't want auto-removed.

## SelfHeal

Revert manual changes:
```yaml
selfHeal: true
```

Without: drift between Git and cluster.

## Skip Validation

```yaml
syncOptions:
- Validate=false
```

For: rare cases (CRD not yet installed).

## Compare Options

```yaml
ignoreDifferences:
- group: apps
  kind: Deployment
  jsonPointers:
  - /spec/replicas
```

ArgoCD won't flag `spec.replicas` difference (HPA manages).

Standard for HPA-managed Deployments.

## Health Checks

Per resource:
```yaml
spec:
  ignoreDifferences:
  - group: apps
    kind: Deployment
    name: my-app
    jsonPointers:
    - /spec/replicas
```

For CRDs: custom Lua scripts.

## Retry

Automatic retry on sync failure:
```yaml
syncPolicy:
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

Exponential backoff.

## Phases Visually

```
PreSync hooks (in wave order)
  ↓
Sync (resources in wave order)
  ↓
PostSync hooks (in wave order)
```

If any fail: SyncFail hooks run.

## Use Case: Microservice Deploy

```yaml
# Wave -1: ConfigMap, Secret
# Wave 0: Deployment, Service
# Wave 1: Ingress
# PreSync hook: DB migration Job
# PostSync hook: smoke test Job
```

Migration runs first; then app deploys with new schema; ingress updates; smoke tests confirm.

## Use Case: Operator Install

```yaml
# Wave -2: CRDs
# Wave -1: RBAC, ServiceAccount
# Wave 0: Operator Deployment
# Wave 1: Custom Resources
```

Operator must be running before CRs.

## Best Practices

- Waves for dependencies
- PreSync hooks for prereqs
- PostSync hooks for validation
- ignoreDifferences for HPA-managed
- prune + selfHeal for production
- Test sync in non-prod first

## Common Mistakes

- All wave 0 (no ordering)
- Hook without delete policy (accumulates)
- prune off (orphans)
- selfHeal on critical Workshop without consideration
- Hook job not idempotent (re-runs cause issues)

## Hook Job Best Practices

- Idempotent (re-run OK)
- Quick (<5 min)
- Logs visible
- Resources sized
- Failure handling

## Cluster Reset

```bash
argocd app sync my-app --force
```

Force apply (skip cache).

```bash
argocd app sync my-app --replace
```

Replace resources (vs patch).

For: stuck state.

## Operations

```bash
# Sync with options
argocd app sync my-app --prune --strategy hook

# Selective sync
argocd app sync my-app --resource apps:Deployment:my-app

# Wait for healthy
argocd app wait my-app --health --sync
```

## Quick Refs

```yaml
# Sync policy
syncPolicy:
  automated:
    prune: true
    selfHeal: true
  syncOptions:
  - CreateNamespace=true
  - ServerSideApply=true

# Hook
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation

# Wave
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
```

## Interview Prep

**Mid**: "Sync hooks."

**Senior**: "Wave ordering for operator."

**Staff**: "GitOps deploy strategy with migrations."

## Next Topic

→ Move to [L13/C14 — Observability in K8s](../C14/README.md)
