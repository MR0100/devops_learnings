# L13/C13/T01 — ArgoCD Deep Dive

## Learning Objectives

- Use ArgoCD for GitOps
- Configure Applications

## ArgoCD

Declarative GitOps tool for K8s.

Pull-based: cluster pulls desired state from Git.

```bash
# Install
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Architecture

- **API Server**: REST/gRPC API + UI
- **Repo Server**: clones Git, renders (Helm template, Kustomize build)
- **Application Controller**: reconciles state
- **Redis**: cache
- **Dex**: OIDC (optional)

## Application

CR representing one app/deployment:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/me/repo
    targetRevision: main
    path: manifests/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## Source Types

- Plain YAML: `path: manifests/`
- Kustomize: `path: overlays/prod` (auto-detected by kustomization.yaml)
- Helm:
  ```yaml
  source:
    repoURL: https://charts.bitnami.com/bitnami
    chart: redis
    targetRevision: 17.0.0
    helm:
      values: |
        master:
          persistence:
            size: 20Gi
  ```
- Jsonnet, Plugin

## Sync Policy

### Manual
User triggers sync via UI / CLI.

### Automated
ArgoCD syncs when Git changes.

```yaml
syncPolicy:
  automated:
    prune: true       # delete resources removed from Git
    selfHeal: true    # revert manual changes
  syncOptions:
  - CreateNamespace=true
```

### Prune
Remove resources no longer in Git.

Without: orphan resources accumulate.

### SelfHeal
Revert manual changes to match Git.

Without: drift between Git + cluster.

## App Status

```
Synced: Git == Cluster
OutOfSync: Git differs from Cluster
Unknown: can't determine
```

```
Healthy: all resources OK
Progressing: rolling out
Degraded: some unhealthy
Suspended: paused
Missing: doesn't exist
```

## CLI

```bash
argocd login argocd.example.com
argocd app list
argocd app get my-app
argocd app sync my-app
argocd app diff my-app
argocd app history my-app
argocd app rollback my-app 5
```

## UI

Web dashboard:
- Application list
- Resource tree visualization
- Sync status
- Logs
- Events

## Auto-Discovery

Each app shows tree:
- Application → Deployment → ReplicaSet → Pods
- → Service → Endpoints
- → Ingress → Rules

Click for details.

## Project

Group of Applications:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: prod-team
  namespace: argocd
spec:
  description: Prod team applications
  sourceRepos:
  - https://github.com/myorg/prod-*
  destinations:
  - namespace: prod-*
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: ""
    kind: Namespace
  namespaceResourceWhitelist:
  - group: "*"
    kind: "*"
```

For: RBAC + restrictions.

## RBAC

```yaml
policy.csv: |
  p, role:dev, applications, sync, default/dev-*, allow
  p, role:dev, applications, get, default/dev-*, allow
  g, alice, role:dev
```

Per-user / group permissions.

For: multi-tenant.

## Cluster Targets

Multi-cluster:
```yaml
spec:
  destination:
    server: https://other-cluster.example.com
    namespace: prod
```

```bash
argocd cluster add my-cluster
```

ArgoCD manages many clusters from one control plane.

## Repo Credentials

Private repos:
```bash
argocd repo add https://github.com/myorg/private --username X --password Y
# Or SSH
argocd repo add git@github.com:myorg/private --ssh-private-key-path ~/.ssh/id_rsa
```

## Helm Values

```yaml
source:
  repoURL: ...
  chart: ...
  helm:
    values: |
      replicas: 3
    valueFiles:
    - values-prod.yaml
    parameters:
    - name: image.tag
      value: v1.2.3
```

Override values.

## Kustomize

```yaml
source:
  repoURL: ...
  path: overlays/prod
  kustomize:
    namePrefix: prod-
    images:
    - my-app:v1.2.3
    commonLabels:
      env: prod
```

Override kustomization fields.

## Sync Hooks

