# L20/C07 — Cloud Security Posture

## Topics

- **T01 CSPM Tools** — Wiz, Lacework, Prisma
- **T02 IaC Scanning** — Checkov, tfsec
- **T03 CIEM (Identity Posture)** — Who has access to what

## Cloud Security Posture Management (CSPM)

Continuously scan cloud config against best practices and standards.

### What CSPM Checks
- Public S3 buckets
- Unencrypted volumes
- Overly broad IAM
- Open security groups
- Missing MFA on root
- CIS / NIST / PCI compliance
- Misconfigured KMS keys
- Stale credentials

### Tools

#### Commercial
- **Wiz** (most prominent recently; agentless, fast)
- **Lacework** (CSPM + workload security)
- **Prisma Cloud (Palo Alto)** (broad)
- **Orca Security** (agentless)
- **Aqua Security** (containers + cloud)
- **Crowdstrike Falcon Cloud Security**

#### Cloud-Native
- **AWS Security Hub** — aggregates findings, has CIS standards
- **GCP Security Command Center**
- **Azure Defender for Cloud**

#### OSS
- **Steampipe** — query cloud config with SQL
- **Cloud Custodian** — policy-as-code for cloud governance

### How They Work
- Read-only IAM role granted in your account
- Scan APIs to inventory resources
- Compare config against policy rules
- Generate findings with severity + remediation

## IaC Scanning

Catch misconfig BEFORE deploy.

### Tools
- **Checkov** (Bridgecrew) — Terraform, K8s, CloudFormation, Helm, etc.
- **tfsec** — Terraform-focused, fast
- **Terrascan** — multi-IaC
- **KICS** — multi-IaC (Checkmarx)
- **Snyk IaC** — commercial

### In CI
```yaml
- uses: bridgecrewio/checkov-action@v12
  with:
    soft_fail: false
    framework: terraform,kubernetes,dockerfile

- uses: aquasecurity/tfsec-action@v1
```

### Sample Rules
- S3 bucket should have versioning
- RDS should have encryption at rest
- EC2 should not have public IP unless specifically allowed
- Security group should not allow 0.0.0.0/0 to port 22

### Suppressing False Positives
```hcl
# checkov:skip=CKV_AWS_18:Private bucket; logging via separate centralized bucket
```

Document why each suppression. Periodic review.

## CIEM (Cloud Infrastructure Entitlements Management)

Focus on identity posture: who can do what, who has used what.

### Why It's Hard
- IAM is complex (deeply nested permissions, conditions)
- Permissions accumulate over years
- People leave; access remains
- Service-to-service access multiplies

### What CIEM Surfaces
- Effective permissions (after all policies, conditions, SCPs)
- Unused permissions ("granted but never used")
- Risky combinations (privilege escalation paths)
- Cross-account access map

### Tools
- **Wiz IAM** (integrated)
- **CyberArk Conjur**
- **SailPoint**
- AWS IAM Access Analyzer (Unused Access feature, free)

## AWS IAM Access Analyzer

Free, AWS-native:
- **External Access** — find resources shared outside your trust zone
- **Unused Access** (newer) — find unused users, roles, perms
- **Policy generation** — generate least-priv policy from CloudTrail
- **Policy validation** — lint policies

Run quarterly to clean up. Specifically:
- Delete unused IAM users
- Detach unused policies
- Remove unused role permissions

## Centralized Security Findings

### Aggregator
- **AWS Security Hub** — multi-account, aggregates GuardDuty/Inspector/Macie/Config/CSPM
- **GCP Security Command Center**
- **Azure Defender for Cloud**

### Workflow
```
Many tools → findings → aggregator → triage → ticket → fix → verify
```

### Triage
- Severity-based prioritization
- Owner assignment (per-team)
- SLA per severity (Critical: 24h; High: 7 days; etc.)
- Track resolution

## Compliance Standards

### Common
- **CIS Benchmarks** — per-platform best practices
- **NIST 800-53** — federal
- **PCI DSS** — payment cards
- **HIPAA** — healthcare
- **SOC 2** — service orgs (Type 2 most common)
- **ISO 27001** — international
- **GDPR** — EU privacy

### Compliance as Code
- Rules in OPA or AWS Config rules
- Continuous evaluation
- Evidence collection automated
- Annual audit easier with continuous data

## Detection vs Prevention

| | When |
|---|---|
| Prevention | Best (block at admission, in CI) |
| Detection + alert | When prevention isn't feasible |
| Detection + auto-remediate | If safe to auto-remediate |

Auto-remediation is delicate: ensure low false positive rate before automating.

## Sample Auto-Remediation

Public S3 bucket detected → Lambda automatically applies Block Public Access.

```python
def handler(event, context):
    bucket = event['detail']['requestParameters']['bucketName']
    s3 = boto3.client('s3')
    s3.put_public_access_block(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True,
        }
    )
    notify_security_team(bucket)
```

EventBridge rule on Config compliance change triggers Lambda.

## Cost

CSPM tools can run $10K-$100K+/year. Worth it for:
- Sensitive workloads
- Compliance-driven orgs
- Multi-account complexity

For simple AWS-only single-account: AWS Security Hub may suffice.

## Interview Themes

- "CSPM — what does it do?"
- "Compare Wiz, Security Hub, Steampipe"
- "IaC scanning in CI"
- "CIEM — what's unique?"
- "Public S3 bucket detected — what's your auto-remediation?"
