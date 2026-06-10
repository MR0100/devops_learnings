# L13/C11/T03 — Helm 3 Architecture (No Tiller)

## Learning Objectives

- Understand Helm 3 design
- Migrate from Helm 2

## Helm 3 (Current)

Client-only. No server-side component (no Tiller).

Architecture:
- `helm` CLI on your machine (or CI)
- Calls K8s API directly
- Releases stored as Secrets in target namespace

## vs Helm 2 (Legacy)

Helm 2 had Tiller (server pod):
- Pod with cluster-admin (security risk)
- Single point of failure
- Sync state between client + Tiller

Helm 3 removed Tiller. Better security + simpler.

If running Helm 2: migrate. Tiller deprecated since 2020.

## Release Storage

Each release = a Secret:
```bash
kubectl get secrets -n my-namespace
# sh.helm.release.v1.my-release.v1
# sh.helm.release.v1.my-release.v2   (after upgrade)
```

Per upgrade: new Secret. Historic for rollback.

## How Install Works

```
helm install my-release ./mychart -n my-namespace
↓
Render templates locally
↓
Apply manifests to K8s (via kubeconfig)
↓
Save release Secret in my-namespace
```

## How Upgrade Works

```
helm upgrade my-release ./mychart
↓
Render templates with new values
↓
Compute 3-way merge (old release, new, current cluster state)
↓
Apply changes
↓
Save new release Secret (incremented version)
```

## 3-Way Merge

When upgrading:
- Original state: previous release
- Desired state: new chart + values
- Live state: actual in cluster (may have manual changes)

Helm computes patch.

If conflict: warning or fail.

## RBAC Required

Helm uses your kubeconfig + RBAC.

For install/upgrade: needs to create/update target resources.

For multi-tenant: per-namespace RBAC.

## CLI Auth

```bash
helm version
# Helm uses ~/.kube/config by default
```

Or:
```bash
helm install --kubeconfig=/path/to/kube.config ...
```

## Namespaces

```bash
helm install my-release ./mychart -n production --create-namespace
```

Per-release namespace. Best practice.

`Release.Namespace` available in templates.

## List Releases

```bash
helm list -n production
# all releases in namespace
helm list -A
# all releases all namespaces
```

## History

```bash
helm history my-release -n production
# REVISION  STATUS    CHART          DESCRIPTION
# 1         deployed  mychart-0.1.0  Install complete
# 2         deployed  mychart-0.2.0  Upgrade complete
```

## Rollback

```bash
helm rollback my-release 1 -n production
```

Revert to revision 1.

## Uninstall

```bash
helm uninstall my-release -n production
```

Deletes resources + release Secret.

`--keep-history` preserves Secret (for rollback to recreate).

## Hooks

Annotations make resources run as hooks:
```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": before-hook-creation
```

Phases:
- pre-install
- post-install
- pre-upgrade
- post-upgrade
- pre-delete
- post-delete
- pre-rollback
- post-rollback
- test

Hook resources NOT tracked in release (separate lifecycle).

## Hook Use Cases

- Schema migration before upgrade
- Backup before install
- Run smoke test (test hook)
- Custom validation

## Migration from Helm 2

Tools:
- helm-2to3 plugin

Steps:
1. Backup Helm 2 state (Tiller releases)
2. Convert to Helm 3 (per-namespace Secrets)
3. Remove Tiller

```bash
helm plugin install https://github.com/helm/helm-2to3
helm 2to3 convert RELEASE_NAME
```

## Threading

Helm 3 is single-threaded. Concurrent installs from same client may conflict.

For CI: ensure sequential.

## Local State

`~/.config/helm/`:
- repositories.yaml
- registry.json

Per-user.

For CI: ephemeral.

## Releases per Workload

One release = one chart + values. For 50 apps: 50 releases (or umbrella chart).

Common pattern: 1 release per app per env.

## helm template

Render without installing:
```bash
helm template my-release ./mychart > manifests.yaml
kubectl apply -f manifests.yaml
```

For: dry-run, GitOps (Argo CD with Helm template).

For ArgoCD: uses `helm template` typically; Argo manages release.

## helm install --dry-run

Renders + validates against API server, doesn't apply:
```bash
helm install my-release ./mychart --dry-run --debug
```

## Lifecycle

Install:
1. Resolve dependencies
2. Render templates
3. Validate (schema, K8s)
4. Apply (in order: namespaces, then resources)
5. Wait for resources Ready (if --wait)
6. Run post-install hooks
7. Save Secret

Upgrade similar.

Rollback: applies older revision's manifests + saves Secret.

## --wait + --timeout

```bash
helm install my-release ./mychart --wait --timeout 5m
```

Waits for all resources Ready before returning.

For: deploy-then-verify scripts.

## --atomic

If install fails: auto-rollback.

```bash
helm install my-release ./mychart --atomic --timeout 5m
```

Good for CI.

## Resource Order

Helm applies in fixed order:
- Namespace
- NetworkPolicy
- ResourceQuota
- ServiceAccount
- Secret
- ConfigMap
- StorageClass
- PV / PVC
- CRD
- Custom Resources
- ClusterRole / ClusterRoleBinding
- Role / RoleBinding
- Service
- DaemonSet / Deployment / etc.
- Ingress

For dependencies (e.g., ConfigMap before Deployment).

## Server-Side Apply

Helm 3 uses client-side apply. Newer (3.13+) optionally server-side:
```bash
helm install ... --server-side
```

For: GitOps compatibility.

## Plugins

Extend Helm:
```bash
helm plugin install https://github.com/databus23/helm-diff
helm diff upgrade my-release ./mychart
```

Common:
- helm-diff: preview changes
- helm-secrets: SOPS integration
- helm-2to3: migration
- helm-git: install from Git

## Best Practices

- Helm 3 (not 2)
- Per-namespace releases
- --atomic in CI
- --wait for verification
- helm-diff before upgrade
- helmfile for many releases
- GitOps with Argo / Flux

## Common Mistakes

- Helm 2 still in use
- Hardcoded namespace
- No --wait (race conditions)
- Forgot --atomic (broken state)
- Manual changes (3-way merge surprises)

## Comparison with Other Tools

| | Helm | Kustomize | jsonnet | Tanka |
|---|---|---|---|---|
| Templating | Yes (Go) | No (overlays) | Yes (Jsonnet) | Yes |
| Native K8s | No (CRDs no) | Yes | No | No |
| Release tracking | Yes | No | No | Yes |
| Versioning | Yes | Manual | Manual | Yes |
| Popularity | Highest | High | Niche | Niche |

For most: Helm.
For overlay: Kustomize.

## GitOps Use

ArgoCD + Helm:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
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

ArgoCD installs chart; manages.

## helmfile + GitOps

For declarative many-releases:
```bash
helmfile apply
```

Or: helmfile committed to Git; ArgoCD syncs.

## Inspection

```bash
helm get values my-release
helm get manifest my-release
helm get notes my-release
helm get hooks my-release
helm get all my-release
```

## Quick Refs

```bash
helm install / upgrade / uninstall
helm list
helm history
helm rollback REV
helm get VALUES|MANIFEST|...

helm template (render)
helm lint (validate)
helm dependency update
```

## Interview Prep

**Mid**: "Helm 3 vs Helm 2."

**Senior**: "How upgrade works (3-way merge)."

**Staff**: "Helm + GitOps strategy."

## Next Topic

→ [T04 — Best Practices](T04-Best-Practices.md)
