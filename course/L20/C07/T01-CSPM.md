# L20/C07/T01 — CSPM Tools (Wiz, Lacework, Prisma)

## Learning Objectives

- Use CSPM
- Continuous compliance

## CSPM

Cloud Security Posture Management:
- Misconfiguration detection
- Compliance check
- Continuous

For: many resources; mistakes inevitable.

## What Detects

- Public S3 bucket
- Open SG (0.0.0.0/0:22)
- Unused IAM roles
- No encryption
- No MFA
- Stale snapshots
- Cross-region exposure

## Tools

### Wiz
- Cloud-native
- Agentless
- Graph analysis
- Strong UX

### Lacework
- AI-driven
- Runtime + posture
- CWPP + CSPM

### Prisma Cloud (Palo Alto)
- Comprehensive
- IaC + runtime
- Enterprise

### Orca Security
- Agentless
- Multi-cloud
- Strong scanner

### Cloud-Native
- AWS Security Hub
- Azure Defender
- GCP Security Command Center

## Workflow

```
1. Connect cloud account
2. Read-only scan
3. Findings
4. Prioritize
5. Remediate
6. Continuous
```

## Common Findings

### IAM
- Wildcard policies
- Long-unused
- No MFA
- Cross-account broad

### Storage
- Public buckets
- No encryption
- No versioning

### Network
- 0.0.0.0/0 in SGs
- No NSG on public IPs
- VPC peering broad

### Compute
- Public IPs
- No patch
- OS EOL

### Database
- Public RDS
- No encryption
- No backup

## Compliance

Frameworks:
- CIS Benchmark
- PCI-DSS
- HIPAA
- SOC 2
- NIST 800-53
- ISO 27001

Map findings to controls.

## Severity

- Critical: act immediately
- High: this week
- Medium: this month
- Low: backlog

## Auto-Remediate

Some tools:
- Lambda triggered on finding
- Auto-fix

For: known safe fixes.

Risk: auto-fix wrong; service impact.

For: conservative.

## Native vs 3rd Party

| | Native | 3rd Party |
|---|---|---|
| Cost | per region | per asset |
| Multi-cloud | per cloud | yes |
| Depth | broad | deep |

For multi-cloud: 3rd party.
For single: native often enough.

## AWS Security Hub

Aggregates:
- GuardDuty
- Inspector
- IAM Access Analyzer
- Macie
- 3rd party

```bash
aws securityhub enable-security-hub
```

For: AWS central.

## Azure Defender

Similar; many plans.

## GCP Security Command Center

Premium tier:
- Findings
- Compliance
- Threat detection

## Wiz Approach

Graph:
- Connections
- Attack paths
- "If X compromised, Y reachable"

For: prioritization.

## Lacework Approach

ML:
- Baseline normal
- Detect anomaly

For: zero-day-ish.

## CWPP

Cloud Workload Protection:
- Runtime
- Plus CSPM

Wiz, Prisma, Lacework: do both.

## CIEM

Cloud Infrastructure Entitlement:
- Identity-focused
- Permissions analysis

(See T03.)

## DevSecOps

CSPM in pipeline:
- IaC scan (Checkov)
- Pre-deploy check
- Post-deploy CSPM

For: catch early.

## Cost

- Wiz: enterprise $$$
- Lacework: $$$
- Native AWS: per finding
- Prisma: enterprise $$$

For: scale matters.

## Real Use

- Most large orgs use CSPM
- Some only native
- FAANGM build custom + use commercial

## Best Practices

- Continuous (not one-time)
- Prioritize critical
- Owners per resource (tags)
- Auto-remediate safe
- Integrate with ticket system

## Common Mistakes

- One-time scan
- Block everything (noise)
- No owner mapping
- No remediation tracking

## Integration

CSPM → ticket → developer → fix → verify.

For: closed loop.

## Quick Refs

```
CSPM: misconfig + compliance
Tools: Wiz, Lacework, Prisma, Orca
Native: AWS SecHub, Azure Defender, GCP SCC

Scan:
- IAM
- Storage
- Network
- Compute
- DB
- Logs
```

## Interview Prep

**Mid**: "What's CSPM."

**Senior**: "CSPM workflow."

**Staff**: "Cloud security platform."

## Next Topic

→ [T02 — IaC Scanning (Checkov, tfsec)](T02-IaC-Scanning.md)
