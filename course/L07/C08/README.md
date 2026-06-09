# L07/C08 — Identity & Access Management

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-IAM-Mental-Model.md) | The IAM Mental Model (Principal, Action, Resource, Condition) | 1.5 hr |
| [T02](T02-Roles-Users-SAs.md) | Roles vs Users vs Service Accounts | 1 hr |
| [T03](T03-Federated-Identity.md) | Federated Identity (SAML, OIDC) | 1 hr |

## The IAM Mental Model

Every IAM decision answers: **can PRINCIPAL do ACTION on RESOURCE under CONDITION?**

- **Principal**: who is asking (user, role, service account)
- **Action**: what API call (`s3:GetObject`, `ec2:RunInstances`)
- **Resource**: what entity (`arn:aws:s3:::my-bucket/*`)
- **Condition**: when/where/how (`aws:SourceIp`, `aws:RequestedRegion`)

Each cloud has its own dialect but the model is the same.

## AWS IAM Policy Anatomy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyS3",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "StringEquals": {"aws:PrincipalTag/team": "data"},
        "IpAddress": {"aws:SourceIp": "203.0.113.0/24"}
      }
    }
  ]
}
```

### Policy Evaluation (AWS)

```
1. Explicit Deny anywhere       → DENY (final)
2. Org SCP doesn't allow         → DENY
3. Permission Boundary doesn't  → DENY
4. Identity policy doesn't       → DENY (unless resource policy allows)
5. Resource policy denies        → DENY
6. Some allow                    → ALLOW
7. No allow                      → DENY (default)
```

## Principal Types

### Users
- Long-term identities
- Username + password / access key
- Avoid for workloads (use roles)
- Suitable for: humans, break-glass

### Groups
- Collection of users; policies attached to group apply to all members
- AWS only (GCP and Azure use group memberships at IAM)

### Roles (AWS) / Service Accounts (GCP) / Managed Identities (Azure)
- Identity for workloads
- Short-lived credentials (assumed via STS, OIDC)
- No long-term secrets
- Recommended for everything non-human

### Cross-Account Roles (AWS)
- Trust relationship: which accounts/users can assume this role
- Allows least-privilege cross-account access

## Federated Identity

Outside IdP authenticates; cloud trusts the IdP.

### SAML
- XML-based (older)
- Used by: Okta, Auth0, ADFS, Google Workspace → AWS IAM Identity Center (formerly SSO)
- Browser-mediated SSO

### OIDC (OpenID Connect, on OAuth 2.0)
- JSON / JWT
- Used by: GitHub Actions, Vault, Kubernetes, modern apps
- Programmatic flow (no browser needed)

### GitHub Actions OIDC → AWS (huge win)
No more static keys in GH Secrets:

```yaml
permissions:
  id-token: write    # request OIDC token
  contents: read

steps:
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123:role/gha-deployer
    aws-region: us-east-1
```

Role's trust policy verifies the GHA OIDC issuer + repo + branch claims.

## Cloud-Specific Patterns

### AWS IAM Roles for Service Accounts (IRSA)
- EKS pod auths to AWS via OIDC
- Pod has a K8s SA, annotated with AWS role
- aws-iam-token mounted; SDK uses it

### EKS Pod Identity (newer, 2023+)
- Replaces IRSA; simpler config
- Add-on; pod identity agent
- No OIDC URL juggling

### GCP Workload Identity (GKE)
- K8s SA bound to GCP SA
- Pods auth as that GCP SA

### Azure Workload Identity (AKS)
- K8s SA federated with Entra ID
- Pod uses Azure AD token

## Best Practices

- **No static keys in code / repos**
- **Use roles for workloads**
- **Federation for humans (SSO via Okta/Workspace/Entra)**
- **Least privilege (start strict, widen as needed)**
- **MFA enforced for humans**
- **Rotate keys frequently if you must use them**
- **Use IAM Access Analyzer / equivalent to find unused permissions**
- **Permission Boundaries for delegated administration**
- **Audit access via CloudTrail / equivalent**

## Common Mistakes

- `*` in actions for IAM users (broad escalation risk)
- Long-lived access keys in CI (use OIDC instead)
- Cross-account roles without ExternalId (confused deputy)
- IAM Roles trusting any account (`Principal: "*"`)
- Forgetting Resource constraint (`*` resources)
- IMDS without v2 (SSRF risk)

## Interview Themes

- "Walk me through IAM policy evaluation in AWS"
- "Difference between IAM user and role"
- "How does OIDC enable keyless cloud auth from CI?"
- "Cross-account access pattern in AWS"
- "Permission boundary vs SCP vs identity policy"
