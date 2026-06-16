# L15/C06/T01 — Recreate Deployment

## Learning Objectives

- Understand recreate strategy
- Know when to use

## Recreate

Stop all old; start all new:
```
Old: ███ → (stopped)
New:               → ███
```

Downtime during.

## K8s Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  strategy:
    type: Recreate
```

## When

- Single-instance app
- Strict consistency (no two versions live)
- Stateful with strict invariants
- Resource-constrained (can't run double)

## Pros

- Simple
- No two versions interacting
- Resource-efficient
- Clear cutover

## Cons

- Downtime
- All-or-nothing
- Rollback = same recreate

## Examples

### DB Migration
Old version drops table; new uses new schema. Can't coexist.

For: bring down; migrate; bring up.

### License-Limited
One instance only.

### Resource Constrained
Only enough for N pods.

## Alternative

Most apps: use Rolling Update.

For zero-downtime: blue/green or canary.

For: only use recreate when justified.

## Pipeline

```yaml
- name: Stop old
  run: kubectl scale deploy/myapp --replicas=0

- name: Wait
  run: kubectl wait pods -l app=myapp --for=delete --timeout=60s

- name: Deploy new
  run: kubectl set image deploy/myapp myapp=NEWIMAGE

- name: Scale up
  run: kubectl scale deploy/myapp --replicas=3

- name: Wait ready
  run: kubectl rollout status deploy/myapp
```

## Downtime Estimate

- Time to stop: 30 sec - minutes
- Time to start: depends on app

For: 1-5 min typical.

## Pre-Deploy Tasks

```yaml
- name: Migrate DB
  run: kubectl create job migrate --image=migrator:v2

- name: Wait migration
  run: kubectl wait jobs/migrate --for=condition=complete
```

Migrations during downtime.

## Avoid in Modern

For most: rolling is better.

Recreate: special cases.

## State Persistence

App state in:
- DB
- Object storage
- Persistent Volumes

App pod ephemeral; restart fine.

For: most apps.

## Reset State

Recreate: also resets in-memory state.

For: stateful apps in K8s:
- StatefulSet (different concepts)
- Headless Service
- Persistent Volumes

## Rolling Back

Re-apply old image:
```yaml
- run: kubectl rollout undo deploy/myapp
```

For Recreate: same downtime as deploy.

## Best Practices

- Avoid unless needed
- Schedule (maintenance window)
- Migrate during downtime
- Notify users
- Time downtime

## Common Mistakes

- Recreate for stateless (use rolling)
- No notification
- No migration coordination
- Long downtime due to app startup

## Quick Refs

```yaml
spec:
  strategy:
    type: Recreate
```

## Interview Prep

**Junior**: "What's recreate."

**Mid**: "When to use."

**Senior**: "Migration coordination."

## Next Topic

→ [T02 — Rolling Update](T02-Rolling-Update.md)
