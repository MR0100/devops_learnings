# L08/C02/T06 — Permission Boundaries & SCPs

## Learning Objectives

- Distinguish boundary vs SCP
- Use both for layered security

## Three Layers

```
SCP (org level)
  ↓
Permission Boundary (role/user level)
  ↓
Identity / Resource Policy (grants)
```

Each caps the next. All ANDed for effective permissions.

## SCPs

Org-level guardrails. Applied to OU or account. Affects ALL principals in scope (except management account root).

```json
{
  "Effect": "Deny",
  "Action": "iam:DeleteRole",
  "Resource": "arn:aws:iam::*:role/OrganizationAccountAccessRole"
}
```

Cap what IAM identity policies can grant. Doesn't grant; only restricts.

Covered in L08/C01/T02.

## Permission Boundaries

Attached to specific IAM user or role. Max permissions that user/role can effectively have.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:*",
      "s3:*",
      "lambda:*"
    ],
    "Resource": "*"
  }]
}
```

Attached:
```bash
aws iam put-role-permissions-boundary --role-name MyRole --permissions-boundary arn:aws:iam::aws:policy/PowerUserAccess
```

User/role has identity policy granting `iam:*`; boundary says only EC2/S3/Lambda. Effective: only EC2/S3/Lambda.

## Use Case: Developer Self-Service

Developers can create roles for their apps but those roles must not exceed boundary.

1. Org admin defines boundary policy (max permissions).
2. Developer creates role with boundary attached.
3. Developer attaches identity policy granting whatever.
4. Effective = identity ∩ boundary.

If developer tries to attach AdministratorAccess: still capped at boundary.

## Boundary Doesn't Grant

```
Identity policy: grants
Boundary: caps
Effective: identity AND boundary
```

No identity policy → 0 permissions even with broad boundary.

## SCP vs Boundary

| | SCP | Boundary |
|---|---|---|
| Scope | Org/OU/Account | Individual user/role |
| Set by | Org admin | Account admin |
| Applies to | All principals (except mgmt root) | Specific principal |
| Function | Cap | Cap |
| Use case | Org guardrails | Delegate role creation |

Use both: SCP for org rules; Boundary for delegated admin within account.

## Pattern: Self-Service with Boundary

Dev creates app roles. Trust policy:
```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::123:role/Dev"},
  "Action": "iam:CreateRole",
  "Resource": "arn:aws:iam::123:role/app-*"
}
```

But: also enforce boundary attachment.

```json
{
  "Effect": "Allow",
  "Action": "iam:CreateRole",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "iam:PermissionsBoundary": "arn:aws:iam::123:policy/DevBoundary"
    }
  }
}
```

Dev can't create role without boundary.

## Common SCPs

### Region Restriction
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    }
  }
}
```

Plus exceptions for global services (IAM, CloudFront).

### Require Encryption
```json
{
  "Effect": "Deny",
  "Action": "s3:PutObject",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}
  }
}
```

### Prevent Account Closure
```json
{
  "Effect": "Deny",
  "Action": ["organizations:LeaveOrganization"],
  "Resource": "*"
}
```

### Protect Org Trail
```json
{
  "Effect": "Deny",
  "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail"],
  "Resource": "arn:aws:cloudtrail:*:*:trail/org-trail"
}
```

## Common Boundary Policies

### Dev Boundary
- EC2: full
- S3: full
- Lambda: full
- DynamoDB: full
- IAM: limited (no role creation outside paths)
- NO: organizations, billing

### App Boundary (production)
- Specific services
- NO IAM write
- Tag enforcement

## SCP / Boundary Pitfalls

### SCP Conflicts With Service Requirements
Service-linked role needed; SCP denying. AWS provides exceptions for service-linked roles but not always.

### Boundary Misses Allow
Boundary lists actions explicitly. New service released → not in boundary → can't use.

Workaround: review/update boundaries quarterly.

### Forgetting Effective Permissions
Wide identity + narrow boundary = narrow effective. Forget; broad-looking policy actually limited.

### Lockout
Wrong SCP/boundary can lock out admins. Always have break-glass:
- Root account (SCP can't restrict in management account)
- Emergency role with attached `AdministratorAccess` and minimal boundary

## Testing

Use IAM Policy Simulator. Or sandbox account with same policies.

Never deploy untested SCPs to production OU.

## Boundary + SCP Together

```
SCP: deny use of disapproved regions
+
Boundary: max scope for dev-created roles
+
Identity policy: grants
=
Effective permissions
```

Defense in depth.

## Evaluation Detailed

For a request:
1. SCP: if denies → DENY
2. Resource policy + Identity policy + Session policy:
   - If any explicit Deny → DENY
   - If Identity allows (and Boundary allows) → ALLOW (same account)
3. Boundary: caps identity-based effective
4. Else → DENY

## Best Practices

- Apply SCPs at OU level (not individual account; harder to manage)
- Boundary for delegated admin (developers, app-creating teams)
- Document each SCP/Boundary purpose
- Quarterly review
- Test before applying widely
- Version-control (Terraform, JSON files)
- Audit with Access Analyzer

## Common Mistakes

- SCP blocks needed service-linked roles
- Boundary too narrow (legitimate work blocked)
- No documentation; future engineers don't know why
- Applied via console (no audit trail)
- Forgetting that root in management account bypasses SCP

## Quick Refs

```bash
# Apply SCP
aws organizations attach-policy --policy-id p-xxx --target-id ou-yyy

# Apply boundary
aws iam put-role-permissions-boundary --role-name MyRole --permissions-boundary arn:...

# Remove boundary
aws iam delete-role-permissions-boundary --role-name MyRole
```

## Interview Prep

**Mid**: "SCP vs IAM policy."

**Senior**: "Boundary use case."

**Staff**: "Org-wide governance for IAM."

## Next Topic

→ [T07 — Assume Role, STS, External ID](T07-Assume-Role-STS.md)
