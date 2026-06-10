# L20/C07/T03 — CIEM (Identity Posture)

## Learning Objectives

- Manage cloud identities
- Reduce permissions

## CIEM

Cloud Infrastructure Entitlement Management:
- Identity-focused
- Analyze permissions
- Detect over-privileged

For: principle of least privilege at scale.

## Problem

Cloud:
- Many identities (users, SAs, roles)
- Permissions sprawl
- Hard to audit manually

## Solutions

- Native (AWS Access Analyzer, Azure PIM, GCP Recommender)
- 3rd party (Wiz, Sonrai, Permify)

## Capabilities

### Over-Privilege Detection
"Role X has perms it never used in 90 days."

Solution: remove.

### Privilege Escalation Paths
"User A → role B → can become admin."

Solution: break chain.

### Unused Identities
"User Z no logins for 6 months."

Solution: deactivate.

### Public Roles
"Role T can be assumed by *."

Solution: restrict.

## AWS Access Analyzer

Free:
```bash
aws accessanalyzer create-analyzer --analyzer-name my --type ACCOUNT
```

Findings:
- Public buckets
- Cross-account access
- Resource policies

## IAM Access Advisor

Per-role:
- Last used per service
- Generate policy from actual usage

For: tighten.

## AWS IAM Policy Generation

Generates least-priv policy from CloudTrail:
```bash
aws accessanalyzer get-finding ...
```

## Azure PIM

Privileged Identity Management:
- JIT activation
- Audit
- Time-bound roles

## Azure Identity Governance

- Access reviews
- Lifecycle

## GCP IAM Recommender

ML-based:
- "Role X over-privileged"
- Suggested smaller role

```bash
gcloud recommender recommendations list \
  --recommender=google.iam.policy.Recommender \
  --project=PROJ \
  --location=global
```

## CIEM Tools (3rd Party)

### Wiz
Includes CIEM.

### Sonrai
Identity graph; analyze paths.

### Permify
Permission management.

### Apono / Britive
JIT access.

## Workflow

```
1. Inventory identities
2. Analyze permissions (used vs granted)
3. Detect over-priv
4. Recommend reduction
5. Apply via PR
6. Continuous
```

## JIT (Just-In-Time)

Standing perms reduced; elevate on demand:
```bash
# Slack
/elevate prod-admin "Investigating ticket-1234"
```

Bot grants 1-hour role; revokes.

For: minimize standing.

## Per-Resource

For each resource:
- Who can access?
- Why?
- Last used?
- Reduce.

## Privilege Escalation

```
User has: iam:CreateRole
   ↓
Creates role: admin
   ↓
Assumes role: admin
```

Mitigation: limit iam:CreateRole.

## Trust Policies

Cross-account roles:
```json
{
  "Principal": {"AWS": "arn:aws:iam::OTHER_ACCT:root"}
}
```

Risky if other account compromised.

For: trust specific roles only.

## Audit Logs

CloudTrail / activity logs:
- Per-role usage
- Per-action
- Anomalies

For: detect abuse.

## Compliance

- SOC 2: access reviews
- PCI: least priv
- HIPAA: minimum necessary

CIEM helps.

## Quarterly Reviews

```
For each user:
- Roles?
- Last used?
- Need?
- Reduce?
```

Manual + automated.

## Automation

```python
# Detect unused roles
for role in iam_roles:
    last_used = role.last_used_date
    if last_used > 90 days ago:
        notify owner; recommend remove
```

Run weekly.

## Service Accounts

Often:
- Over-privileged
- Static keys
- Never reviewed

For: special focus.

## Workload Identity

(IRSA, WI, Azure WI):
- Eliminates static keys
- Tighter scoping

Use everywhere.

## Best Practices

- Continuous CIEM
- IRSA / WI for workloads
- JIT for admin
- Quarterly access reviews
- Automate detection
- Native tools first

## Common Mistakes

- Owner role (too broad)
- Long-standing admin
- No reviews
- Static keys
- No tooling

## Quick Refs

```bash
# AWS
aws accessanalyzer create-analyzer
aws iam generate-service-last-accessed-details

# Azure
PIM in portal

# GCP
gcloud recommender recommendations list
```

## Interview Prep

**Mid**: "What's CIEM."

**Senior**: "Reduce permissions."

**Staff**: "Identity at scale."

## Next Topic

→ Move to [L20/C08 — Zero Trust](../C08/README.md)
