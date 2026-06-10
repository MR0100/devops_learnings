# L13/C12/T01 — Bases & Overlays

## Learning Objectives

- Use Kustomize for env config
- Apply overlay pattern

## Kustomize

Native K8s tool (built into kubectl). Customize without templating.

vs Helm:
- Kustomize: overlays + patches
- Helm: templating + packaging

```bash
kubectl apply -k ./overlays/dev
```

Or:
```bash
kustomize build ./overlays/dev | kubectl apply -f -
```

## Concepts

- **Base**: reusable manifests
- **Overlay**: env-specific customizations

## Base

```
base/
├── kustomization.yaml
├── deployment.yaml
├── service.yaml
└── configmap.yaml
```

kustomization.yaml:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
- configmap.yaml

commonLabels:
  app: my-app

namespace: default
```

Manifests are vanilla K8s YAML.

## Overlay

```
overlays/
├── dev/
│   ├── kustomization.yaml
│   └── replica-patch.yaml
├── staging/
│   └── kustomization.yaml
└── prod/
    ├── kustomization.yaml
    └── replica-patch.yaml
```

overlays/prod/kustomization.yaml:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production

resources:
- ../../base

patches:
- path: replica-patch.yaml

commonLabels:
  env: prod

images:
- name: my-app
  newTag: v1.2.3
```

overlays/prod/replica-patch.yaml:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 5
```

## Build

```bash
kustomize build ./overlays/prod
# or
kubectl kustomize ./overlays/prod
```

Outputs combined manifests.

## Apply

```bash
kubectl apply -k ./overlays/prod
```

## Common Patterns

### Per-Environment Replicas
Base: 1 replica.
Overlay/prod: patch to 10.

### Per-Environment Resources
Base: small CPU/RAM.
Overlay/prod: larger.

### Per-Environment Images
```yaml
images:
- name: my-app
  newTag: v1.2.3-prod
```

### Per-Environment Configs
Different ConfigMap per env:
```yaml
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=info
  - API_URL=https://prod.api.example.com
```

## Resources

```yaml
resources:
- deployment.yaml
- service.yaml
- ../shared/network-policy.yaml   # path
- github.com/me/repo/manifests?ref=v1  # remote
```

Local files, paths, remote.

## Naming Prefix / Suffix

```yaml
namePrefix: prod-
nameSuffix: -v2

# my-app → prod-my-app-v2
```

For multi-env in same namespace (rare).

## Labels + Annotations

```yaml
commonLabels:
  app: my-app
  env: prod
commonAnnotations:
  contact: alice@example.com
```

Applied to all resources.

## Namespace

```yaml
namespace: production
```

Overrides namespace in all resources.

## Replacements

Set fields based on other fields:
```yaml
replacements:
- source:
    kind: ConfigMap
    name: app-config
    fieldPath: data.DOMAIN
  targets:
  - select:
      kind: Ingress
      name: my-app
    fieldPaths:
    - spec.rules.0.host
```

Replace Ingress host with ConfigMap's DOMAIN value.

## Multi-Layer Overlays

```
base/
overlays/
├── common/
│   ├── kustomization.yaml
│   └── ...
├── dev/
│   ├── kustomization.yaml      # references common
│   └── ...
└── prod/
    ├── kustomization.yaml      # references common
    └── ...
```

Common layer for shared overrides.

## Components

Reusable optional pieces:
```yaml
components:
- ../components/monitoring
- ../components/logging
```

Mix into overlays.

## kustomization.yaml Fields

- `resources`: manifests to include
- `bases`: legacy (use `resources` now)
- `patches`: modifications
- `patchesStrategicMerge`: legacy (use `patches`)
- `patchesJson6902`: legacy
- `configMapGenerator`: generate ConfigMaps
- `secretGenerator`: generate Secrets
- `commonLabels` / `commonAnnotations`
- `namespace`
- `namePrefix` / `nameSuffix`
- `images`: image tag overrides
- `replicas`: replica overrides
- `replacements`: field replacements
- `generatorOptions`: hash suffix, etc.

## Edit kustomization

```bash
kustomize edit set image my-app=my-app:v2.0
kustomize edit add resource deployment.yaml
kustomize edit set replicas my-deployment=5
```

CLI mutates kustomization.yaml.

## Kustomize vs Helm

| | Kustomize | Helm |
|---|---|---|
| Templating | No (overlays) | Yes |
| Native K8s | Yes (kubectl) | No |
| Versioning | Manual | Built-in releases |
| Sharing | Files / Git | Charts / OCI |
| Learning | Easier | Steeper |
| Complexity | Easier for simple | Better for complex |

For: simple multi-env. → Kustomize.
For: distribution + parameters. → Helm.

Can combine: Helm chart + Kustomize overlay (less common).

## ArgoCD Support

ArgoCD natively supports Kustomize:
```yaml
spec:
  source:
    path: overlays/prod
    kustomize:
      images:
      - my-app:v1.2.3
```

For: GitOps with Kustomize.

## Common Mistakes

- Forgot to reference overlay from kustomization.yaml
- Patch field doesn't match base
- Resource not in base (overlay patches nothing)
- commonLabels conflict with selectors (immutable)

## commonLabels Caveat

Adding commonLabels post-deploy can break Deployment selectors (immutable).

Plan labels upfront.

## Selectors

Deployment.spec.selector.matchLabels must match template labels.

If commonLabels adds new label: both selector and template get it. Generally OK.

But: changing existing labels breaks selector match.

## Output

```bash
kustomize build ./overlays/prod > rendered.yaml
```

Or:
```bash
kustomize build ./overlays/prod | kubectl apply -f -
```

## Image Override

```yaml
images:
- name: nginx
  newName: my-registry/nginx
  newTag: v1.27
- name: my-app
  digest: sha256:abc...
```

Per-env image tag without editing Deployment YAML.

## Replicas Override

```yaml
replicas:
- name: my-app
  count: 5
```

Per-env scale.

## Best Practices

- Base = vanilla; no env-specific
- Overlay = env-specific only
- One overlay per env
- Common label / namespace per overlay
- Use generators for Configs
- Avoid deep nesting

## Common Mistakes

- Env-specific in base
- No overlay (just one set; no flexibility)
- Patches that don't apply
- Manual edits to generated manifests

## Best Practices

- Bases minimal
- Overlays focused
- Use generators
- Version control everything
- Diff before apply (`kubectl diff -k ./`)
- Plan labels upfront
- CI validates `kustomize build`

## When NOT Kustomize

- Need true templating (variables, conditionals)
- Distribution to other teams (Helm chart)
- Complex parameter logic

For: stay with Helm.

## Comparison

For 5-service app, 3 envs:
- Kustomize: 1 base + 3 overlays
- Helm: 1 chart + 3 values files

Both work. Kustomize: vanilla YAML. Helm: templates.

## Quick Refs

```bash
# Build (render)
kustomize build ./overlays/prod
kubectl kustomize ./overlays/prod

# Apply
kubectl apply -k ./overlays/prod

# Edit
kustomize edit set image X=Y:v2
kustomize edit add resource cm.yaml

# Diff
kubectl diff -k ./overlays/prod
```

## Interview Prep

**Mid**: "Kustomize vs Helm."

**Senior**: "Overlay design."

**Staff**: "Kustomize for 20-service multi-env platform."

## Next Topic

→ [T02 — Patches (Strategic Merge, JSON Patch)](T02-Patches.md)
