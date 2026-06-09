# L08/C01/T01 — Root Account, MFA, Billing Alarms

## Learning Objectives

- Secure new AWS account day-one
- Avoid bill shock

## Day-One Checklist

For every AWS account:
1. Strong root password
2. Hardware MFA on root
3. Stash root credentials offline
4. Create IAM user / SSO for daily use
5. Enable CloudTrail (multi-region)
6. Billing alerts
7. Enable Cost Explorer
8. Tag policies

Skip none. Each is one breach away from disaster.

## Root Account

Owns the account. Can:
- Close account
- Change support plan
- Modify root settings
- Cannot be restricted by IAM

Only it can:
- Change account name / email
- Cancel AWS support
- Restore IAM access (lockout)

Use it: setup, infrequent root-only tasks. Otherwise NEVER.

## MFA Setup

Hardware key (YubiKey) > Authy/Google Auth.

```
Account → Security Credentials → MFA → Assign hardware key
```

Lose key = locked out. Have backup.

## CloudTrail

Records every API call. From day 1:
```
CloudTrail → Trails → Create trail
- Name: organization-trail
- Apply to all regions: yes
- Storage: S3 bucket (in this account or central security)
- Log file validation: yes
- Encrypt logs with KMS: yes
- Retention: 1 year+
```

Watch for:
- Root account login
- IAM user creation
- Policy changes
- Resource creation in unusual regions

## Billing Alarms

Set early. Out-of-control bills are common.

### Budget
```
Billing → Budgets → Create
- Cost budget
- Monthly, $X threshold
- Email alert at 80%, 100%, 120% forecasted
```

Multiple budgets per team/project.

### CloudWatch Billing Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name BillingAlarm-100USD \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

Sends SNS notifications. Wire SNS to Slack / PagerDuty.

### Cost Anomaly Detection
```
Billing → Cost Anomaly Detection
- Create monitor; AWS auto-detects unusual spend
- Per service / per linked account
- Alerts on >$X anomaly
```

ML-based. Catches what static thresholds miss.

## Cost Explorer

Enable (free):
```
Billing → Cost Explorer → Enable
```

Lets you analyze:
- Cost by service
- By tag
- By account
- Forecasts

Can take 24 hours to populate.

## Default VPC

Each region has default VPC. Delete it if not using; cleanups easier:
```
aws ec2 delete-vpc --vpc-id vpc-default
```

Or keep; just don't deploy to it.

## Region Strategy

Decide:
- Primary region (e.g., us-east-1)
- DR region (e.g., us-west-2)
- Block unused regions via SCP (covered T02)

Each new region = attack surface; cost monitoring; CloudTrail trail.

## Account Email

Use:
- aws+account-name@yourcompany.com (catchall)
- Or aws-prod@, aws-dev@ (separate emails)

Avoid: individual employee emails (leaves with employee).

## Support Plan

| Tier | Cost | Response |
|---|---|---|
| Basic | Free | None |
| Developer | $29/mo | 12h business |
| Business | 3% bill / $100 min | <1h critical |
| Enterprise On-Ramp | $5500/mo | <30 min critical |
| Enterprise | $15k+/mo | <15 min critical |

Production = Business minimum. Mission-critical = Enterprise.

## Initial IAM

Create:
- IAM user "admin" (you) — bridge to SSO
- IAM role "OrganizationAccountAccessRole" (for org)
- Admin group with AdministratorAccess

Better: don't create IAM users; use Identity Center (SSO) from start.

## Tagging Strategy

Define tags from day 1:
- Environment (dev / staging / prod)
- Team
- Project
- CostCenter
- Owner
- ManagedBy (terraform / manual)

Enforce via tag policies (Organizations).

## Service Quotas

Default limits per service. Some low (5 VPCs/region, 1000 Lambda concurrent).

Request increases proactively for known needs.

```
Service Quotas → request increase
```

## GuardDuty

Threat detection. Enable:
```
GuardDuty → Enable
```

Cost: $0.50/GB CloudTrail processed; ~$10-50/mo small account.

Catches:
- Suspicious IAM activity
- Crypto-mining
- Compromised credentials
- Reconnaissance

## Security Hub

Aggregates findings:
- GuardDuty
- Inspector (vuln scan)
- Macie (S3 PII scan)
- Config (compliance)

Enable for any production.

## Initial Network Diagram

Even simple account: document
- Regions used
- VPCs
- Public/private subnets
- Gateways

Update as architecture grows. Map saves debugging.

## What NOT To Do Day-One

- Use root key for app
- Open SG 0.0.0.0/0 anywhere
- Deploy resources without tagging
- No backup strategy
- No CloudTrail
- Generous IAM policies "for now"

These compound; harden later is hard.

## Quick Refs

```bash
# Whoami
aws sts get-caller-identity

# Account ID
aws sts get-caller-identity --query Account --output text

# Configured profiles
aws configure list-profiles
```

## Interview Prep

**Junior**: "Why MFA on root?"

**Mid**: "New account hardening checklist."

**Senior**: "Bill spike — investigate."

**Staff**: "Multi-account governance with Organizations."

## Next Topic

→ [T02 — AWS Organizations, SCPs, OUs](T02-Organizations-SCPs.md)
