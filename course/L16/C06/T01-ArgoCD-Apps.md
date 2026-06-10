# L16/C06/T01 — ArgoCD: Apps, ApplicationSets, Projects

## Learning Objectives

- Use ArgoCD for GitOps
- Scale via ApplicationSet

## ArgoCD

GitOps CD for K8s:
- Pulls from Git
- Reconciles cluster
- UI / CLI / API
- Multi-cluster

## Install

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/me/manifests.git
    targetRevision: main
    path: myapp/
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

For: one app.

## Sync

```bash
# Manual
argocd app sync myapp

# Automated (above)
```

ArgoCD pulls Git → applies to cluster.

## Self-Heal

If cluster drifts:
- ArgoCD detects
- Re-applies Git state

For: no manual touch.

## Prune

Resources removed from Git → deleted from cluster.

Risky for accidental deletes; require opt-in.

## Sources

Multiple:
```yaml
sources:
- repoURL: ...
  path: base/
- repoURL: ...
  path: overlay/
```

For: Kustomize-style.

## Helm

```yaml
source:
  repoURL: ...
  path: charts/
  helm:
    valueFiles:
    - values-prod.yaml
    parameters:
    - name: image.tag
      value: v1.0.0
```

## Kustomize

```yaml
source:
  repoURL: ...
  path: overlays/prod/
  kustomize:
    namePrefix: prod-
```

## ApplicationSet

Generate many Apps:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp-multi-cluster
spec:
  generators:
  - list:
      elements:
      - cluster: dev
        url: https://dev-k8s.example.com
      - cluster: prod
        url: https://prod-k8s.example.com
  template:
    metadata:
      name: '{{cluster}}-myapp'
    spec:
      project: default
      source:
        repoURL: https://github.com/me/manifests.git
        targetRevision: main
        path: myapp/
      destination:
        server: '{{url}}'
        namespace: prod
```

For: same app to many clusters.

## Generators

- List
- Cluster (discovers registered clusters)
- Git (paths in repo)
- Matrix (combine)
- Merge
- PullRequest

```yaml
generators:
- git:
    repoURL: https://github.com/me/manifests.git
    revision: main
    directories:
    - path: '*/'
```

For: app per directory.

## Projects

Group apps:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: myteam
  namespace: argocd
spec:
  sourceRepos:
  - 'https://github.com/myteam/*'
  destinations:
  - namespace: 'myteam-*'
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
  roles:
  - name: deployer
    policies:
    - p, proj:myteam:deployer, applications, sync, myteam/*, allow
```

For: RBAC and policy.

## RBAC

```yaml
data:
  policy.csv: |
    p, role:admin, applications, *, */*, allow
    p, role:developer, applications, get, */*, allow
    g, my-org-team, role:developer
```

For: team-based access.

## SSO

```yaml
url: https://argocd.example.com

oidc.config: |
  name: Okta
  issuer: https://okta.example.com
  clientID: ...
  clientSecret: $oidc.okta.clientSecret
```

## Multi-Cluster

```bash
argocd cluster add CLUSTER_NAME
```

Adds cluster; ArgoCD can deploy to it.

## Notifications

```yaml
data:
  service.slack: |
    token: $slack-token
  trigger.on-sync-succeeded: |
    - description: App synced
      send: [app-sync-succeeded]
      when: app.status.operationState.phase in ['Succeeded']
```

For: alerts.

## Hooks

```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
```

Run before sync.

Phases:
- PreSync
- Sync
- PostSync
- SyncFail

For: migrations, smoke tests.

## Waves

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

Order resources. Wave 1 before wave 2.

## Rollback

```bash
argocd app rollback myapp
```

To previous synced revision.

Or via UI.

## Image Updater

ArgoCD Image Updater:
- Watch registry for new images
- Update manifests in Git
- ArgoCD syncs

For: full GitOps with image automation.

## App of Apps

```
parent-app
  ├─ child-app-1 (via Application CR)
  ├─ child-app-2
  └─ child-app-3
```

Parent manages children. ApplicationSet often better now.

## Best Practices

- Per-team project
- ApplicationSet for multi-cluster
- Auto-sync + self-heal in prod
- Notifications for failures
- SSO
- Branch-based environments (env/dev, env/prod)

## Common Mistakes

- Pruning without care (delete prod)
- Manual cluster changes (drift; ArgoCD reverts)
- No RBAC
- Same Project for all apps

## Quick Refs

```bash
argocd login URL
argocd app list / sync / get / rollback NAME
argocd cluster add CLUSTER
argocd repo add URL

# CR
kubectl get application -n argocd
kubectl get applicationset -n argocd
kubectl get appproject -n argocd
```

## Interview Prep

**Junior**: "What's ArgoCD."

**Mid**: "App + ApplicationSet."

**Senior**: "GitOps at scale."

**Staff**: "Multi-cluster deploy."

## Next Topic

→ [T02 — Sync Hooks & Waves](T02-Sync-Hooks-Waves.md)
