# L13/C13/T03 — App-of-Apps Pattern

## Learning Objectives

- Bootstrap clusters with App-of-Apps
- Manage many apps via one ref

## App-of-Apps

ArgoCD pattern: ONE root Application creates many child Applications.

```
root-app (Application)
├── child-app-1 (Application)
├── child-app-2 (Application)
└── child-app-3 (Application)
```

Each child manages its own workloads.

## Why

- Bootstrap whole cluster from one Git ref
- Disaster recovery: re-apply root → all apps return
- Visibility: see all apps at once
- Lifecycle: per-environment whole-cluster config

## Structure

```
gitops/
├── root/
│   └── root-app.yaml         # root Application
├── apps/
│   ├── monitoring/
│   │   └── app.yaml         # child Application
│   ├── ingress/
│   │   └── app.yaml
│   └── my-app/
│       └── app.yaml
```

## Root Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/me/gitops
    targetRevision: main
    path: apps   # directory of child Applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Root manages contents of `apps/` directory. Each file = Application CR.

## Child Application

apps/monitoring/app.yaml:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: monitoring
  namespace: argocd
spec:
  project: platform
  source:
    repoURL: https://github.com/prometheus-community/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 55.x.x
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## Bootstrap

```bash
# Install ArgoCD
kubectl apply -n argocd -f argocd-install.yaml

# Apply root
kubectl apply -f root-app.yaml

# Root creates children; children create resources
```

Whole cluster comes up.

## ApplicationSet (Modern)

Better pattern than App-of-Apps:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-apps
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://github.com/me/gitops
      revision: main
      directories:
      - path: apps/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/me/gitops
        targetRevision: main
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

For each directory under `apps/`: creates Application.

Add directory → new app auto-created.

## Generators

### List
```yaml
generators:
- list:
    elements:
    - name: app-a
      cluster: prod
    - name: app-b
      cluster: staging
```

### Cluster
```yaml
generators:
- clusters: {}
```

Per-cluster Application.

### Git Directories
```yaml
generators:
- git:
    directories:
    - path: apps/*
```

Per-directory Application.

### Git Files
```yaml
generators:
- git:
    files:
    - path: "apps/*.yaml"
```

Per-file Application.

### Matrix
```yaml
generators:
- matrix:
    generators:
    - clusters: {}
    - git:
        directories:
        - path: apps/*
```

Cross-product: per cluster × per app.

For: deploy all apps to all clusters.

## Per-Cluster Config

```yaml
template:
  spec:
    destination:
      server: '{{server}}'
      namespace: my-app
```

`{{server}}` from cluster generator.

## Per-Environment

```yaml
generators:
- list:
    elements:
    - env: dev
      replicas: 1
    - env: prod
      replicas: 5
template:
  metadata:
    name: 'my-app-{{env}}'
  spec:
    source:
      helm:
        valuesObject:
          replicas: '{{replicas}}'
```

For: parameterized apps.

## App-of-Apps vs ApplicationSet

| | App-of-Apps | ApplicationSet |
|---|---|---|
| Style | Explicit YAML per child | Generator-based |
| Adding app | New YAML + commit | Add directory or list item |
| Dynamic | Less | More |
| Boilerplate | More | Less |
| Used | Earlier | Modern preferred |

For new: ApplicationSet.
For existing simple: App-of-Apps OK.

## Project Per Tier

```yaml
spec:
  project: platform   # for shared services
spec:
  project: prod-team  # for prod team apps
```

Different RBAC; different allowed sources/destinations.

## Sync Order

Children can have priorities:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"   # later
    argocd.argoproj.io/sync-wave: "-1"  # earlier
```

For: deploy infra first, then apps.

## Cluster Bootstrap

Full bootstrap:
1. Provision K8s cluster (Terraform)
2. Install ArgoCD (kubectl)
3. Apply root Application (kubectl)
4. ArgoCD reconciles all children
5. Cluster fully configured

For DR: same process; cluster rebuilt fast.

## Tenancy

Per-team root:
```yaml
# teams/team-a/root.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: team-a-root
spec:
  source:
    repoURL: https://github.com/team-a/manifests
```

Team manages own apps; org has team-level root.

## Best Practices

- ApplicationSet over plain App-of-Apps
- Project per team
- Sync waves for ordering
- Notifications on root + children
- Backup root Git repo
- Tested in non-prod first

## Common Mistakes

- Root too broad (modifying breaks all)
- Children with wide RBAC
- Forgetting CreateNamespace
- Not pruning (orphans)
- One huge ApplicationSet

## Disaster Recovery

Cluster down → rebuild:
1. Terraform creates cluster
2. Install ArgoCD
3. Apply root
4. All apps return

Test annually.

## Multi-Cluster

Root in management cluster manages many target clusters:
```yaml
spec:
  destination:
    server: https://target-cluster.example.com
    namespace: ...
```

For: central management.

## ApplicationSet Examples

### Per-Cluster Same App
```yaml
generators:
- clusters: {}
template:
  metadata:
    name: 'app-{{name}}'
  spec:
    destination:
      server: '{{server}}'
      namespace: default
```

Deploy app to all clusters.

### Per-Environment Different Configs
```yaml
generators:
- list:
    elements:
    - env: dev
      replicas: 1
      cpu: 100m
    - env: prod
      replicas: 5
      cpu: 1
template:
  spec:
    source:
      helm:
        valuesObject:
          replicaCount: '{{replicas}}'
          resources:
            requests:
              cpu: '{{cpu}}'
```

## Inspection

```bash
# All children
argocd app list

# Sync root (cascades)
argocd app sync root

# Health
argocd app get root
```

## Quick Refs

```yaml
# Root Application
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  source:
    path: apps   # directory of children

# ApplicationSet (modern)
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
  - git:
      directories: [{path: apps/*}]
  template: {...}
```

## Interview Prep

**Mid**: "App-of-Apps pattern."

**Senior**: "ApplicationSet generators."

**Staff**: "Bootstrap 50 clusters via ApplicationSet."

## Next Topic

→ [T04 — Sync Strategies, Hooks, Waves](T04-Sync-Hooks-Waves.md)
