# L16/C07/T01 — Flux v2: Source, Kustomize, Helm Controllers

## Learning Objectives

- Use Flux v2
- Understand controller model

## Flux

GitOps for K8s; CNCF graduated:
- Pure GitOps (no UI by default)
- Multi-controller architecture
- Helm + Kustomize first-class

## Controllers

- **Source Controller**: fetches Git / Helm / S3
- **Kustomize Controller**: applies Kustomize
- **Helm Controller**: installs Helm releases
- **Notification Controller**: events + alerts
- **Image Reflector / Updater**: image automation

## Install

```bash
# CLI
brew install fluxcd/tap/flux

# Bootstrap (creates Flux + commits to Git)
flux bootstrap github \
  --owner=myorg \
  --repository=my-cluster \
  --branch=main \
  --path=clusters/production
```

Flux installs itself; commits manifest.

## GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/me/manifests.git
  ref:
    branch: main
```

Polls Git.

## Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: "./apps/my-app"
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
  targetNamespace: prod
```

Applies Kustomize-rendered manifests.

## HelmRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: nginx
spec:
  interval: 1h
  url: https://kubernetes.github.io/ingress-nginx
```

## HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: nginx
spec:
  interval: 5m
  chart:
    spec:
      chart: ingress-nginx
      version: '4.x'
      sourceRef:
        kind: HelmRepository
        name: nginx
  values:
    controller:
      replicaCount: 2
```

## OCIRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: OCIRepository
metadata:
  name: my-app
spec:
  interval: 1m
  url: oci://registry.example.com/charts/my-app
  ref:
    tag: v1.0.0
```

For: OCI-stored manifests / charts.

## Bucket

S3 / GCS source:
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: Bucket
metadata:
  name: my-app
spec:
  interval: 5m
  endpoint: s3.amazonaws.com
  bucketName: my-manifests
  secretRef:
    name: my-aws-creds
```

## Variables

```yaml
spec:
  postBuild:
    substitute:
      cluster_name: production
      region: us-east-1
```

Substitutes in manifests at apply time.

## Dependencies

```yaml
kind: Kustomization
metadata:
  name: app
spec:
  dependsOn:
  - name: cert-manager
```

App waits for cert-manager Kustomization.

## Notification

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: slack
spec:
  type: slack
  address: https://hooks.slack.com/...

---
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: my-alerts
spec:
  providerRef:
    name: slack
  eventSeverity: error
  eventSources:
  - kind: Kustomization
    name: my-app
```

For: Slack alerts on errors.

## Image Automation

ImageRepository + ImagePolicy + ImageUpdateAutomation:
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: my-app
spec:
  image: registry/my-app
  interval: 1m

---
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: ">=1.0.0"
```

Updates Git when new image:
- Detects new tag
- Commits updated manifest
- Kustomization syncs

## Multi-Tenancy

```
clusters/
  cluster-a/
    flux-system/
    apps/
      team-1/
      team-2/
  cluster-b/
    ...
```

Per cluster + team.

## Sync Modes

### Pull (Default)
Flux polls Git.

### Push (via Webhook)
Webhook tells Flux to re-sync.

```yaml
kind: Receiver
spec:
  type: github
  events: [push]
  resources:
  - kind: GitRepository
    name: my-app
```

For: faster.

## vs ArgoCD

| | Flux | ArgoCD |
|---|---|---|
| UI | None default (gitops UI add-on) | Rich UI |
| Multi-cluster | Federation / per-cluster | Single ArgoCD multi-cluster |
| Helm | First-class | First-class |
| Image automation | Built-in | Image Updater |
| Controllers | Many small | One bigger |
| Mindshare | Smaller | Larger |
| Bootstrap | CLI | Install + register |

## Choose

For: Flux if multi-controller, GitOps purist.
For: ArgoCD if want UI, simpler model.

## RBAC

Per-Kustomization service account:
```yaml
spec:
  serviceAccountName: team-a-sa
```

Apply with that SA's permissions.

For: tenant isolation.

## Validation

```bash
flux check
flux get kustomization -A
flux logs --all-namespaces
```

## Suspend / Resume

```bash
flux suspend kustomization my-app
flux resume kustomization my-app
```

For: pause sync.

## Best Practices

- Bootstrap-via-CLI
- Per-cluster, per-team isolation
- Notifications for failures
- Image automation for tag updates
- Webhooks for fast sync
- RBAC per Kustomization

## Common Mistakes

- Single GitRepository all clusters
- No notifications (silent failures)
- Manual changes to cluster (Flux reverts)
- Cluster-admin Flux

## Quick Refs

```bash
flux bootstrap github --owner=O --repository=R
flux create source git NAME --url=URL --branch=BRANCH
flux create kustomization NAME --source=...
flux get / suspend / resume
flux logs / events
```

## Interview Prep

**Mid**: "Flux v2 controllers."

**Senior**: "Flux vs ArgoCD."

**Staff**: "GitOps platform."

## Next Topic

→ Move to [L16/C08 — Spinnaker](../C08/README.md)
