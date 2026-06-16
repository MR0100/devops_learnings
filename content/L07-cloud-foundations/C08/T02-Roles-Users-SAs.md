# L07/C08/T02 — Roles vs Users vs Service Accounts

## Learning Objectives

- Pick the right identity type
- Apply per cloud

## Three Identity Categories

| | What |
|---|---|
| User | Human or app with static credentials |
| Role | Identity assumed temporarily |
| Service Account | Identity for non-human (different per cloud) |

## AWS

### IAM User
- Has access keys (long-lived)
- Used for: humans (legacy), some apps
- Modern: avoid; replace with federated user / role

### IAM Role
- Assumed via STS; temp credentials
- Used for:
  - EC2 (instance profile)
  - Lambda (execution role)
  - Cross-account
  - Federated humans

### What about Service Accounts?
AWS doesn't have explicit "service account" type. Equivalent: IAM Role assumed by:
- EC2 instance profile (auto)
- Lambda (auto)
- ECS task role (auto)
- IRSA for EKS pods

## GCP

### User
Google account; person identity.

### Service Account
First-class entity. Email format (`my-sa@project.iam.gserviceaccount.com`). 
- Has identity, keys (rotatable)
- Permissions via roles
- Assumed by GCE VMs (default SA), GKE pods (Workload Identity)
- Impersonable by users

### Workload Identity
GKE: K8s SA → GCP SA mapping. Pods get GCP identity. Like IRSA in EKS.

## Azure

### User
Azure AD account; human or legacy app.

### Service Principal
Equivalent to AWS service account / app identity.

### Managed Identity
- System-assigned: tied to resource lifecycle (created with resource; deleted with it)
- User-assigned: standalone; can be assigned to multiple resources

Like AWS instance profile. No keys to manage.

## K8s Service Accounts

In-cluster identity for pods:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
```

```yaml
spec:
  serviceAccountName: my-app
  containers: [...]
```

K8s ServiceAccount → token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`.

For cluster API access. Combined with RBAC.

## Federating K8s SA to Cloud

### IRSA (AWS)
K8s SA → AWS IAM Role via OIDC. Pod's SA token exchanged for IAM creds.

```yaml
annotations:
  eks.amazonaws.com/role-arn: arn:aws:iam::123:role/MyRole
```

### Workload Identity (GCP)
K8s SA ↔ GCP SA mapping. Pod uses GCP identity natively.

```yaml
annotations:
  iam.gke.io/gcp-service-account: my-sa@project.iam.gserviceaccount.com
```

### Workload Identity (Azure AKS)
K8s SA → Azure AD identity.

## When To Use What

| Use Case | AWS | GCP | Azure |
|---|---|---|---|
| Human via SSO | Federated user (SAML/OIDC) → role | User (Cloud Identity) | User (Azure AD) |
| EC2 / GCE / VM | Instance Profile (role) | Default / custom SA | Managed Identity |
| Lambda / Cloud Function | Execution role | SA | Managed Identity |
| K8s pod | IRSA | Workload Identity | Workload Identity |
| External CI/CD | OIDC → role | Workload Identity Federation | Managed Identity / SP |
| Legacy app on-prem | IAM Roles Anywhere | Workload Identity | SP with cert |

## OIDC Federation

External provider (GitHub Actions, GitLab) → exchange OIDC token for cloud creds.

No static keys! CI/CD can deploy to cloud without secrets.

### GitHub Actions → AWS
```yaml
permissions:
  id-token: write
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123:role/GitHubActionsRole
      aws-region: us-east-1
```

Trust policy on role allows specific GitHub repo / branch.

## Static Keys

When unavoidable:
- Rotate (90 days)
- Store in secret manager
- Audit usage (CloudTrail)
- Restrict via Conditions (IP, time)
- Bound permissions

But mostly: don't use static keys.

## Multi-Factor Auth

- Required for IAM users (root, console)
- Hardware key (YubiKey) for sensitive
- Virtual MFA (Authy, Google Auth)
- Enforced via Condition: `aws:MultiFactorAuthPresent`

