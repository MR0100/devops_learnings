# L16/C06/T02 — Sync Hooks & Waves

## Learning Objectives

- Order ArgoCD syncs
- Use hooks for migrations

## Sync Wave

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

Lower numbers first. Negative OK.

## Example

```yaml
# CRDs first
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-2"

# Operators
argocd.argoproj.io/sync-wave: "-1"

# App resources
argocd.argoproj.io/sync-wave: "0"

# Tests
argocd.argoproj.io/sync-wave: "1"
```

For: dependency ordering.

## Hooks

Run at specific phase:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
```

## Hook Types

### PreSync
Before main sync. For: migrations, backups.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: migration
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: myapp:latest
        command: [migrate-db]
      restartPolicy: Never
```

### Sync
Main phase. Default.

### PostSync
After sync. For: smoke tests, notifications.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  annotations:
    argocd.argoproj.io/hook: PostSync
spec:
  template:
    spec:
      containers:
      - name: smoke
        image: smoke-tester
```

### SyncFail
On failure. For: cleanup.

### PostDelete
After app delete.

## Delete Policy

```yaml
argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
```

Options:
- HookSucceeded: delete after success
- HookFailed: delete after fail
- BeforeHookCreation: delete before next run

## Resource Ordering Without Wave

ArgoCD applies in this order:
1. Namespaces
2. CRDs
3. Other resources

Waves override.

## Health Checks

ArgoCD waits for resource Health = Healthy.

Built-in checks for:
- Deployment (ready replicas)
- StatefulSet
- DaemonSet
- Service
- Job (succeeded)

Custom (Lua):
```lua
hs = {}
if obj.status ~= nil then
  if obj.status.phase == "Running" then
    hs.status = "Healthy"
  end
end
return hs
```

## Sync Ordering Example

App with DB migration:
```yaml
# Job: migrate before app
argocd.argoproj.io/hook: PreSync

# Deployment: in main sync, wave 0
# (no annotation, default)

# Job: smoke test after
argocd.argoproj.io/hook: PostSync
```

Migration runs first.
Then deployment.
Then smoke test.

## Sync Options

```yaml
syncPolicy:
  syncOptions:
  - CreateNamespace=true
  - ServerSideApply=true
  - SkipDryRunOnMissingResource=true
  - PrunePropagationPolicy=foreground
```

## CreateNamespace

ArgoCD creates target namespace if missing.

## ServerSideApply

K8s server-side apply (instead of client).
For: fewer conflicts.

## Replace

```yaml
syncOptions:
- Replace=true
```

`kubectl replace` instead of apply.
For: certain resources (deprecate).

## Selective Sync

```bash
argocd app sync myapp --resource Deployment:nginx
```

Sync specific resource only.

## Sync Status

```bash
argocd app get myapp
```

Shows:
- Synced (Git == cluster)
- OutOfSync (drift)
- Unknown (problem)

Plus Health (resources healthy).

## Diff

```bash
argocd app diff myapp
```

Show cluster vs Git.

## Retries

```yaml
syncPolicy:
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

## Best Practices

- Wave CRDs before usage
- PreSync for DB migration
- PostSync for smoke
- Delete policies prevent stale Jobs
- Health checks tight

## Common Mistakes

- Wrong wave order (resources missing)
- Missing delete policy (Jobs accumulate)
- Hook fails → sync fails (consider)
- Long-running hooks (timeout)

## Migration Pattern

```yaml
# 1. Backup (PreSync wave -1)
# 2. Migrate DB (PreSync wave 0)
# 3. App deploy (Sync)
# 4. Smoke test (PostSync wave 1)
# 5. Notify (PostSync wave 2)
```

## Quick Refs

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
    argocd.argoproj.io/hook: PreSync | Sync | PostSync | SyncFail | PostDelete
    argocd.argoproj.io/hook-delete-policy: HookSucceeded | HookFailed | BeforeHookCreation
```

## Interview Prep

**Mid**: "Hooks vs waves."

**Senior**: "DB migration GitOps."

**Staff**: "Sync orchestration."

## Next Topic

→ Move to [L16/C07 — Flux v2](../C07/README.md)
