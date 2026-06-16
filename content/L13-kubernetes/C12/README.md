# L13/C12 — Kustomize

## Topics

- **T01 Bases & Overlays** — Base = reusable manifest set. Overlay = environment-specific patches.
- **T02 Patches (Strategic Merge, JSON Patch)** — Strategic merge replaces by key; JSON Patch uses RFC 6902 operations.
- **T03 Generators** — configMapGenerator, secretGenerator. Auto-hashed names trigger pod rollouts on change.

## Layout

```
base/
├── kustomization.yaml
├── deployment.yaml
├── service.yaml
└── configmap.yaml

overlays/
├── dev/
│   ├── kustomization.yaml
│   ├── patches/
│   │   └── deployment-resources.yaml
│   └── configmap-patch.yaml
├── staging/
└── prod/
```

## base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

commonLabels:
  app: myapp

resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml

configMapGenerator:
  - name: myapp-config
    files:
      - config.yaml
```

## overlays/prod/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: prod

patches:
  - path: deployment-resources.yaml
    target:
      kind: Deployment
      name: myapp

replicas:
  - name: myapp
    count: 10

images:
  - name: myapp
    newTag: v1.2.3
```

## Usage

```bash
kubectl apply -k overlays/prod/
kustomize build overlays/prod/        # render to stdout
```

## Why Kustomize Wins (Sometimes)

- Pure YAML — no templating language
- Built into kubectl (`-k`)
- ArgoCD/Flux native support
- Composes well with patches

## Why Kustomize Loses (Sometimes)

- No conditionals
- Patches can become hard to track at scale
- Less ecosystem than Helm

## Interview Themes

- "Compare Helm and Kustomize"
- "Walk me through a multi-environment Kustomize layout"
- "Strategic merge vs JSON patch — when to use each"
