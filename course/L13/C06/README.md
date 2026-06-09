# L13/C06 — Security

## Topics

- **T01 RBAC Deep Dive** — Role/ClusterRole + RoleBinding/ClusterRoleBinding. Verbs (get, list, watch, create, update, patch, delete, deletecollection). Resources, subresources (e.g., pods/exec). Use aggregated ClusterRoles for extension.
- **T02 Service Accounts & Token Volumes** — Each pod has an SA. Token is short-lived projected volume (1.21+). For external cloud auth: IRSA (EKS), Workload Identity (GKE), Federated Identity (AKS).
- **T03 Pod Security Standards** — Replaces PSP (removed in 1.25). Profiles: privileged, baseline, restricted. Applied per-namespace via labels.
- **T04 NetworkPolicies** — L3/L4 firewall. Default-deny ingress + egress per namespace, then allow specific. Requires NetworkPolicy-capable CNI.
- **T05 Secrets Encryption at Rest** — `EncryptionConfiguration` with KMS provider. Without this, etcd backups leak secrets.
- **T06 OPA Gatekeeper & Kyverno** — Policy engines via validating admission webhooks. Block disallowed configs (no privileged pods, must have resource limits, etc.)
- **T07 Image Pull Secrets, Image Policy** — Private registries via Secret of type docker-registry. Sign images with Cosign; verify with policy controller (Sigstore Policy Controller, Connaisseur).

## RBAC Quick Template

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: alice-pod-reader
  namespace: dev
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## Pod Security Standard Profiles

| Profile | Allows | Blocks |
|---|---|---|
| privileged | Everything (cluster admins, system) | Nothing |
| baseline | Most defaults | hostNetwork, hostPID, privileged, hostPath |
| restricted | Hardened | runAsRoot, capabilities (must drop ALL), seccomp RuntimeDefault required |

```yaml
# Per-namespace
apiVersion: v1
kind: Namespace
metadata:
  name: my-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Interview Themes

- "How does RBAC work?"
- "How would you prevent privileged pods from being created?"
- "Encryption at rest — what does it cover?"
- "Compare Gatekeeper and Kyverno"
