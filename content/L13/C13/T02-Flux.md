# L13/C13/T02 — Flux v2

## Learning Objectives

- Use Flux v2
- Compare with ArgoCD

## Flux v2

GitOps tool. Modular controllers (vs ArgoCD's monolithic):
- Source Controller
- Kustomize Controller
- Helm Controller
- Notification Controller
- Image Automation Controller

## Install

```bash
brew install fluxcd/tap/flux

# Bootstrap
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/prod \
  --personal
```

Creates Git repo + installs Flux + commits manifests.

## Source Controller

Watches Git/Helm/OCI sources:
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/me/my-app
  ref:
    branch: main
```

Fetches Git; provides to other controllers.

## Helm Repository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami
```

For Helm chart sources.

## OCI Repository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: OCIRepository
metadata:
  name: my-app
spec:
  interval: 1m
  url: oci://ghcr.io/myorg/manifests
  ref:
    tag: latest
```

For OCI-distributed manifests.

## Kustomization

Apply Kustomize from source:
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./overlays/prod
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
  targetNamespace: production
  validation: client
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: my-app
    namespace: production
```

Reconciles K8s state to match source.

## HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: redis
  namespace: cache
spec:
  interval: 5m
  chart:
    spec:
      chart: redis
      version: 17.x.x
      sourceRef:
        kind: HelmRepository
        name: bitnami
  values:
    master:
      persistence:
        size: 20Gi
```

Installs/upgrades chart.

## Reconciliation

Each controller:
- Watches its CR
- Compares actual vs desired
- Reconciles

Pull-based; cluster reads Git.

## Dependencies

```yaml
spec:
  dependsOn:
  - name: cert-manager
```

Wait for other Kustomization/HelmRelease before applying.

For: ordered deploys.

## Image Automation

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: my-app
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: ">=1.0.0"
```

Auto-update image tag in Git when new published.

For: continuous deployment of latest image.

## Notification

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Alert
metadata:
  name: slack
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
  - kind: Kustomization
    name: '*'
```

Slack/Teams/webhook on events.

## Flux vs ArgoCD

| | Flux v2 | ArgoCD |
|---|---|---|
| Architecture | Modular controllers | Monolithic |
| UI | Limited (Weave GitOps) | Rich |
| API | CRDs | CRDs + API server |
| Multi-cluster | Per-cluster install | Centralized |
| Image automation | Built-in | Argo Image Updater addon |
| Learning curve | More CRDs to learn | Higher-level abstraction |
| Maturity | Stable | Stable |

For UI: ArgoCD often.
For CRD-native: Flux.

## Multi-Cluster

Each cluster has Flux installed. Each pulls own state.

For central management: ArgoCD or Flux + Multi-Cluster operators (KCP, Cluster API).

## Sync Mode

Flux always automated. No "manual" sync per app.

For pause:
```yaml
spec:
  suspend: true
```

## Drift Handling

Flux continuously reconciles:
- Drift detected → applies Git state
- Like ArgoCD selfHeal but always on

## Bootstrap

`flux bootstrap`:
1. Creates Git repo
2. Adds Flux manifests
3. Commits + pushes
4. Installs Flux in cluster
5. Flux watches its own repo (self-managed)

## Webhooks

Receiver:
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Receiver
metadata:
  name: github-webhook
spec:
  type: github
  events:
  - "push"
  secretRef:
    name: webhook-token
  resources:
  - kind: GitRepository
    name: my-app
```

GitHub webhook → instant sync.

## RBAC

Per-namespace service accounts:
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
spec:
  serviceAccountName: my-app-deployer
```

Flux uses this SA's permissions.

For: tenant isolation.

## Tenancy

Per-team namespaces with own GitOps:
- Tenant SA with limited RBAC
- Per-team Kustomization
- Source from team's repo

For: multi-team platform.

## Decryption

Sealed Secrets / SOPS support:
```yaml
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-keys
```

Decrypts SOPS-encrypted files in Git before apply.

## Health Checks

```yaml
healthChecks:
- apiVersion: apps/v1
  kind: Deployment
  name: my-app
  namespace: prod
```

Kustomization waits for resource healthy.

## Pruning

```yaml
spec:
  prune: true
```

Delete resources removed from Git.

## Validation

```yaml
spec:
  validation: client   # validate before apply
```

For: catch errors.

## Inspection

```bash
flux get all -A
flux get sources git
flux get kustomizations
flux get helmreleases

# Logs
flux logs --all-namespaces --follow

# Reconcile
flux reconcile kustomization my-app
flux suspend kustomization my-app
flux resume kustomization my-app
```

## Weave GitOps

UI for Flux (optional):
```bash
helm install weave-gitops weaveworks/weave-gitops
```

For visual dashboard.

## When Flux

- CRD-native preference
- Multi-controller modularity
- Image automation built-in
- Don't need rich UI
- Self-bootstrap

## When ArgoCD

- Rich UI critical
- Many users (UI for ops)
- Multi-cluster central management
- Existing ArgoCD investment

For most: ArgoCD edge (UI).
For modular / cloud-native: Flux.

## Best Practices

- Bootstrap once; manage via Git
- Per-app Kustomization
- Image automation for fast deploy
- Notifications
- SOPS for secrets
- Tenant isolation via SA

## Common Mistakes

- Manual `kubectl apply` (Flux reverts)
- No notifications (silent failures)
- Wide SA permissions
- Plain secrets in Git

## Operations

```bash
# Apply manifest
kubectl apply -f kustomization.yaml

# Check sync
flux get kustomization my-app

# Force reconcile
flux reconcile source git my-app
flux reconcile kustomization my-app
```

## Quick Refs

```bash
flux bootstrap github --owner=X --repository=Y
flux create source git NAME --url=URL --branch=main
flux create kustomization NAME --source=GitRepository/NAME --path=./
flux get all -A
flux logs --follow
```

## Interview Prep

**Mid**: "Flux vs ArgoCD."

**Senior**: "Multi-tenant GitOps with Flux."

**Staff**: "GitOps platform for 50 teams."

## Next Topic

→ [T03 — App-of-Apps Pattern](T03-App-of-Apps.md)
