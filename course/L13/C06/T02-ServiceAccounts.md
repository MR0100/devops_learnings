# L13/C06/T02 — Service Accounts & Token Volumes

## Learning Objectives

- Use ServiceAccounts correctly
- Configure cloud federation

## ServiceAccount

Identity for processes running in pods.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: default
```

Used for:
- Pod's identity to K8s API
- Bridge to cloud IAM (IRSA, Workload Identity)
- RBAC subject

## Default SA

Every namespace has `default` SA. Pods without `serviceAccountName` use it.

Don't grant cluster-admin to default. Instead:
- Use explicit SAs per app
- Default SA minimal permissions

## Setting SA on Pod

```yaml
spec:
  serviceAccountName: my-app
  containers:
  - name: app
    image: ...
```

## Token Projection

Modern K8s (1.21+): tokens are projected, short-lived, audience-bound:
- Token file at `/var/run/secrets/kubernetes.io/serviceaccount/token`
- Token rotates (~1 hour default)
- Refreshed by kubelet
- Tied to specific audience

Legacy (pre-1.21): long-lived tokens in Secret. Deprecated.

## Disable Auto-Mount

If pod doesn't need K8s API:
```yaml
spec:
  automountServiceAccountToken: false
  ...
```

Or on SA:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
automountServiceAccountToken: false
```

For: workloads that don't use K8s API. Reduces attack surface.

## Token Volume Projection

For custom audience / expiration:
```yaml
spec:
  serviceAccountName: my-app
  containers:
  - name: app
    volumeMounts:
    - name: token
      mountPath: /var/run/secrets/tokens
  volumes:
  - name: token
    projected:
      sources:
      - serviceAccountToken:
          path: my-token
          expirationSeconds: 600
          audience: my-app.example.com
```

For: external systems verifying token (e.g., Vault).

## SA Token Secret (Legacy)

Pre-1.24: each SA auto-creates a Secret with long-lived token. Removed in 1.24+ for security.

If needed (rare):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-token
  annotations:
    kubernetes.io/service-account.name: my-app
type: kubernetes.io/service-account-token
```

For: legacy external integrations.

## Cross-Namespace SAs

SA is namespaced; binding can span:
```yaml
kind: ClusterRoleBinding
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: monitoring
```

Used by monitoring tools (Prometheus) reading cluster-wide.

## IRSA (EKS)

K8s SA → AWS IAM role via OIDC:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/MyAppRole
```

Pod using this SA:
1. Token mounted (projected, audience=sts.amazonaws.com)
2. AWS SDK reads token + role ARN
3. Calls STS AssumeRoleWithWebIdentity
4. Gets temp AWS creds (auto-refreshed)

For: AWS API access from pods without static keys.

Detailed in L08/C02/T05.

## EKS Pod Identity (Newer)

Alternative to IRSA. Simpler:
```bash
aws eks create-pod-identity-association \
  --cluster-name mycluster \
  --namespace my-ns \
  --service-account my-app \
  --role-arn arn:aws:iam::123:role/MyAppRole
```

No SA annotation needed.

## Workload Identity (GKE)

K8s SA ↔ GCP SA:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    iam.gke.io/gcp-service-account: my-app@project.iam.gserviceaccount.com
```

Pod inherits GCP SA permissions.

## Workload Identity (AKS)

K8s SA → Azure AD identity:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    azure.workload.identity/client-id: <client-id>
```

Pod gets Azure AD token.

## Vault Integration

Vault Auth via SA token:
```bash
vault write auth/kubernetes/login role=my-role jwt=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
```

Vault validates token with K8s API; returns Vault token.

Or via Vault Agent (sidecar) handles automatically.

## Pod with Multiple Tokens

```yaml
spec:
  volumes:
  - name: vault-token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          audience: vault.example.com
  - name: aws-token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          audience: sts.amazonaws.com
```

For: multi-cloud / multi-system access.

## TokenRequest API

Programmatic token creation:
```bash
kubectl create token my-app --duration=1h --audience=my-app.example.com
```

For: external CI tools needing temporary access.

## SA RBAC

