# L13/C06/T01 — RBAC Deep Dive

## Learning Objectives

- Design RBAC for cluster
- Apply least privilege

## RBAC

Role-Based Access Control. Decides who can do what:
- **Principal**: User, Group, ServiceAccount
- **Verb**: get, list, watch, create, update, patch, delete, deletecollection
- **Resource**: pods, deployments, secrets, etc.

## Four Resources

| | Scope | Permissions | Binding |
|---|---|---|---|
| Role | namespace | rules | RoleBinding |
| ClusterRole | cluster-wide | rules | ClusterRoleBinding (or RoleBinding) |
| RoleBinding | namespace | binds Role to subjects | n/a |
| ClusterRoleBinding | cluster-wide | binds ClusterRole | n/a |

## Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
```

Namespace-scoped.

## RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: dev
  name: alice-pod-reader
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

Binds Role to user/SA/group in namespace.

## ClusterRole

Cluster-wide:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
```

Used for:
- Cluster-scoped resources (nodes, PVs, namespaces)
- Same role in many namespaces (bind via RoleBinding per ns)
- Aggregate ClusterRoles

## ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admins
subjects:
- kind: Group
  name: cluster-admins
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

Cluster-wide grant.

## ClusterRole + RoleBinding

ClusterRole can be bound via RoleBinding (restricts to one namespace):
```yaml
kind: RoleBinding
metadata:
  namespace: dev
subjects: [...]
roleRef:
  kind: ClusterRole       # using cluster role
  name: secret-reader
```

User can read secrets only in `dev`. Cluster role reused.

## API Groups

- `""` (core): pods, services, configmaps, secrets, namespaces
- `apps`: deployments, replicasets, statefulsets, daemonsets
- `batch`: jobs, cronjobs
- `networking.k8s.io`: ingresses, networkpolicies
- `rbac.authorization.k8s.io`: roles, rolebindings
- `storage.k8s.io`: storageclasses

Plus CRDs (their own API groups).

## Verbs

| Verb | Effect |
|---|---|
| get | Read one |
| list | Read collection |
| watch | Stream changes |
| create | New |
| update | Replace |
| patch | Modify |
| delete | Remove |
| deletecollection | Delete many |

Plus subresource verbs.

## Subresources

```yaml
resources: ["pods/exec", "pods/log", "pods/portforward"]
verbs: ["create", "get"]
```

For:
- `pods/exec`: kubectl exec
- `pods/log`: kubectl logs
- `pods/portforward`: kubectl port-forward
- `services/proxy`: kubectl proxy
- `*/status`: status updates

## Resource Names

Restrict to specific resources:
```yaml
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["my-secret"]
  verbs: ["get"]
```

`list` doesn't honor resourceNames (returns all in namespace). Use only with get/update/patch/delete.

## Subjects

```yaml
subjects:
- kind: User
  name: alice
- kind: Group
  name: developers
- kind: ServiceAccount
  name: my-app
  namespace: default
```

User/Group: from external auth (OIDC, certs).
ServiceAccount: in-cluster identity.

## Default ClusterRoles

Built-in:
- `cluster-admin`: full access
- `admin`: namespace admin (no cluster-wide)
- `edit`: read/write within namespace, but not RBAC
- `view`: read-only in namespace

```bash
kubectl get clusterrole | head
```

For common patterns: use these instead of custom.

## Aggregated ClusterRoles

Combine ClusterRoles via labels:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
  labels:
    rbac.authorization.k8s.io/aggregate-to-view: "true"
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

`view` ClusterRole auto-aggregates this via `aggregationRule`.

For extending built-ins.

## Wildcards

```yaml
verbs: ["*"]
resources: ["*"]
apiGroups: ["*"]
```

All. Powerful; dangerous. Avoid except for cluster-admin.

## Checking Permissions

```bash
# Can I do X?
kubectl auth can-i get pods --namespace=prod
kubectl auth can-i delete deployments
kubectl auth can-i '*' '*'   # admin?

# As another user
kubectl auth can-i list secrets --as=alice
kubectl auth can-i list secrets --as=system:serviceaccount:default:my-sa

# All my permissions
kubectl auth can-i --list
```

