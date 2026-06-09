# L08/C02 — IAM Mastery

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Users-Groups-Roles.md) | Users, Groups, Roles, Policies | 1 hr |
| [T02](T02-Trust-vs-Permission.md) | Trust Policies vs Permission Policies | 1 hr |
| [T03](T03-Resource-Based.md) | Resource-Based Policies | 1 hr |
| [T04](T04-Conditions-Access-Analyzer.md) | Conditions, IAM Access Analyzer | 1 hr |
| [T05](T05-IRSA.md) | IAM Roles for Service Accounts (IRSA) | 1 hr |
| [T06](T06-Boundaries-SCPs.md) | Permission Boundaries & SCPs | 1 hr |
| [T07](T07-AssumeRole.md) | Assume Role, STS, External ID | 1 hr |

IAM is the highest-leverage skill in AWS. Almost every security incident is an IAM mistake. This chapter goes deep.

## Identity vs Resource Policies

Two policy "doors":
- **Identity policy** — attached to a principal (user, role); says "this principal can do X"
- **Resource policy** — attached to a resource; says "these principals can do X on me"

Either can grant access. Both must allow for full effect (with caveats).

### Cross-Account Access

Same-account: identity policy alone is enough.
Cross-account: **both** identity policy (in calling account) **and** resource policy (in target account) must allow.

## Trust vs Permission Policies (on a Role)

A role has TWO policies:

### Trust Policy
- Who can ASSUME the role
- "Principal: arn:aws:iam::123:user/alice can sts:AssumeRole on this role"

### Permission Policies
- What the ROLE can do once assumed
- "Allow s3:Get* on my-bucket/*"

Confusing them is a common mistake. Trust = "who's the user", Permission = "what they can do as the user."

## Sample Trust Policy (Cross-Account)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111111111111:root"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {"sts:ExternalId": "MySharedSecret"}
    }
  }]
}
```

The `ExternalId` protects against the **confused deputy** attack — see T07.

## Resource-Based Policies

Attached to:
- S3 buckets (bucket policy)
- KMS keys (key policy)
- SQS queues
- SNS topics
- Lambda (function policy)
- Secrets Manager
- VPC Endpoints
- IAM roles (trust policy itself is a resource policy)

```json
// S3 bucket policy
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowReadFromOtherAccount",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::222:role/data-reader"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

## Conditions (the Real Power)

Common condition keys:
```
aws:SourceIp                  caller IP
aws:VpcSourceIp               within a VPC
aws:SourceVpc                 specific VPC
aws:SourceVpce                via specific VPC endpoint
aws:PrincipalArn              the principal's ARN
aws:PrincipalTag/X            tag on principal
aws:RequestTag/X              tag in the create request
aws:ResourceTag/X             tag on the resource
aws:RequestedRegion           region of API call
aws:CurrentTime               time
aws:MultiFactorAuthPresent    is MFA used
aws:UserAgent                 caller UA (don't rely on)
```

### ABAC (Attribute-Based Access Control)

Tag-driven policies. Principals tagged with `team=payments` can access resources tagged `team=payments`.

```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "arn:aws:s3:::*",
  "Condition": {
    "StringEquals": {"aws:ResourceTag/team": "${aws:PrincipalTag/team}"}
  }
}
```

One policy → many tenants.

## IAM Roles for Service Accounts (IRSA)

EKS pods auth to AWS without static creds.

1. Cluster has an OIDC issuer URL (`https://oidc.eks.region.amazonaws.com/id/XYZ`)
2. Register it as an IAM Identity Provider
3. Create IAM Role with trust policy trusting the OIDC issuer + specific K8s SA
4. Annotate the K8s SA with role ARN

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::111:role/my-app-role
```

Pod gets short-lived AWS creds automatically.

### EKS Pod Identity (newer, 2023+)
Replaces IRSA's OIDC setup. Add-on; pod-identity-agent; simpler config.

## Permission Boundaries

The MAXIMUM permissions an identity can have, even if its policies say more.

```
Effective permissions = Identity Policies ∩ Permission Boundary
```

Use case: delegate IAM admin to dev teams but cap what they can grant.

## SCPs (Recap from C01)

Org-level deny boundary. **SCPs deny; they don't grant.**

```
Effective permissions = SCP ∩ Boundary ∩ Identity Policy ∩ Resource Policy
```

## STS (Security Token Service)

Issues short-lived credentials.

- `AssumeRole` — get credentials for a role
- `AssumeRoleWithSAML` — federation
- `AssumeRoleWithWebIdentity` — OIDC (used by IRSA, GHA OIDC)
- `GetSessionToken` — short-lived creds for an IAM user (rarely needed)
- `GetFederationToken` — even more rarely needed

Default session: 1h, configurable up to 12h.

## Confused Deputy

A service acts on behalf of another customer when it shouldn't. Mitigation: ExternalId.

```
Vendor offers SaaS that needs cross-account role
You create role trusting vendor's AWS account
But vendor's AWS account is shared with 1000 customers!
Anyone in the vendor's customer base could ask vendor to access your role.
Fix: vendor uses a unique ExternalId per customer.
```

## IAM Access Analyzer

- **External Access** — finds resources shared outside your trust zone
- **Unused Access** — finds unused users, roles, permissions
- **Policy generation** — generates least-privilege policy from CloudTrail history
- **Policy validation** — lints policies for findings

Run quarterly to clean up cruft.

## Least Privilege Workflow

1. Start with no perms
2. Add only what's needed
3. Watch CloudTrail for denied actions
4. Add specifically; don't broaden to `*`
5. After 30 days, run Access Analyzer Unused Access; trim further

## Common Mistakes

- `Action: *` and `Resource: *` (admin everything)
- IAM users for workloads (use roles)
- Static keys in env vars in code (use roles + temporary creds)
- Trust policy with `Principal: "*"` (anyone can assume!)
- Cross-account role without ExternalId
- Wildcard in resource that includes sensitive ARNs
- Forgetting that resource policies can grant (review S3 bucket policies)

## Interview Themes

- "Walk me through IAM evaluation logic"
- "Trust policy vs permission policy"
- "How does IRSA work end-to-end?"
- "What's the confused deputy problem?"
- "Permission boundary vs SCP — when each?"
- "ABAC vs RBAC in AWS IAM"