SA without explicit RBAC: cannot access API.

```yaml
kind: RoleBinding
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
```

## SA Per Workload

Best practice: one SA per workload:
- Distinct permissions
- Audit per workload
- Rotate independently

vs shared SA: blast radius huge.

## Image Pull Secrets via SA

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
imagePullSecrets:
- name: my-registry-secret
```

All pods using SA inherit pull secret. Useful for private registries.

For ECR: better to use IRSA / Pod Identity for ECR auth.

## Audit SA Usage

```bash
# All SAs
kubectl get sa -A

# SA in use by pods
kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.serviceAccountName}{"\n"}{end}' | sort -u

# Bindings for SA
kubectl get rolebinding,clusterrolebinding -A -o json | jq '.items[] | select(.subjects[]?.kind == "ServiceAccount")'
```

## Deletion

Deleting SA:
- Bindings remain (orphaned)
- Pods can still run (token may continue working until expiration)
- New pods using deleted SA: stuck

Clean up: delete bindings too.

## Security Considerations

SA tokens:
- Mounted into pod
- Anyone exec'ing pod can read
- Compromised pod = compromised SA permissions

Mitigate:
- Minimal RBAC
- Pod Security Standards (no privileged, no host mounts)
- Image scanning (no malicious code)
- Network policies (limit egress)

## Project SAs

For project-scoped resources:
- Per-project namespace
- SA per app in namespace
- RBAC within namespace

For multi-tenant.

## kubectl as User vs SA

```bash
# As user (from kubeconfig)
kubectl get pods

# As SA (impersonation)
kubectl get pods --as=system:serviceaccount:default:my-app

# Using SA token
TOKEN=$(kubectl create token my-app --duration=10m)
kubectl --token=$TOKEN get pods
```

## Common Mistakes

- Default SA cluster-admin
- Shared SA across apps
- Long-lived tokens (use projection)
- automount enabled when not needed
- No RBAC binding (SA can't do anything)
- IRSA annotation typo (no AWS access)

## Best Practices

- One SA per workload
- automountServiceAccountToken: false for non-API pods
- Minimal RBAC
- IRSA/Workload Identity for cloud
- Short-lived token projection
- Audit annually
- Disable legacy long-lived tokens

## Pod-Level Token Refresh

Token rotated by kubelet:
- Re-projected into volume
- App reads file each time (or watches)
- SDK handles refresh automatically

## Container's Identity

Inside pod:
```bash
cat /var/run/secrets/kubernetes.io/serviceaccount/token
cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

For API calls:
```python
import requests

token = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read()
ca = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
ns = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

r = requests.get(
    f"https://kubernetes.default.svc/api/v1/namespaces/{ns}/pods",
    headers={"Authorization": f"Bearer {token}"},
    verify=ca,
)
```

## OIDC Discovery

K8s exposes OIDC issuer at:
```
https://<cluster>.<region>.eks.amazonaws.com/id/<unique>
```

For external systems (AWS IAM, Vault) to validate tokens.

## Federated Identity Flow (IRSA)

1. Pod token (audience=sts.amazonaws.com) projected
2. AWS SDK reads AWS_ROLE_ARN env
3. SDK calls STS AssumeRoleWithWebIdentity with token
4. STS validates token (calls EKS OIDC issuer)
5. STS returns temp AWS creds
6. SDK uses creds; refreshes periodically

Zero static credentials.

## Quick Refs

```bash
# Create SA
kubectl create serviceaccount my-app

# Bind to role
kubectl create rolebinding my-app-binding --serviceaccount=default:my-app --role=pod-reader

# Token
kubectl create token my-app --duration=1h

# Pod uses SA
kubectl run pod1 --image=nginx --serviceaccount=my-app

# Check
kubectl get sa my-app -o yaml
kubectl auth can-i get pods --as=system:serviceaccount:default:my-app
```

## Interview Prep

**Mid**: "What is ServiceAccount."

**Senior**: "IRSA flow."

**Staff**: "Multi-cloud SA federation."

## Next Topic

→ [T03 — Pod Security Standards](T03-PodSecurityStandards.md)
