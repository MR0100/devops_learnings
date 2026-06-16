# L20/C01/T03 — Least Privilege

## Learning Objectives

- Apply least privilege
- Audit access

## Principle

Minimum access to do job:
- No more
- Reviewed
- Time-bound where possible

For: limit blast radius.

## Why

Compromised credential:
- Wide access → wide damage
- Limited access → limited damage

## Examples

### Bad
```
User: alice
Role: Owner (everything)
```

### Good
```
User: alice
Role: Storage Admin for prod buckets
```

## IAM

### AWS
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::my-bucket/*"
}
```

Specific action; specific resource.

### Azure
RBAC roles per resource.

### GCP
Predefined or custom IAM roles.

## Per Service

- Service A: read DB X only
- Service B: write queue Y only

NOT:
- Service A: read everything

For: minimize.

## Per Engineer

### Daily
Read-only.

### Time-bound
Promote for task; expire.

### JIT
Just-in-time elevation:
- AWS IAM Identity Center
- Azure PIM
- Custom: ChatOps `/elevate`

## RBAC vs ABAC

### RBAC
Role-Based:
- "Engineer can read prod"

Simple; doesn't scale.

### ABAC
Attribute-Based:
- "Engineer + on-call → can read prod"
- "Engineer + tenant=A → access tenant A"

Flexible.

## Audit

Quarterly:
- List access per user
- Verify needed
- Revoke unused

For: hygiene.

## Tools

- AWS Access Analyzer
- Azure Identity Governance
- GCP Recommender
- Okta access reviews

## SoD (Separation of Duties)

Same person can't:
- Develop + deploy + audit

For: prevent fraud.

E.g.:
- Dev: code
- Deployer: prod push
- Auditor: review

Different people.

## Cloud Examples

### AWS
- Avoid `*` in actions
- Use service-linked roles
- Use Access Analyzer

### Azure
- PIM for admin
- Conditional Access
- Per-RG / sub roles

### GCP
- Predefined roles > Owner
- Custom for tight
- VPC SC for resources

## App Permissions

- Read-only DB connection for reads
- Separate write connection
- Per-endpoint roles

For: tight.

## K8s

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: prod
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

Per-namespace; specific resources.

Not: cluster-admin everywhere.

## Default Deny

Network policies:
```yaml
ingress:
- from: []  # nothing
```

Then allow specific.

## Audit Logs

Enable:
- CloudTrail
- Cloud Audit Logs
- Azure Activity Log
- K8s audit

Review for unauthorized actions.

## Service Accounts

Per service:
- Own SA
- Specific permissions

NOT:
- Default SA (often too broad)
- Shared SA

## Secrets

Per service:
- Own secret
- Scoped read

NOT: master credential.

## Anti-Patterns

### Owner / Editor
Too broad. Avoid.

### Long-Lived Creds
Should rotate.

### Standing Admin
Always admin = leak risk.

For: JIT.

## Examples

### Pet Service
Backend: read+write pet table.
NOT: read all tables in DB.

### Lambda Function
Single role: only S3 bucket X read.
NOT: S3 full access.

### CI/CD
Deploy to staging: deploy role for staging.
Deploy to prod: separate role (less access elsewhere).

## Quarterly Review

```
For each user:
- Current roles?
- Last used?
- Need still?

For each role:
- Permissions?
- Reduce?
- Deprecate?
```

For: continuous tightening.

## Best Practices

- Specific actions
- Specific resources
- Time-bound for admin
- JIT for elevation
- Audit regularly
- Default deny

## Common Mistakes

- Wildcard permissions
- Roles too broad
- No reviews
- Shared SAs
- Standing admin

## Quick Refs

```
Permission = specific action + specific resource
JIT: elevate when needed
SoD: separate dev/deploy/audit
Audit: quarterly
Default: deny
```

## Interview Prep

**Junior**: "What is least privilege?" — Granting each user, service, or process only the permissions it needs to do its job, and nothing more, to limit blast radius if it's compromised.

**Mid**: "How do you design IAM for least privilege?" — Start from deny-by-default, scope roles to specific actions and resources (not wildcards), prefer short-lived/assumed roles over long-lived keys, and separate duties so no single role can both act and approve.

**Senior**: "What is just-in-time elevation and why use it?" — Instead of standing admin access, users request time-boxed, audited elevation for a specific task; this shrinks the window an attacker can abuse and gives you a clear access trail.

**Staff**: "How do you enforce least privilege org-wide and prove it?" — Use SCPs/permission boundaries as guardrails, continuously right-size policies from actual access logs (e.g. CIEM, IAM Access Analyzer), require JIT for privileged roles, and review unused permissions on a cadence so entitlements trend toward what's actually used.

## Next Topic

→ Move to [L20/C02 — Shift Left Security](../C02/README.md)
