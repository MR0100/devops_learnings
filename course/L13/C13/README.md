# L13/C13 — GitOps

## Topics

- **T01 ArgoCD Deep Dive** — Pull-based GitOps. App = Git repo + path + cluster + namespace. Application controllers reconcile. Web UI, RBAC, SSO.
- **T02 Flux v2** — Modular: Source Controller (Git/Helm), Kustomize Controller, Helm Controller, Notification Controller. Heavier on Kubernetes-native CRDs.
- **T03 App-of-Apps Pattern** — One root Application that creates all other Applications. Bootstrap entire cluster from a single Git ref.
- **T04 Sync Strategies, Hooks, Waves** — Manual vs automated sync. Pre/post sync hooks (e.g., DB migration before app). Sync waves order resources.

## GitOps Principles

1. **Declarative**: desired state in Git
2. **Versioned + Immutable**: history is the audit trail
3. **Pulled automatically**: operator reconciles, no CI pushes to cluster
4. **Continuously reconciled**: drift detection + correction

## ArgoCD App Example

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
    targetRevision: HEAD
    path: deploy/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

## App-of-Apps

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bootstrap
spec:
  source:
    repoURL: ...
    path: bootstrap/apps  # contains many Application manifests
```

## ArgoCD vs Flux

| | ArgoCD | Flux v2 |
|---|---|---|
| UI | Rich web UI | None (CLI / 3rd party) |
| Push vs pull | Pull | Pull |
| Multi-cluster | Yes | Yes |
| Multi-source | Yes (1 source per app, multi via dependencies) | Multi-source apps |
| Architecture | Monolithic app | Microservice (5+ controllers) |
| Best for | Visibility, team UI | Pure GitOps purists, scaled fleet |

## Recommended Reading

- "Operating Patterns for ArgoCD" docs
- Weaveworks GitOps principles
- ArgoCD best practices guide

## Interview Themes

- "What is GitOps and why does it matter?"
- "Compare ArgoCD and Flux"
- "How do you bootstrap a new K8s cluster with GitOps?"
- "Sync waves — what problem do they solve?"
