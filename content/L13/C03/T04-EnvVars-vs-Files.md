# L13/C03/T04 — Environment Variables vs Files

## Learning Objectives

- Choose between env vars and files
- Apply each correctly

## Two Options

ConfigMap / Secret can be mounted as:
- Env vars
- Files (volume)

Each has trade-offs.

## Env Vars

```yaml
env:
- name: LOG_LEVEL
  value: info
- name: DB_URL
  valueFrom:
    secretKeyRef:
      name: db
      key: url
```

### Pros
- Simple
- 12-factor app standard
- Auto-injected at process start
- Inspectable via `env`

### Cons
- NO auto-update (must restart for new values)
- Visible in `ps -e -f` (sometimes)
- Logged on crash (sometimes)
- Static size limit (env block ~32 KB typically)
- Can leak via subprocess

## Files

```yaml
volumes:
- name: config
  configMap:
    name: app-config

volumeMounts:
- name: config
  mountPath: /etc/config
```

App reads /etc/config/log.level etc.

### Pros
- Auto-update (volume reflects CM changes)
- Larger size capable
- More secure (not in process env)
- Better for structured config (YAML, JSON)

### Cons
- App must read files (more code)
- Setup more verbose

## When Env Vars

- Simple settings (LOG_LEVEL, PORT)
- 12-factor standards
- Existing app uses env
- Static config

## When Files

- Structured config (YAML, properties)
- Config that updates without restart
- Sensitive data (avoid env)
- Larger data

## Mixed

Common: simple things env; complex things files:
```yaml
env:
- name: LOG_LEVEL
  value: info

volumes:
- name: config
  configMap:
    name: app-config

volumeMounts:
- name: config
  mountPath: /etc/config

# App reads /etc/config/app.yaml for complex
```

## Auto-Update Mechanics

Volume-mounted CM:
- kubelet syncs every few minutes
- Updates files atomically (symlink swap)
- App must detect (watch / poll)

Env vars:
- Set at process start
- Container restart needed for new

## Watching Files

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == '/etc/config/app.yaml':
            reload_config()

observer = Observer()
observer.schedule(Handler(), '/etc/config', recursive=True)
observer.start()
```

Or simpler: poll every 30s; check file mtime.

## SubPath Mount

To mount one specific file:
```yaml
volumeMounts:
- name: config
  mountPath: /etc/myapp/app.yaml
  subPath: app.yaml
```

But: subPath mounts do NOT receive updates.

For auto-update: mount whole dir.

## Env Var Approach Updates

Need restart:
```bash
kubectl rollout restart deployment/web
```

Or Reloader Operator:
```yaml
annotations:
  reloader.stakater.com/auto: "true"
```

Auto-restart on CM/Secret change.

## Sensitive Data

Secrets as env vars:
- Visible in process env
- Subprocess inherits
- Logged on crash sometimes

Secrets as files:
- Read only when needed
- Not in env block
- More secure

For passwords / API keys: prefer files (or use Secret Manager).

## Limits

| | Env | Files |
|---|---|---|
| Size | ~32 KB total | 1 MiB per CM/Secret |
| Update | Restart needed | Auto |
| Setup | Simple | Volume + mount |
| Sensitive | Less secure | More secure |
| Structured | Awkward | Natural |

## Patterns

### 12-Factor Standard
```yaml
env:
- name: PORT
  value: "8080"
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: db
      key: url
- name: LOG_LEVEL
  value: info
```

App reads `os.environ["PORT"]`. Standard.

### Spring Boot / Java
External application.yml:
```yaml
volumes:
- name: config
  configMap:
    name: app-config

volumeMounts:
- name: config
  mountPath: /config

# Spring auto-discovers /config/application.yml
```

### Mixed Reload
Env vars: static (start-only).
Files: dynamic.

Combine: most config in files; bootstrap in env.

## ConfigMap Hash Strategy

Helm / Kustomize: add hash of CM as annotation on Deployment:
```yaml
template:
  metadata:
    annotations:
      checksum/config: <hash>
```

CM change → hash change → Deployment template change → rollout.

For env var approach.

## Secrets in Env

```yaml
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db
      key: password
```

Concerns:
- Logged on crash (some apps print env)
- Subprocess sees
- Visible in `kubectl describe pod` (kind of)

For high-security: mount as file; read at startup; clear from memory after.

## Vault Agent Pattern

Vault sidecar:
- Fetches secrets from Vault
- Renders to files
- App reads files

For: rotating secrets, dynamic secrets (per-app DB user).

## Init Container Pattern

Init container fetches secrets / config:
```yaml
initContainers:
- name: fetch
  image: secret-fetcher
  volumeMounts:
  - name: secrets
    mountPath: /secrets
  command: ["fetch", "/secrets/app.json"]

containers:
- name: app
  volumeMounts:
  - name: secrets
    mountPath: /secrets
    readOnly: true
```

Init writes to emptyDir; app reads.

For: bootstrap with external secrets.

## App Design

For new apps: support both:
- Env for simple
- Config file for complex
- Defaults in code

```python
config = load_yaml("/etc/config/app.yaml") if exists else {}
log_level = os.environ.get("LOG_LEVEL") or config.get("log.level") or "info"
```

Precedence: env > file > default.

## Common Mistakes

- Env vars for huge config
- Files without watch (stale)
- Secrets in env when files better
- No update strategy
- SubPath expecting updates

## Best Practices

- Simple → env vars
- Complex → files
- Sensitive → files (or external)
- Document update strategy
- Use Helm/Kustomize for hash-rollouts
- Reloader Operator if needed

## Testing

Manually update CM:
```bash
kubectl edit cm app-config
```

Check file update in pod:
```bash
kubectl exec my-pod -- cat /etc/config/app.yaml
# (wait minute)
kubectl exec my-pod -- cat /etc/config/app.yaml   # updated
```

Env vars: pod restart needed:
```bash
kubectl rollout restart deployment/web
```

## Quick Refs

```yaml
# Env from CM
env:
- name: X
  valueFrom:
    configMapKeyRef:
      name: my-cm
      key: x

# File from CM
volumes:
- name: cfg
  configMap:
    name: my-cm

volumeMounts:
- name: cfg
  mountPath: /etc/cfg

# Env from Secret
env:
- name: PASS
  valueFrom:
    secretKeyRef:
      name: my-sec
      key: pass

# File from Secret
volumes:
- name: secret
  secret:
    secretName: my-sec
    defaultMode: 0400

volumeMounts:
- name: secret
  mountPath: /etc/secrets
  readOnly: true
```

## Interview Prep

**Mid**: "Env vs file mount."

**Senior**: "Dynamic config refresh."

**Staff**: "Config strategy for 100 microservices."

## Next Topic

→ Move to [L13/C04 — Networking in Kubernetes](../C04/README.md)