## kubectl who-can (plugin)

```bash
kubectl who-can get secrets --namespace=prod
# Shows all subjects with the permission
```

Install: `kubectl krew install who-can`.

## RBAC for ServiceAccounts

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

Pod uses SA → inherits permissions.

## SA Auto-Mount

By default, SA token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`.

To disable:
```yaml
spec:
  automountServiceAccountToken: false
```

For pods not needing API access.

## Group Membership

Cert subject's `O=` field becomes group:
```
CN=alice/O=developers
```

`alice` is User; `developers` is Group.

For OIDC: groups claim mapped.

## Least Privilege

Per app:
- Specific verbs
- Specific resources
- Specific resourceNames (where applicable)
- Specific namespace

Avoid:
- `cluster-admin` to apps
- `*` everywhere
- Wide ClusterRoleBindings

## Common Patterns

### Read-Only Namespace
```yaml
kind: RoleBinding
roleRef:
  kind: ClusterRole
  name: view
subjects:
- kind: Group
  name: viewers
```

### CI/CD Deploy
```yaml
kind: Role
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "update", "patch"]
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "create", "update", "patch"]
```

For CI deploying to namespace.

### Cluster Operator
```yaml
kind: ClusterRole
rules:
- apiGroups: ["custom.io"]
  resources: ["myresources"]
  verbs: ["*"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

For operator managing CR + child resources.

## RBAC Discovery

```bash
# All roles in namespace
kubectl get role,rolebinding -n dev

# All cluster roles
kubectl get clusterrole

# Bindings
kubectl get clusterrolebinding

# Who has cluster-admin?
kubectl get clusterrolebinding -o json | jq '.items[] | select(.roleRef.name=="cluster-admin")'
```

## RBAC for Custom Resources

Auto: `*` rules NOT applied to CRDs (must specify):
```yaml
rules:
- apiGroups: ["custom.io"]
  resources: ["myresources"]
  verbs: ["*"]
```

Without: SA can't manage CR even if has `*` `*`.

## Audit

API Server audit log records every API call + RBAC decision.

For: detect anomalous access; troubleshoot denials.

```bash
# When request denied
kubectl get pods
# Error: User "alice" cannot list pods in namespace "default"
```

Check binding chain:
```bash
kubectl auth can-i list pods --as=alice
kubectl get rolebinding,clusterrolebinding -A -o json | jq '.items[] | select(.subjects[]?.name == "alice")'
```

## Anti-Patterns

- `cluster-admin` for apps
- ClusterRoleBinding when RoleBinding sufficient
- Wide wildcards
- SA in `default` namespace bound to `cluster-admin`
- No periodic audit

## Best Practices

- Built-in roles where possible (view, edit, admin)
- Custom Role per app, least privilege
- SA per app (not shared)
- Aggregated ClusterRoles for extension
- Audit quarterly
- Tooling: rbac-lookup, kubectl-who-can
- automountServiceAccountToken: false for non-API pods

## Common Mistakes

- ClusterRoleBinding when RoleBinding works
- Forgetting subresources (pods/log)
- Wildcards for "easier"
- Resource names with list (doesn't filter)
- No group structure

## RBAC + Federation

For SSO:
- OIDC provider → groups claim
- ClusterRoleBindings on groups (not individual users)
- Add/remove from group in IdP

For: scalable RBAC.

## RBAC for kubectl Users

Users authenticated via:
- Client certificate
- OIDC token
- Webhook
- Bootstrap token

Then RBAC checks per request.

## Quick Refs

```bash
# Check
kubectl auth can-i get pods
kubectl auth can-i --list

# Apply
kubectl apply -f role.yaml -f rolebinding.yaml

# View
kubectl describe rolebinding alice-pod-reader

# Plugin
kubectl who-can get secrets -n prod
```

## Interview Prep

**Junior**: "What is RBAC?"

**Mid**: "Role vs ClusterRole."

**Senior**: "Design RBAC for multi-tenant cluster."

**Staff**: "Audit + tighten RBAC org-wide."

## Next Topic

→ [T02 — Service Accounts & Token Volumes](T02-ServiceAccounts.md)
