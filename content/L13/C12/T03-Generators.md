# L13/C12/T03 — Generators

## Learning Objectives

- Use configMapGenerator and secretGenerator
- Trigger rollouts via hash suffix

## Generators

Create ConfigMaps and Secrets from sources.

Auto-hashed names trigger pod restart on content change.

## configMapGenerator

```yaml
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=info
  - PORT=8080
  files:
  - app.yaml
  - log4j.properties
  envs:
  - .env
```

Generates ConfigMap with content.

Name suffix: `app-config-abc123` (hash of content).

Content change → new hash → new ConfigMap → triggers Deployment rollout (if references).

## secretGenerator

```yaml
secretGenerator:
- name: db-secret
  literals:
  - username=admin
  - password=changeme
  type: Opaque
```

Similar, but Secret type.

## File-Based

```yaml
configMapGenerator:
- name: nginx-config
  files:
  - nginx.conf
  - mime.types
```

Each file becomes key (filename) → value (content).

## Env File

```yaml
configMapGenerator:
- name: env-config
  envs:
  - .env
```

`.env`:
```
LOG_LEVEL=debug
DB_HOST=db.example.com
```

Each line becomes key=value.

## Hash Suffix

Default: name suffixed with content hash:
```
app-config → app-config-abc123def
```

If content changes: new hash → new ConfigMap → Deployment template updates → rollout.

## Disable Hash

```yaml
generatorOptions:
  disableNameSuffixHash: true
```

For: when you don't want rollout on every change.

Risk: stale config not picked up.

## Annotations / Labels

```yaml
configMapGenerator:
- name: app-config
  literals: ...
  options:
    annotations:
      env: prod
    labels:
      app: my-app
```

For: organize.

## Reference

```yaml
spec:
  containers:
  - name: app
    envFrom:
    - configMapRef:
        name: app-config        # Kustomize rewrites to app-config-abc123
```

Kustomize updates references; no manual hash.

## Multiple Generators

```yaml
configMapGenerator:
- name: app-config
  literals: [LOG_LEVEL=info]
- name: db-config
  literals: [DB_HOST=db]

secretGenerator:
- name: api-secret
  literals: [api_key=xyz]
- name: db-secret
  literals: [password=changeme]
```

## Merging (Same Name)

To extend existing ConfigMap:
```yaml
configMapGenerator:
- name: app-config
  behavior: merge       # or create / replace
  literals:
  - NEW_KEY=value
```

`behavior` options:
- `create`: error if exists (default)
- `merge`: add to existing
- `replace`: full replace

For overlay extending base.

## Per-Env

base:
```yaml
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=info
```

overlays/prod:
```yaml
configMapGenerator:
- name: app-config
  behavior: merge
  literals:
  - LOG_LEVEL=warn       # override
  - METRICS_ENABLED=true # add
```

Final: merged with prod's overrides.

## File Sources Per Env

base/app.yaml: defaults
overlays/prod/app.yaml: prod-specific

```yaml
# overlay
configMapGenerator:
- name: app-config
  behavior: replace
  files:
  - app.yaml
```

Replaces whole ConfigMap with overlay's file.

## Secret Generator Types

```yaml
secretGenerator:
- name: tls
  type: kubernetes.io/tls
  files:
  - tls.crt
  - tls.key
- name: docker-creds
  type: kubernetes.io/dockerconfigjson
  files:
  - .dockerconfigjson
```

For TLS, image pull, etc.

## Variables in Generators (Manual)

Generators don't support templating. Workaround:
- Multiple env-specific files
- Or generate files in CI before kustomize build

## When NOT Generators

- ConfigMaps managed by Operators (let them create)
- ConfigMaps watched by external controllers
- Large binary content (use volume mount of file)

## Best Practices

- Use generators for managed configs
- Behavior `merge` for per-env additions
- Disable hash if rollout undesired
- Don't put secrets in plain (use sealed-secrets, SOPS, External Secrets)

## Common Mistakes

- Hardcoded ConfigMap name (Kustomize-managed has hash)
- behavior: create when overlay (collision with base)
- Generating secret with plain values committed
- Forgot to reference generated CM in pod

## Secret Patterns

For sensitive:
- Don't generate from plain literals (committed)
- Use External Secrets Operator
- Or SOPS-encrypted source
- Or Sealed Secrets

For non-sensitive: literals OK.

## SOPS Integration

```yaml
secretGenerator:
- name: db-secret
  files:
  - password.enc=password.enc   # SOPS-encrypted
```

Decrypt before kustomize build:
```bash
sops -d password.enc > password
kustomize build ./
rm password
```

Or use kustomize-sops plugin.

## Disabling Hash for Operators

If ConfigMap managed by external (Operator updates):
```yaml
generatorOptions:
  disableNameSuffixHash: true
```

Operator doesn't know about hash.

## Output Manifests

```bash
kustomize build ./overlays/prod
# Includes:
# - ConfigMap with hashed name
# - Deployment referencing hashed name
```

Apply: K8s creates ConfigMap; pods reference; rollout if changed.

## Inspection

```bash
kustomize build ./overlays/prod | grep -A 10 'kind: ConfigMap'
```

Show generated content.

## ConfigMap Update Effect

Mount changes propagate to file mounts (~minute).
Env vars: NO update; pod restart needed.

Hash suffix triggers pod restart automatically.

For: predictable config rollout.

## Pattern: ConfigMap Hash via Patch

Alternative to generators: manually compute hash; annotation:
```yaml
metadata:
  annotations:
    config-hash: {{ sha256sum cm-content }}
```

For: not using generators but still wanting rollout.

## Generators + Patches

Generators create resources; patches modify them:
```yaml
configMapGenerator:
- name: app-config
  literals: ...

patches:
- target:
    kind: ConfigMap
    name: app-config
  patch: |-
    metadata:
      labels:
        managed-by: kustomize
```

For: add labels to generated.

## Common Setup

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml

configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=info

# overlays/prod/kustomization.yaml
resources:
- ../../base

configMapGenerator:
- name: app-config
  behavior: merge
  literals:
  - LOG_LEVEL=warn
  - METRICS_ENABLED=true

patches:
- path: replicas-patch.yaml
```

## Quick Refs

```yaml
configMapGenerator:
- name: NAME
  literals: [K=V]
  files: [file]
  envs: [.env]
  behavior: create|merge|replace

secretGenerator:
- name: NAME
  literals: [K=V]
  files: [file]
  type: Opaque|kubernetes.io/tls|kubernetes.io/dockerconfigjson

generatorOptions:
  disableNameSuffixHash: true|false
  labels: {...}
  annotations: {...}
```

## Interview Prep

**Mid**: "Generators purpose."

**Senior**: "Hash suffix mechanism."

**Staff**: "Config rollout strategy."

## Next Topic

→ Move to [L13/C13 — Service Mesh in K8s](../C13/README.md)
