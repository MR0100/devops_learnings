# L16/C07 — Flux v2

## Topics

- **T01 Source, Kustomize, Helm Controllers** — Flux's modular architecture.

## Architecture

Flux is a set of controllers:
- **Source Controller**: pulls Git/Helm/OCI sources, stores artifacts
- **Kustomize Controller**: applies kustomized manifests from sources
- **Helm Controller**: manages HelmReleases
- **Notification Controller**: alerts (Slack, MS Teams, etc.)
- **Image Automation Controller**: detects new images, opens PRs

## GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-repo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/manifests
  ref:
    branch: main
  secretRef:
    name: github-credentials
```

## Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: my-repo
  path: ./deploy/overlays/prod
  prune: true
  wait: true
  timeout: 5m
  patches:
    - patch: |
        - op: replace
          path: /spec/replicas
          value: 10
      target:
        kind: Deployment
        name: my-app
  postBuild:
    substitute:
      env: prod
      region: us-east-1
```

## HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: redis
  namespace: cache
spec:
  interval: 10m
  chart:
    spec:
      chart: redis
      version: '17.x'
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    architecture: replication
    auth:
      enabled: true
```

## Image Automation

Flux can detect new images and update Git manifests:

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: app
spec:
  image: ghcr.io/org/app
  interval: 1m

---
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: app
spec:
  imageRepositoryRef: { name: app }
  policy:
    semver:
      range: '>=1.0.0'
```

When new image v1.2.5 appears matching the policy, Flux commits an update to the manifest in Git. Then Kustomize Controller picks it up and deploys.

## Flux vs ArgoCD

| | Flux | ArgoCD |
|---|---|---|
| Architecture | Microservice (controllers) | Monolithic |
| UI | None (CLI / third-party) | Rich web UI |
| Multi-tenancy | Strong | Strong |
| Image automation | Built-in | Argo Image Updater (add-on) |
| Multi-source per app | Native | Newer feature |
| Best for | GitOps purists, CLI-driven | Visibility, team UI |

## Bootstrap

```bash
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/my-cluster \
  --personal
```

This commits Flux's own manifests to your Git repo; Flux then manages itself from Git.

## When Flux

- Pure GitOps preference
- Heavy K8s-native users
- Don't need UI
- Want microservice architecture

## Interview Themes
- "Flux v2 controllers — describe"
- "Flux image automation"
- "Flux vs ArgoCD"
- "Bootstrap — how?"