## Common Patterns

### CI/CD Deploys to AWS
1. CI has GitHub OIDC token
2. AWS IAM role trusts GitHub OIDC issuer
3. Trust restricted by `sub` claim (specific repo/branch)
4. CI assumes role; gets short-lived creds
5. Deploys

No long-lived secrets in CI.

### App Reads Secrets
1. Pod has K8s SA "my-app"
2. SA → IAM role (IRSA)
3. Role has secretsmanager:GetSecretValue permission
4. App SDK uses IRSA creds
5. Reads secret

### Cross-Account Access
1. User in account A
2. Assumes role in account B (cross-account trust)
3. Acts as role in B
4. Audit logs in B show "assumed from A"

## RBAC vs ABAC

**RBAC**: Role-Based Access Control. "Engineers can read prod logs."

**ABAC**: Attribute-Based Access Control. "Users can read resources tagged with their team."

```json
"Condition": {
  "StringEquals": {
    "aws:ResourceTag/Team": "${aws:PrincipalTag/Team}"
  }
}
```

ABAC scales: don't update policy for every new team/user; tag and trust.

## Identity Lifecycle

Created → Used → Reviewed → Rotated → Disabled → Deleted.

Auto where possible:
- Detect unused after 90 days
- Disable
- Notify owner
- Delete after 30 more

## Common Mistakes

- IAM user for application
- Service Account keys in code
- No MFA on root
- Permissions all `*`
- Long-lived static keys
- No cross-account audit

## Identity Provider

For humans: pick one (Okta, Auth0, Azure AD).
Federate to AWS / GCP / Azure / K8s / SaaS.
Single source of truth.

Cost: ~$5-15/user/month for serious IdP.

## Decision Tree

For an app needing AWS access:
1. Running on EC2/ECS/Lambda? → Use respective execution role.
2. In EKS? → IRSA.
3. External CI/CD? → OIDC federation.
4. External on-prem? → IAM Roles Anywhere.
5. Local dev? → AWS CLI profile with SSO.

Last resort: IAM user with rotated keys.

## Best Practices

- Use the workload-native identity for every app: instance profile/execution role on AWS, Managed Identity on Azure, default/custom SA on GCP — never embed keys.
- Federate K8s pods to cloud identity (IRSA / Workload Identity) instead of mounting long-lived cloud credentials in the cluster.
- Give CI/CD short-lived creds via OIDC federation (e.g. GitHub Actions → AWS role), with the trust policy scoped to a specific repo/branch.
- Federate human access to a single IdP (Okta/Azure AD/Identity Center) and require MFA, especially on root/break-glass accounts.
- Prefer ABAC (tag-based conditions) over per-team policies so access scales without policy churn.
- Manage identity lifecycle: detect unused identities/keys after ~90 days, disable, then delete; if static keys are truly unavoidable, rotate and store them in a secret manager.

## Quick Refs

Identity-type equivalents across clouds:

| Concept | AWS | GCP | Azure |
|---|---|---|---|
| Human (SSO) | Federated user → role | Cloud Identity user | Azure AD user |
| VM identity | Instance profile (role) | Service Account | Managed Identity |
| Function identity | Execution role | Service Account | Managed Identity |
| K8s pod | IRSA | Workload Identity | Workload Identity |
| External CI/CD | OIDC → role | Workload Identity Federation | Managed Identity / SP |

Decision tree for an app needing cloud access: EC2/ECS/Lambda → execution role · EKS → IRSA · external CI/CD → OIDC federation · on-prem → IAM Roles Anywhere · local dev → CLI + SSO · last resort → IAM user with rotated keys.

RBAC = grant by role ("engineers read prod logs"); ABAC = grant by matching attributes/tags (`aws:ResourceTag/Team == aws:PrincipalTag/Team`).

## Interview Prep

**Mid**: "IAM role vs user."

**Senior**: "IRSA vs node-level role."

**Staff**: "Identity for 1000-engineer org."

## Next Topic

→ [T03 — Federated Identity (SAML, OIDC)](T03-Federated-Identity.md)
