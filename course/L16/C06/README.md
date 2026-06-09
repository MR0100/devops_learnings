# L16/C06 — ArgoCD (Recap from L13)

## Topics

- **T01 Apps, ApplicationSets, Projects** — Core ArgoCD CRDs.
- **T02 Sync Hooks & Waves** — Order resources during sync.

## Application (the unit)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo
    targetRevision: main
    path: deploy/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true       # delete things removed from Git
      selfHeal: true    # revert manual changes
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

## ApplicationSet (template for many Apps)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
spec:
  generators:
    - clusters: {}        # one per cluster
  template:
    metadata:
      name: '{{name}}-addons'
    spec:
      project: default
      source:
        repoURL: https://github.com/org/repo
        path: addons
      destination:
        server: '{{server}}'
        namespace: kube-system
```

Generators: clusters, list, git directories, matrix, merge, pull-request.

## Projects

Group Applications; restrict source repos and destinations:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments
spec:
  sourceRepos:
    - https://github.com/org/payments-*
  destinations:
    - namespace: 'payments-*'
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - { group: '', kind: Namespace }
  namespaceResourceWhitelist:
    - { group: '*', kind: '*' }
```

## Sync Waves

Order resources during sync:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

Lower wave applies first. Useful for: CRDs before CRs; namespaces before resources in them.

## Sync Hooks

Run jobs during sync phases:
- PreSync (e.g., DB migrations)
- Sync (default)
- PostSync (e.g., smoke tests)
- SyncFail (cleanup)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: my-migration-tool
```

## RBAC

```yaml
# ConfigMap argocd-rbac-cm
policy.csv: |
  p, role:payments, applications, sync, payments/*, allow
  p, role:payments, applications, get, payments/*, allow
  g, payments-team, role:payments
```

## Multi-Cluster

ArgoCD can manage many clusters:
```bash
argocd cluster add my-cluster
```

Argo runs in a "central" cluster; manages many.

## When ArgoCD

- GitOps-driven deploys
- Want a UI for status/operators
- Multi-cluster from one place
- Need rich sync semantics

## Interview Themes
- "ApplicationSet — what does it solve?"
- "Sync waves vs hooks"
- "App-of-apps pattern"
- "ArgoCD vs Flux"
