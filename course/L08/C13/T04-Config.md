# L08/C13/T04 — Config & Conformance Packs

## Learning Objectives

- Use AWS Config
- Apply conformance packs

## AWS Config

Records resource state + changes. Evaluate against rules.

For: compliance, change tracking, drift detection.

## Enable

```bash
aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=arn:...
aws configservice put-delivery-channel --delivery-channel name=default,s3BucketName=config-bucket
aws configservice start-configuration-recorder --configuration-recorder-name default
```

Records all resources by default; filter to subset.

## Resource Inventory

For every supported AWS resource:
- Current configuration
- Change history
- Relationships

## Config Rules

Evaluate compliance:
- Managed rules (AWS-provided)
- Custom rules (Lambda-backed)

Example managed:
- `s3-bucket-public-read-prohibited`
- `ec2-security-group-attached-to-eni`
- `rds-instance-public-access-check`
- `root-account-mfa-enabled`

```bash
aws configservice put-config-rule --config-rule file://rule.json
```

## Evaluation

Periodic (e.g., daily) or change-triggered.

Reports COMPLIANT or NON_COMPLIANT per resource.

## Remediation

Auto-fix non-compliant via SSM Automation:
- Public S3 → enable Block Public Access
- Unencrypted volume → encrypt (re-create)
- Open SG → close port

Be careful: false positives could cause outages.

## Conformance Packs

Bundle of Config rules + remediation as code:
```bash
aws configservice put-conformance-pack --conformance-pack-name CIS --template-s3-uri s3://...
```

Deploy across org.

## AWS-Managed Packs

- CIS AWS Foundations Benchmark
- AWS Foundational Best Practices
- HIPAA
- PCI DSS
- NIST 800-53
- Operational Best Practices for X

For compliance frameworks: enable the pack.

## Custom Conformance Pack

Define your rules + remediations:
```yaml
Resources:
  ConfigRule1:
    Type: AWS::Config::ConfigRule
    Properties:
      Source: {...}
```

CloudFormation-style.

## Org-Wide

Delegated admin:
```bash
aws configservice put-organization-conformance-pack ...
```

Pack deployed in all accounts.

## Cost

Per evaluation:
- $0.001 per evaluation
- $0.003 per config item recorded

For 1000 resources × 10 rules × 1 eval/day = ~$3/mo.

Plus S3 storage (cheap).

Can add up at scale (5 figures/mo for large orgs).

## Recording Scope

To save: record only some resource types:
```yaml
RecordingGroup:
  AllSupported: false
  ResourceTypes:
    - AWS::EC2::Instance
    - AWS::S3::Bucket
    - AWS::IAM::Role
```

## Inventory Use Cases

- Resource count + spend
- Find unencrypted volumes
- Find public S3
- Find unused IAM
- Audit drift

```bash
aws configservice select-resource-config --expression "
  SELECT resourceId, resourceName 
  FROM AWS::EC2::Instance 
  WHERE configuration.state.name = 'running'
"
```

SQL-like queries (Config Advanced Queries).

## Change Tracking

For each resource: timeline of configuration changes.

```bash
aws configservice get-resource-config-history --resource-type AWS::S3::Bucket --resource-id my-bucket
```

For: "What changed when?"; rollback investigation.

## Security Hub Integration

Config rules feed Security Hub. Compliance state per standard.

## Relationships

Config tracks resource relationships:
- EC2 → VPC, SG, Subnet
- S3 → KMS key

For: blast radius analysis.

## Common Managed Rules

- s3-bucket-public-read-prohibited
- s3-bucket-public-write-prohibited
- s3-bucket-server-side-encryption-enabled
- s3-bucket-versioning-enabled
- ec2-security-group-attached-to-eni
- ec2-instance-no-public-ip
- restricted-ssh
- restricted-common-ports
- root-account-mfa-enabled
- iam-password-policy
- iam-user-mfa-enabled
- rds-instance-public-access-check
- encrypted-volumes
- vpc-flow-logs-enabled
- cloudtrail-enabled
- ebs-snapshot-public-restorable-check

## Custom Rule

Lambda-backed:
```python
def lambda_handler(event, context):
    config_item = event["invokingEvent"]["configurationItem"]
    # Check compliance
    if check(config_item):
        return {"compliance_type": "COMPLIANT"}
    return {"compliance_type": "NON_COMPLIANT"}
```

Plus IAM permissions; register as Config rule.

## SSM Auto-Remediation

```yaml
Resources:
  S3BucketRemediation:
    Type: AWS::Config::RemediationConfiguration
    Properties:
      ConfigRuleName: s3-bucket-public-read-prohibited
      TargetId: AWS-DisableS3BucketPublicReadWrite
      TargetType: SSM_DOCUMENT
      Parameters:
        BucketName:
          ResourceValue:
            Value: RESOURCE_ID
```

Auto-runs SSM doc on non-compliance.

## When NOT Config

- Tiny account; cost > benefit
- All resources change frequently; noise
- Compliance not needed

For most prod: enable.

## Compliance Reports

Security Hub renders Config data into standards reports.

For audits: export.

## Best Practices

- Enable at org level
- Conformance pack for frameworks
- Custom rules for org policies
- Auto-remediation for clear-cut
- Alerts on critical NON_COMPLIANT
- Document exceptions

## Common Mistakes

- Recording everything (cost)
- No remediation (passive observation)
- Custom rules without testing
- Per-account chaos (use org)

## Limitations

- Some resources not yet supported
- Delayed evaluation (not instant)
- Cost at huge scale

## Alternatives

CSPM tools (Wiz, Lacework) often more capable but expensive.

For AWS-only: Config + Security Hub baseline; vendor on top.

## Integration

Config + EventBridge:
```json
{
  "source": ["aws.config"],
  "detail-type": ["Config Rules Compliance Change"]
}
```

→ Lambda → Slack / Jira.

## Quick Refs

```bash
# Enable
aws configservice put-configuration-recorder ...
aws configservice put-delivery-channel ...
aws configservice start-configuration-recorder --configuration-recorder-name default

# Rule
aws configservice put-config-rule --config-rule file://rule.json

# Query
aws configservice select-resource-config --expression "SELECT * FROM AWS::EC2::Instance"

# Conformance pack
aws configservice put-conformance-pack --conformance-pack-name CIS --template-s3-uri s3://...
```

## Interview Prep

**Mid**: "What is Config."

**Senior**: "Conformance pack for CIS."

**Staff**: "Org-wide compliance program."

## Next Topic

→ [T05 — Detective, Audit Manager](T05-Detective-Audit.md)
