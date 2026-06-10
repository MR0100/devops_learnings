# L13/C09/T01 — Init Containers

## Learning Objectives

- Use init containers for prerequisites
- Order container startup

## Init Containers

Special containers running before app containers:
- Sequential (one after another)
- Each must succeed before next
- App containers only start after all init succeed

```yaml
spec:
  initContainers:
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 'until nc -z db 5432; do echo waiting; sleep 2; done']
  - name: migrate-db
    image: my-migrator:v1
    command: ['./migrate']
  containers:
  - name: app
    image: my-app:v1
```

Order: wait-for-db → migrate-db → app.

## Use Cases

### Wait for Dependencies
```yaml
- name: wait-for-redis
  image: busybox
  command: ['sh', '-c', 'until nc -z redis 6379; do sleep 1; done']
```

### Schema Migrations
```yaml
- name: migrate
  image: liquibase
  command: ['liquibase', 'update']
```

App runs after schema ready.

### Fetch Secrets
```yaml
- name: fetch-secrets
  image: vault-agent
  command: ['vault', 'agent', '-config=...']
```

Writes to shared volume.

### Generate Configuration
```yaml
- name: render-config
  image: gomplate
  command: ['gomplate', '-f', '/templates/config.tpl', '-o', '/config/app.yaml']
```

### Permission Setup
```yaml
- name: chown-data
  image: busybox
  command: ['chown', '-R', '1000:1000', '/data']
  securityContext:
    runAsUser: 0   # need root
  volumeMounts:
  - name: data
    mountPath: /data
```

For: shared volume needs specific ownership.

## Resources

Init containers have resources too:
```yaml
initContainers:
- name: init
  image: ...
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
```

Pod's effective request = max(init request) OR sum(app request), per resource.

## Sequential

Init runs in order:
- init1 → init2 → init3 → app

Each must exit 0.

For parallel: init not the tool; consider design.

## Restart Behavior

Init container failure:
- Restart per restartPolicy
- OnFailure / Always: retried
- Never: pod marked Failed

If first init never succeeds: pod stuck.

## Visibility

```bash
kubectl get pods
# my-pod   0/1   Init:1/3   0   30s
```

Init:N/M shows progress.

```bash
kubectl logs my-pod -c <init-name>
```

For: debug init.

## Status

```bash
kubectl describe pod my-pod
# Init Containers:
#   wait-for-db: completed
#   migrate-db: completed
# Containers:
#   app: running
```

## Sidecars vs Init

| | Init | Sidecar |
|---|---|---|
| Lifecycle | Before app | With app |
| Restart | If fails | If crashes |
| Purpose | Setup | Companion |

Both: same pod; share volumes.

Modern sidecar (1.28+): init container with `restartPolicy: Always` becomes a sidecar (covered T02).

## Common Patterns

### CNI Plugins
Some CNIs use init container to set up networking before app.

### Permission Fix
Volume mounted with wrong perms; init fixes.

### Wait for Service
External Service must be ready; init polls.

### Cache Warm
Pre-load cache from DB before app serves.

## Don't Use For

- Long-running tasks (use Job or sidecar)
- Replacement for init system (use proper)
- Application logic (use app)

## Failures

```bash
kubectl logs my-pod -c init-1 --previous
```

Common causes:
- Network can't reach (dependency)
- Permission denied
- Image pull error
- Command not found

## Init + Volumes

Init writes; app reads:
```yaml
initContainers:
- name: render
  volumeMounts:
  - name: config
    mountPath: /config

containers:
- name: app
  volumeMounts:
  - name: config
    mountPath: /etc/config

volumes:
- name: config
  emptyDir: {}
```

emptyDir shared.

## Init for Migrations

```yaml
initContainers:
- name: db-migrate
  image: my-app:v1
  command: ['./manage.py', 'migrate']
  env:
  - name: DATABASE_URL
    valueFrom: ...
```

Each pod runs migration. Issue: parallel pods race.

Better: separate Job runs migration once; pods wait via initContainer:
```yaml
initContainers:
- name: wait-for-migration
  command: ['sh', '-c', 'until kubectl get job/migrate-job -o jsonpath="{.status.succeeded}" | grep -q 1; do sleep 5; done']
```

For: avoid race.

## Init Container Pull

Image pulled like app containers. Cached on node.

For: minimize size; use thin image (busybox, alpine).

## Multiple Init

```yaml
initContainers:
- name: step1
  ...
- name: step2
  ...
- name: step3
  ...
```

Each waits for previous.

For: complex multi-step setup.

## Performance

Each init = pod start delay. Minimize:
- Small images
- Fast commands
- Parallel where possible (separate containers wait via app)

## Best Practices

- Idempotent (re-runs OK)
- Quick (<30s ideal)
- Logs to stdout
- Specific image (not full app)
- Resources defined
- Document why each

## Common Mistakes

- Heavy app image as init (slow pull)
- No timeout (hangs)
- Privileged when not needed
- Same image as app but different command (waste)
- Long-running init (blocks pod start)

## Pod Startup Time

```
Image pull + Init 1 + Init 2 + ... + App start
```

For latency-critical: limit init.

## Inspection

```bash
# Pod status
kubectl get pod my-pod

# Init container logs
kubectl logs my-pod -c init-name

# Describe
kubectl describe pod my-pod

# Previous (if crashed)
kubectl logs my-pod -c init-name --previous
```

## When NOT Init

- Continuous task (sidecar)
- Setup that takes minutes (separate Job)
- Doesn't need to block app (consider sidecar)

## Quick Refs

```yaml
spec:
  initContainers:
  - name: init-x
    image: busybox
    command: ['sh', '-c', 'until ...; do sleep 1; done']
    volumeMounts: ...
  containers:
  - name: app
    image: my-app
    volumeMounts: ...
```

## Interview Prep

**Junior**: "What's an init container."

**Mid**: "When use init vs sidecar."

**Senior**: "Multi-stage init pattern."

## Next Topic

→ [T02 — Sidecars](T02-Sidecars.md)
