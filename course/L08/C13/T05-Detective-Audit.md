# L08/C13/T05 — Detective, Audit Manager

## Learning Objectives

- Use Detective for investigations
- Use Audit Manager for compliance

## Detective

Visualize and analyze security events. Builds graph from CloudTrail, VPC Flow Logs, GuardDuty, EKS audit.

For: post-incident investigation.

```bash
aws detective create-graph
```

Per region; per account.

## What It Does

Aggregates 30+ days of:
- API calls (CloudTrail)
- Network (Flow Logs)
- DNS
- GuardDuty findings
- EKS audit

Auto-builds relationships:
- Resource → Resource
- Principal → API calls
- IP → Resources

## UI

Console-only mostly. Graph + timeline.

For: forensics.

## Use Cases

### Investigate Finding
GuardDuty alert → click "Investigate" → Detective opens graph of involved entities.

### Track Compromised Credentials
Show all API calls from key over time. Suspicious patterns visible.

### Network Path Analysis
Which resources talked to which IPs?

## Pricing

Per GB ingested + analyzed. $2/GB.

For typical org: $50-500/mo per account.

## Detective + GuardDuty + SH

- GuardDuty: detect
- Security Hub: aggregate
- Detective: investigate

Triad of AWS security.

## Limitations

- AWS-only
- Console UX (not API-friendly)
- Cost at scale

## Audit Manager

Automate compliance evidence collection:
- Pre-built frameworks
- Continuous evidence gathering
- Report generation

```bash
aws auditmanager create-assessment ...
```

## Frameworks

- AWS License Manager
- AWS Operational Best Practices
- CIS Benchmarks
- FedRAMP
- GDPR
- HIPAA
- ISO 27001
- NIST 800-53
- PCI DSS
- SOC

Custom frameworks: define controls + evidence.

## How It Works

1. Pick framework
2. Create assessment (scope: accounts, services)
3. Audit Manager collects evidence (CloudTrail, Config, Security Hub findings)
4. Review evidence per control
5. Generate report for auditor

Continuous; not one-time.

## Evidence Types

- Compliance check results
- Configuration data
- User activity
- API calls
- Manual (you upload docs)

## Reports

Exportable PDFs / data for audit.

## Pricing

Per evidence collected:
- $1.25 per 1000 evidence
- Plus framework cost (sometimes)

For typical org: $100-1000/mo.

## Manual Add Evidence

Upload screenshots / docs:
```bash
aws auditmanager batch-import-evidence-to-assessment-control ...
```

For: things not auto-collected.

## Delegations

Assign controls to specific people / teams to review.

For: workflow during audit.

## Snapshot

Lock evidence at point in time for audit period:
- Don't change after submission
- Auditor reviews exactly what was

## When NOT

- No compliance audits
- Tiny org (overkill)
- One-time check (use Security Hub)

## Replacement vs Augmentation

For SOC 2 / ISO: replaces / accelerates manual evidence gathering.

For pure cloud-only: significant time saver.

## Org-Wide

Delegated admin; aggregates org evidence.

## Architecture

Audit Manager:
- Reads from Config, CloudTrail, Security Hub
- Maps to controls
- Generates assessment
- Continuous + reportable

## Compliance Lifecycle

1. Set up controls (frameworks)
2. Implement controls (technical)
3. Continuous evidence (Audit Manager)
4. Auditor reviews
5. Certify
6. Renew annually

## Integration

- Config: state
- Security Hub: findings
- CloudTrail: activity
- IAM Access Analyzer: external access
- All feed Audit Manager

## Common Mistakes

- Setting up Audit Manager without source data
- Custom frameworks for everything (use pre-built)
- Manual evidence when auto possible
- No delegations (one person reviewing everything)

## Best Practices

- Use pre-built frameworks
- Continuous (not last-minute)
- Delegate to control owners
- Manual evidence with metadata
- Snapshot before submission

## Comparison

| | Config | Security Hub | Detective | Audit Manager |
|---|---|---|---|---|
| Purpose | Inventory + rules | Aggregate findings | Investigate | Compliance evidence |
| Time horizon | Current + history | Current | Past 30+ days | Continuous |
| User | Engineer | Sec team | IR / forensics | Compliance |

Each different role; together comprehensive.

## SOC2 Example Workflow

1. Define controls (Audit Manager framework "SOC2")
2. Implement (encryption, access, monitoring)
3. Audit Manager collects evidence
4. Sec team triages Security Hub findings
5. IR investigates anomalies (Detective)
6. Quarterly: review evidence
7. Annual: submit to auditor

## Cost

- Detective: $50-500/mo
- Audit Manager: $100-1000/mo

For compliance value: usually worth.

## Quick Refs

```bash
# Detective
aws detective create-graph

# Audit Manager
aws auditmanager create-assessment --name myAssessment --framework-id ...
aws auditmanager list-controls
aws auditmanager get-evidence-by-evidence-folder ...
```

## Interview Prep

**Mid**: "Detective vs GuardDuty."

**Senior**: "Compliance program design."

**Staff**: "SOC2 evidence automation."

## Next Topic

→ Move to [L08/C14 — Well-Architected Framework](../C14/README.md)
