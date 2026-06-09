# L08/C02/T05 — IAM Roles for Service Accounts (IRSA)

## Learning Objectives

- Use IRSA in EKS
- Avoid pod-level credential issues

## Pre-IRSA

EKS pods inherited node's IAM role. Problems:
- All pods on a node had same permissions
- Hard to scope per-pod
- One pod compromised = node-level access

## IRSA

K8s ServiceAccount mapped to AWS IAM role via OIDC. Pod assumes role; gets per-pod creds.

## How It Works

1. EKS cluster has OIDC provider URL
2. AWS IAM trusts this OIDC provider
3. IAM role's trust policy allows ServiceAccount X in namespace Y
4. Pod uses ServiceAccount X
5. SDK reads OIDC token from disk
6. STS validates token; returns temp creds

## Setup

### Step 1: Create OIDC Provider for Cluster
```bash
eksctl utils associate-iam-oidc-provider --cluster mycluster --approve
```

Or manually create IAM OIDC identity provider with cluster's OIDC URL.

### Step 2: Create IAM Role

Trust policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:sub": "system:serviceaccount:my-namespace:my-sa",
        "oidc.eks.us-east-1.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:aud": "sts.amazonaws.com"
      }
    }
  }]
}
```

Attach permission policy (e.g., S3 read).

### Step 3: Annotate ServiceAccount
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-sa
  namespace: my-namespace
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/MyAppRole
```

### Step 4: Use in Pod
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      serviceAccountName: my-sa
      containers: [...]
```

### Step 5: Done

SDK in pod automatically uses IRSA creds.

## eksctl Shortcut

```bash
eksctl create iamserviceaccount \
  --cluster mycluster \
  --namespace my-namespace \
  --name my-sa \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve
```

Creates IAM role + SA + annotation. One command.

## How Pod Knows

Mutating webhook (added by EKS): injects:
- Env vars: `AWS_ROLE_ARN`, `AWS_WEB_IDENTITY_TOKEN_FILE`
- Volume mount: projected token at `/var/run/secrets/eks.amazonaws.com/serviceaccount/token`

SDK reads these; calls `sts:AssumeRoleWithWebIdentity`; gets creds.

## Token Rotation

Projected token rotates automatically (typically hourly).

## Pod Identity (Newer)

EKS Pod Identity (2023+): alternative to IRSA. Pod identity agent on each node; simpler config.

```bash
aws eks create-pod-identity-association \
  --cluster-name mycluster \
  --namespace my-ns \
  --service-account my-sa \
  --role-arn arn:aws:iam::123:role/MyAppRole
```

No annotations on SA needed. Same IAM role; cleaner.

Both supported; IRSA still works.

## When Pod Identity vs IRSA

| Feature | IRSA | Pod Identity |
|---|---|---|
| Setup | More steps | Simpler |
| Role trust | Cluster-specific | Reusable |
| Cross-account | Yes | Yes |
| Audience | Each SA distinct | Common |
| Newer | 2019 | 2023 |

Pod Identity recommended for new.

## Cross-Account

Role in account B; pod in EKS in account A:
- B's role trusts A's OIDC provider
- Sub claim restricts which SA in A

Same mechanism; different accounts.

## Multiple Roles per Pod

One SA → one role primarily. For multiple:
- Re-assume via sts:AssumeRole (chain)
- Or use multiple SAs (one per role; switch in code)

## Limitations

- 1 hour default session
  - Extend with `aws sts assume-role-with-web-identity --duration-seconds N` (up to 12h)
- VPC required for STS endpoint or internet access
- OIDC provider URL has thumbprint; rotates rarely

## Troubleshooting

### Pod can't access AWS
1. SA annotation correct?
2. IAM role trust policy matches `system:serviceaccount:ns:sa`?
3. OIDC provider associated with cluster?
4. Pod actually using the SA?
5. SDK version supports IRSA?

```bash
kubectl describe pod my-pod
# Check env vars AWS_ROLE_ARN
```

```bash
kubectl exec my-pod -- env | grep AWS
```

### STS endpoint unreachable
Public STS endpoint or VPC endpoint needed. Private cluster without endpoint: fails.

## Best Practices

- One IAM role per workload (least privilege)
- Tight sub condition in trust policy
- IRSA + Network Policy + PSA for layered security
- Audit IAM role permissions
- Rotate / review periodically

## Alternative: Node IAM Role

Node group has IAM role; all pods inherit. Wide blast radius.

Use only for cluster-level (CNI, CSI). For workloads: IRSA / Pod Identity.

## kube2iam / kiam (Deprecated)

Pre-IRSA hacks; proxied metadata. Don't use anymore.

## Common Mistakes

- Trust policy missing or wrong sub
- OIDC provider not created
- SA annotation typo
- Using node role instead of IRSA
- Permissions too broad

## Audit

Find pods with what roles:
```bash
kubectl get sa -A -o yaml | grep role-arn
```

Run Access Analyzer to find overly permissive.

## Multi-Cluster

Same IAM role usable from multiple EKS clusters by:
- Adding each cluster's OIDC provider to trust
- Or use IAM Roles Anywhere for non-EKS K8s

## Interview Prep

**Mid**: "What does IRSA do?"

**Senior**: "IRSA setup steps."

**Staff**: "IRSA vs Pod Identity vs node role."

## Next Topic

→ [T06 — Permission Boundaries & SCPs](T06-Permission-Boundaries-SCPs.md)
