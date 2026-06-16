# L13/C03/T01 — ConfigMaps

## Learning Objectives

- Use ConfigMaps for config
- Mount as env or volume

## ConfigMap

KV store for non-sensitive config:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: db.example.com
  database.port: "5432"
  log.level: info
  app.yaml: |
    server:
      port: 8080
    feature:
      flag1: true
```

Up to 1 MiB per ConfigMap.

## Create

```bash
# Literal
kubectl create configmap app-config --from-literal=key=value

# From file
kubectl create configmap app-config --from-file=app.yaml

# From dir
kubectl create configmap app-config --from-file=./config-dir/

# From env file
kubectl create configmap app-config --from-env-file=.env
```

Or YAML (preferred for IaC).

## Consume as Env Var

```yaml
spec:
  containers:
  - name: app
    env:
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
```

Or whole CM as env:
```yaml
envFrom:
- configMapRef:
    name: app-config
```

Each key becomes env var.

## Mount as Volume

```yaml
volumes:
- name: config
  configMap:
    name: app-config

containers:
- name: app
  volumeMounts:
  - name: config
    mountPath: /etc/config
```

Files in /etc/config/:
- /etc/config/database.host
- /etc/config/database.port
- /etc/config/app.yaml

## Specific Files

```yaml
volumes:
- name: config
  configMap:
    name: app-config
    items:
    - key: app.yaml
      path: application.yaml
```

Only `app.yaml` mounted; renamed to `application.yaml`.

## Auto-Update

Volume-mounted: ConfigMap changes propagate to pod (eventually, ~minute):
- Pod sees new files
- App must re-read

Env var: NO auto-update. Pod must restart.

## SubPath

To mount one file:
```yaml
volumeMounts:
- name: config
  mountPath: /etc/myapp/config.yaml
  subPath: app.yaml
```

But: `subPath` mount doesn't auto-update.

For auto-update: mount whole dir.

## Optional

```yaml
envFrom:
- configMapRef:
    name: maybe-config
    optional: true
```

Pod starts even if CM missing.

## Immutable

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
immutable: true
data:
  key: value
```

Can't edit. Must create new + update Deployment.

For: performance (kube-apiserver doesn't watch) + safety (prevent accidental edits).

## Namespace

ConfigMap is namespaced. Pods can only reference CMs in same namespace.

For cross-namespace: copy CM or use ExternalSecrets / similar.

## Size Limit

1 MiB per ConfigMap. For larger:
- Split into multiple CMs
- Mount from PVC

## App Config Patterns

### YAML File
```yaml
# ConfigMap
data:
  app.yaml: |
    server:
      port: 8080
    log:
      level: info
```

Mount as file; app reads.

### Env Vars
```yaml
data:
  LOG_LEVEL: info
  PORT: "8080"
```

Use as envFrom.

### Mix
Some env (for tooling); some files (for apps reading config files).

## Updating

```bash
# Edit live
kubectl edit cm/app-config

# Apply changes
kubectl apply -f app-config.yaml

# Recreate (if immutable)
kubectl delete cm/app-config
kubectl apply -f app-config.yaml
```

For env vars: must restart pods:
```bash
kubectl rollout restart deployment/web
```

For mounted files: app handles (auto-update via volume; ~minute lag).

## Reloader Operator

Watches ConfigMap / Secret; triggers pod restart on change.

Annotation:
```yaml
annotations:
  reloader.stakater.com/auto: "true"
```

When CM updates: rollout restart of pods using it.

For: env vars that need refresh.

## Versioning

Hash ConfigMap content; include in pod template annotation:
```yaml
template:
  metadata:
    annotations:
      configmap-hash: "abc123"
```

Hash change → template change → rollout.

Helm/Kustomize: built-in.

## Helm

```yaml
# Trigger rollout on CM change
spec:
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

## Kustomize

```yaml
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=info
  files:
  - app.yaml
```

Generates CM with hash suffix; updates pods on change.

## Common Mistakes

- Secrets in ConfigMap (use Secret)
- Big files (1 MiB limit)
- Env var without restart strategy
- Subpath mount expecting updates

## Best Practices

- Non-sensitive only
- Mount as files for auto-update
- Env vars for simple
- Immutable for stable config
- Use Helm/Kustomize for hash-based rollout
- Document keys

## Patterns

### Per-Environment
```yaml
# dev-config.yaml
metadata:
  name: app-config
data:
  log.level: debug

# prod-config.yaml
metadata:
  name: app-config
data:
  log.level: info
```

Same name; per-env CM. Pod refers by name; works in either env.

### Feature Flags
```yaml
data:
  features.yaml: |
    enable_new_ui: true
    enable_beta: false
```

App reads; toggle features.

For real feature flags: LaunchDarkly, GrowthBook (better tooling).

### Logging Config
```yaml
data:
  log4j.properties: |
    log4j.rootLogger=INFO
    log4j.appender.stdout=org.apache.log4j.ConsoleAppender
```

Java apps read /etc/config/log4j.properties.

## Operators

```bash
# List
kubectl get configmap

# Describe
kubectl describe cm/app-config

# YAML
kubectl get cm/app-config -o yaml

# Get specific value
kubectl get cm/app-config -o jsonpath='{.data.log\.level}'

# Delete
kubectl delete cm/app-config
```

## Hot Reload

App can watch /etc/config/ for changes:
```python
from watchdog.observers import Observer

class ConfigHandler:
    def on_modified(self, event):
        if event.src_path == '/etc/config/app.yaml':
            reload_config()
```

Or polling every N seconds.

## Limits

- 1 MiB per CM
- N CMs per namespace: depends on etcd
- Pod can reference many CMs

For huge config: split or move to PVC.

## Configuration Strategy

Layers:
- Defaults (in image)
- Per-env CM (env vars)
- Per-pod env (rare; via downward API)
- Runtime (database, dynamic)

CM for env-specific config that's static.

## Common Anti-Patterns

- Same CM for many apps (coupled)
- All env vars (file better for structured)
- No versioning (deploy diff)
- Plaintext secrets

## When Secret vs CM

| | ConfigMap | Secret |
|---|---|---|
| Sensitive | No | Yes |
| Encoding | Plain | Base64 |
| Encryption at rest | Optional | Recommended |
| Mount | Same | Same |
| Use | Config | Passwords, keys |

Use Secret for sensitive even if not "real secrets." Habit.

## Quick Refs

```bash
# Create from literal
kubectl create cm app-config --from-literal=key=value

# From file
kubectl create cm app-config --from-file=app.yaml

# Apply
kubectl apply -f cm.yaml

# Use as env (in pod spec)
envFrom:
- configMapRef:
    name: app-config

# Use as file (in pod spec)
volumes:
- name: config
  configMap:
    name: app-config

volumeMounts:
- name: config
  mountPath: /etc/config
```

## Interview Prep

**Junior**: "What's a ConfigMap."

**Mid**: "Auto-update of mounted CM."

**Senior**: "ConfigMap update strategy for 100 services."

## Next Topic

→ [T02 — Secrets (And Why They're Not Really Secret)](T02-Secrets.md)
