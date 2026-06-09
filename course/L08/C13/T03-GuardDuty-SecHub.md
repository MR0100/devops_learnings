# L08/C13/T03 — GuardDuty, Security Hub, Inspector, Macie

## Learning Objectives

- Use AWS security services
- Build security posture

## Four Services

| | Purpose |
|---|---|
| GuardDuty | Threat detection (CloudTrail / VPC / DNS) |
| Security Hub | Aggregate findings; compliance |
| Inspector | Vulnerability scan (EC2 / Lambda / containers) |
| Macie | S3 sensitive data discovery |

## GuardDuty

ML-based threat detection. Analyzes:
- CloudTrail events
- VPC Flow Logs
- DNS logs
- EKS audit logs
- S3 data events
- Lambda invocations

```bash
aws guardduty create-detector --enable
```

Auto-enabled across regions when delegated admin.

## Findings

Categories:
- Backdoor (C2 communication)
- Behavior (anomalous API calls)
- Cryptocurrency (mining)
- Discovery (recon)
- Exfiltration
- Impact (resource manipulation)
- InitialAccess
- Persistence
- Policy violation
- Privilege escalation
- Recon

Severity: 1.0-8.9.

## Investigation

GuardDuty finding → CloudWatch Events → Lambda / SNS for alerting.

```json
{
  "type": "UnauthorizedAccess:EC2/MaliciousIPCaller.Custom",
  "severity": 8.0,
  "resource": {"instanceDetails": {...}},
  "service": {"action": {...}}
}
```

## Cost

Per CloudTrail / VPC Flow / DNS data processed. Typical: $10-100/mo per account.

S3 protection: extra.

## Org-Wide

Delegate admin to security account; enable across all org accounts:
```bash
aws guardduty enable-organization-admin-account --admin-account-id ...
```

Findings centralized.

## Security Hub

Aggregates findings from:
- GuardDuty
- Inspector
- Macie
- Config
- IAM Access Analyzer
- Third-party (CrowdStrike, etc.)

Plus compliance standards:
- AWS Foundational Security Best Practices
- CIS AWS Foundations
- PCI DSS

```bash
aws securityhub enable-security-hub
```

## Dashboard

Per-finding, per-severity, per-standard.

For: single pane of glass.

## Cross-Account

Org-wide; security account aggregates.

## Cost

$0.0010 per finding. Plus standard checks.

Standard: 1-100 controls × $0.0030/control eval/mo. ~$10-50/mo.

## Inspector

Vulnerability scanning:
- EC2 instances (auto-discovered)
- Lambda functions
- ECR images

CVE detection + network reachability.

```bash
aws inspector2 enable --resource-types EC2 ECR LAMBDA
```

Continuous. No agent needed for EC2 (uses SSM).

## Findings

CVE per resource. Severity + CVSS score.

Action:
- Patch
- Block deploy if critical
- Accept risk (with rationale)

## Cost

Per-resource hour scanned:
- EC2: $0.13/mo per instance
- Lambda: $0.30/mo per function
- ECR: $0.09 per image scan

For 100 EC2: $13/mo.

## Macie

S3 PII discovery:
- SSN, credit cards
- Health records (PHI)
- Credentials in code
- Custom regex

```bash
aws macie2 enable-macie
```

Scans buckets; reports.

Cost: per GB scanned. Selective scanning.

## Findings

- "S3 bucket contains 1500 SSNs"
- "Unencrypted bucket public"

Triage; remediate.

## Workflow Integration

Findings → EventBridge:
```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"]
}
```

→ Lambda → ticketing system / Slack / SOAR.

For: alerting + automated response.

## Auto Remediation

For high-confidence findings:
- Public S3 bucket → block
- Exposed key → rotate
- Crypto-mining EC2 → isolate

EventBridge → Lambda → action.

Be careful: false positives can cause outages.

## SCP for Security

Combine with SCPs:
- Block disabling GuardDuty
- Block disabling CloudTrail
- Force MFA

Defensive.

## Detective

Investigation tool (separate; covered T05). Correlates findings across services for forensics.

## Audit Manager

Compliance evidence collection (separate). For SOC, ISO, etc.

## Recommended Setup

Org-wide:
- GuardDuty (always-on)
- Security Hub (aggregation + best practices)
- Inspector (vuln management)
- Macie (PII; if S3 has sensitive)
- CloudTrail (audit)
- Config (compliance state)

For: comprehensive security posture.

## Cost Total

For medium account:
- GuardDuty: $20/mo
- Security Hub: $20/mo
- Inspector: $20/mo
- Macie: variable

~$60-200/mo per account.

For 50 accounts: $3000-10000/mo. Real money.

## Alternative

Third-party CSPM (Cloud Security Posture Management):
- Wiz
- Lacework
- Prisma Cloud
- Orca

Replace / augment Security Hub. More features; higher cost.

## Patterns

### Daily Triage
- Security Hub findings → ticket
- Critical → on-call
- Auto-close known-benign

### Quarterly Review
- Compliance posture
- Standards score
- Improve highest-impact

### Incident Response
- GuardDuty alert → IR runbook
- Containment via Lambda
- Forensics via Detective

## Common Mistakes

- Enable but ignore findings
- No alerting (silent)
- Auto-remediate without testing
- Per-account; no aggregation
- Ignoring Security Hub Best Practices

## Best Practices

- Enable org-wide
- Aggregate to security account
- Standards: enable all relevant
- Alert on HIGH/CRITICAL
- Suppress known benign with rationale
- Document remediation per finding type

## Severity Mapping

Severity → action:
- INFORMATIONAL: log
- LOW: review weekly
- MEDIUM: review daily
- HIGH: alert; act today
- CRITICAL: page on-call

## Compliance Reports

Security Hub: standard report exports.
Audit Manager: detailed evidence per framework.

For audits: pull report; reviewer reviews.

## CSPM Tooling Comparison

| | AWS Native | Vendor (Wiz, etc.) |
|---|---|---|
| Cost | Lower | High |
| Multi-cloud | No | Yes |
| Features | AWS only | Cross-service |
| Setup | Native | Some setup |
| For | AWS-heavy | Multi-cloud / advanced |

## Quick Refs

```bash
# GuardDuty
aws guardduty create-detector --enable

# Security Hub
aws securityhub enable-security-hub --enable-default-standards

# Inspector
aws inspector2 enable --resource-types EC2 ECR LAMBDA

# Macie
aws macie2 enable-macie

# Findings
aws securityhub get-findings --filters '{}'
```

## Interview Prep

**Mid**: "GuardDuty purpose."

**Senior**: "Security stack architecture."

**Staff**: "Security posture for 100-account org."

## Next Topic

→ [T04 — Config & Conformance Packs](T04-Config.md)
