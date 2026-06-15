# L08/C13 — Security & Compliance

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-KMS.md) | KMS (Customer-Managed Keys, Envelope Encryption) | 1 hr |
| [T02](T02-Secrets-Manager.md) | Secrets Manager vs Parameter Store | 1 hr |
| [T03](T03-GuardDuty-SecHub.md) | GuardDuty, Security Hub, Inspector, Macie | 1 hr |
| [T04](T04-Config.md) | Config & Conformance Packs | 1 hr |
| [T05](T05-Detective-Audit.md) | Detective, Audit Manager | 0.5 hr |

## KMS

Key Management Service. Stores/manages encryption keys.

### Key Types
- **AWS Managed Keys** (`aws/service-name`) — automatic, free
- **Customer Managed Keys (CMK)** — you control rotation, policy
- **AWS Owned Keys** — invisible to you
- **Imported Key Material** — bring your own (BYOK)

### Pricing
- $1/month per CMK
- $0.03 per 10K requests

### Envelope Encryption

```
Plaintext data (e.g., 1 GB)
   │
   ↓ (1) Generate Data Key
KMS API: GenerateDataKey
   ↓
Plaintext data key (256-bit)
   │
   ↓ (2) Encrypt data locally
Encrypted data (stored at rest)
   │
   ↓ (3) Encrypt data key with CMK
Encrypted data key (stored alongside data)

DATA KEY THROWN AWAY (only encrypted version persisted)
```

For decryption: send encrypted data key to KMS, get back plaintext, decrypt data, discard plaintext key.

Why: KMS doesn't see bulk data; CPU isn't bottlenecked at KMS; bulk encryption stays local.

### Key Policy

Resource-based policy on the CMK:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnableIAMPermissions",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::111:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "AllowKeyUsageForS3",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::111:role/app"},
      "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {"kms:ViaService": "s3.us-east-1.amazonaws.com"}
      }
    }
  ]
}
```

### Auto-Rotation
- Enable per-CMK
- Yearly (was 365d; now annual but configurable)
- Transparent to applications (old encrypted data still decrypts)

### Multi-Region Keys
Same key material in multiple regions. Use for cross-region replication where source/dest both need to decrypt.

### KMS in Practice
- Use SSE-KMS for S3 (per-bucket key)
- Use bucket keys (S3) to reduce KMS calls (caches data key)
- Use CMKs for compliance; AWS-managed for convenience

## Secrets Manager vs Parameter Store

### Parameter Store (SSM)
- Free for Standard tier (4 KB, 10K params)
- Advanced tier paid (more storage, throughput)
- SecureString (KMS-encrypted)
- Hierarchical (`/app/prod/db/password`)
- Versioning

### Secrets Manager
- Paid ($0.40/secret/month + $0.05 per 10K API calls)
- **Automatic rotation** with Lambda (RDS, DocumentDB, Redshift have built-in rotators)
- Cross-region replication
- Used by RDS for master password rotation
- Resource policies

### When Which
| Need | Pick |
|---|---|
| Static config (URLs, feature flags) | Parameter Store |
| App secrets, low rotation | Parameter Store SecureString |
| DB credentials with auto-rotation | Secrets Manager |
| Compliance requires rotation evidence | Secrets Manager |
| Tight budget | Parameter Store |

## GuardDuty

ML-based threat detection. Analyzes:
- CloudTrail (anomalous API patterns)
- VPC Flow Logs (suspicious connections)
- DNS Logs (malicious domain queries)
- S3 Data Events (optional)
- EKS audit logs (optional)
- Malware Protection (EC2, ECS Fargate, S3)

Findings: low/medium/high severity. Integrates with Security Hub, EventBridge.

### Enable Org-Wide
One click via Organizations integration. Findings centralized in master account.

## Security Hub

Aggregator of security findings:
- GuardDuty
- Inspector
- Macie
- Config
- 3rd-party (Wiz, Lacework, etc.)
- Your custom

Provides:
- Compliance standards checks (CIS, PCI, NIST, AWS Foundational)
- Cross-account aggregation
- EventBridge integration for automation

## Inspector

Vulnerability scanner.

### v2 (current)
- EC2: scans installed packages for CVEs
- ECR: scans images at push (and continuously)
- Lambda: scans deployment packages

Findings → Security Hub. Free trial; pay per resource scanned.

## Macie

ML for sensitive data discovery in S3:
- PII, PHI, credentials, etc.
- Per-GB scanned cost
- Use: compliance, data classification, S3 inventory

## Config

Records resource configuration over time + evaluates against rules.

### Use
- "Was this EC2 ever public?"
- "Is every EBS volume encrypted?"
- "Compliance reporting"

### Conformance Packs
Pre-built rule sets:
- CIS AWS Foundations
- PCI DSS
- HIPAA
- Operational Best Practices for X

### Remediation
Auto-remediate non-compliant resources via SSM documents.

### Cost
Per-configuration-item recorded; aggregated across accounts gets expensive.

## Detective

Investigation tool. Builds graphs from CloudTrail + GuardDuty + VPC Flow Logs.

Use: when GuardDuty surfaces a finding, drill into context.

## Audit Manager

Automates compliance audits.
- Frameworks (SOC 2, PCI, HIPAA, GDPR)
- Auto-collects evidence from Config, CloudTrail, Security Hub
- Generates audit reports

Reduces manual evidence gathering.

## Org-Wide Security Setup (Recommended)

Per Landing Zone:
- All accounts: GuardDuty, Config, Security Hub on
- Security Hub: aggregates to master/security account
- Centralized log archive: CloudTrail + Config + VPC Flow Logs to S3 with Object Lock
- IAM Access Analyzer org-wide
- AWS Backup with cross-region copies for critical data
- AWS Detective in security account

## Interview Themes

- "Walk me through envelope encryption"
- "Parameter Store vs Secrets Manager"
- "Compare GuardDuty, Inspector, Macie"
- "What does Security Hub do?"
- "Compliance posture — how do you build it on AWS?"
- "How would you respond to a GuardDuty 'unauthorized API call' finding?"