Like Helm hooks:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
```

Phases:
- PreSync
- Sync
- PostSync
- SyncFail

For: DB migration, validation, notifications.

## Sync Waves

Order resources within sync:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"   # before main
```

For: deploy DB before app, etc.

## Diff Detection

ArgoCD continuously polls (~3 min):
- Fetch Git
- Render
- Compare with cluster

If differs: OutOfSync.

Then automated sync (if configured) or manual.

## Webhook (Faster)

Git webhook → ArgoCD → immediate sync (instead of polling).

```bash
# GitHub
https://argocd.example.com/api/webhook
```

For: low-latency deploys.

## Notifications

```yaml
# argocd-notifications
triggers:
- name: on-sync-failed
  condition: app.status.operationState.phase in ['Error', 'Failed']
  template: app-sync-failed

templates:
- name: app-sync-failed
  slack:
    message: ":warning: {{.app.metadata.name}} sync failed"
```

For: Slack, email, webhook on events.

## SSO

OIDC integration:
```yaml
oidc.config: |
  issuer: https://auth.example.com
  clientID: argocd
  clientSecret: $oidc.clientSecret
```

For: single sign-on; group-based RBAC.

## Resource Health

ArgoCD evaluates health:
- Deployment: progressing → healthy when rollout complete
- Service: always healthy
- Custom: Lua scripts per CRD

For CRDs:
```yaml
resource.customizations:
  example.com/MyResource:
    health.lua: |
      hs = {}
      if obj.status ~= nil then
        if obj.status.phase == "Ready" then
          hs.status = "Healthy"
        else
          hs.status = "Progressing"
        end
      end
      return hs
```

## Multi-Source

Combine sources:
```yaml
sources:
- repoURL: https://github.com/me/chart
  chart: my-chart
  targetRevision: 1.0.0
  helm:
    valueFiles:
    - $values/values-prod.yaml
- repoURL: https://github.com/me/values
  ref: values
  targetRevision: main
```

Chart from one repo; values from another.

## Drift Handling

```
selfHeal: true   # revert manual changes
selfHeal: false  # alert; don't fix
```

For: tier-0 production, sometimes manual fix needed.

## Limitations

- Default: 3-min polling (use webhook)
- Single Git source per app (use multi-source for some)
- CRD health needs Lua scripts

## ApplicationSet

Template + generator for many Applications:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-apps
spec:
  generators:
  - list:
      elements:
      - name: app-a
        env: dev
      - name: app-b
        env: prod
  template:
    metadata:
      name: '{{name}}-{{env}}'
    spec:
      destination:
        namespace: '{{env}}'
```

For: deploy same app to many envs / clusters.

## App of Apps

One root Application containing other Applications:
```
root-app
├── app-a (namespace-1)
├── app-b (namespace-2)
└── app-c (namespace-3)
```

Bootstrap whole cluster from single ref.

## Best Practices

- Automated sync + prune + selfHeal
- Webhook for fast sync
- Notifications
- RBAC per project
- Multi-cluster managed centrally
- ApplicationSet for many envs

## Common Mistakes

- No selfHeal (drift unchecked)
- No prune (orphans)
- Wide RBAC
- Plain credentials in Git
- No notifications

## Operations

```bash
# Status
argocd app get my-app

# Force sync
argocd app sync my-app --force

# Rollback
argocd app rollback my-app REVISION

# Refresh (re-fetch Git)
argocd app get my-app --refresh
```

## Quick Refs

```bash
# Apply Application
kubectl apply -f app.yaml -n argocd

# CLI
argocd app list
argocd app sync NAME
argocd app diff NAME

# UI
https://argocd.example.com
```

## Interview Prep

**Mid**: "What is GitOps."

**Senior**: "ArgoCD architecture."

**Staff**: "Multi-cluster GitOps."

## Next Topic

→ [T02 — Flux v2](T02-Flux.md)
