# L08/C11/T05 — CloudTrail for Audit

## Learning Objectives

- Use CloudTrail for audit
- Detect security events

## CloudTrail

Records every AWS API call:
- Who
- What
- When
- From where
- Result

For: audit, compliance, security investigation, debugging.

## Default Trail

Every account: 90-day Event History (free):
- All Management Events (CreateUser, RunInstances, etc.)
- Searchable in console

For longer: create Trail.

## Trails

Persistent recording to S3:
```bash
aws cloudtrail create-trail --name org-trail \
  --s3-bucket-name trail-logs --is-multi-region-trail
```

Multi-region: captures all regions.
Organization trail: all accounts in Org.

## Event Types

### Management Events
Default. Account-level operations:
- IAM (CreateUser, AttachPolicy)
- EC2 (RunInstances, TerminateInstances)
- S3 (CreateBucket, PutBucketPolicy)

Free for first copy.

### Data Events
Optional. Per-object operations:
- S3 (GetObject, PutObject)
- Lambda (Invoke)
- DynamoDB (GetItem, PutItem)

$0.10 per 100k events. Expensive at scale; enable selectively.

### Insights Events
ML-based anomaly detection:
- Unusual API call rate
- New API source
- Errored API spike

Costs extra.

## Event Record

```json
{
  "eventTime": "2026-06-09T10:00:00Z",
  "eventSource": "s3.amazonaws.com",
  "eventName": "PutBucketPolicy",
  "userIdentity": {
    "type": "AssumedRole",
    "arn": "arn:aws:sts::123:assumed-role/admin/alice"
  },
  "sourceIPAddress": "192.168.1.1",
  "userAgent": "aws-cli/...",
  "requestParameters": {...},
  "responseElements": {...},
  "errorCode": null
}
```

## S3 Destination

Logs JSON.gz files in S3:
```
s3://trail-logs/AWSLogs/123/CloudTrail/us-east-1/2024/06/09/...json.gz
```

Lifecycle: archive to Glacier; delete after retention.

## CloudWatch Logs Destination

Optional: stream to CloudWatch Logs for alerting.

```bash
aws cloudtrail update-trail --name org-trail --cloud-watch-logs-log-group-arn ... --cloud-watch-logs-role-arn ...
```

## Log File Integrity

Sign log files; verify untampered:
```bash
aws cloudtrail enable-log-file-validation --name org-trail
```

Logs digest file every hour.

Use:
```bash
aws cloudtrail validate-logs --trail-arn ... --start-time ...
```

For compliance / forensics.

## Athena Queries

Query S3 logs:
```sql
SELECT eventName, COUNT(*) FROM cloudtrail
WHERE eventTime > '2024-06-09'
  AND userIdentity.arn LIKE '%alice%'
GROUP BY eventName
```

Setup table (Glue catalog) one-time.

## Alerting Examples

### Root Login
```sql
eventSource = 'signin.amazonaws.com'
AND userIdentity.type = 'Root'
```

Always concerning.

### IAM Policy Change
```sql
eventName IN ('PutUserPolicy', 'AttachUserPolicy', ...)
```

### Console Login Without MFA
```sql
eventName = 'ConsoleLogin'
AND additionalEventData.MFAUsed = 'No'
```

### Disabling Security
```sql
eventName IN ('StopLogging', 'DeleteTrail', 'DeleteFlowLogs')
```

### Cross-Account Activity
```sql
sourceIPAddress NOT IN (corp IPs)
```

## Insights

Auto-detect anomalies:
- Sudden spike in API calls
- New source IP
- Unusual error rate

Enable per trail.

## Org Trail

For multi-account: one trail at org level:
- All accounts log to central S3
- Security team analyzes
- Member accounts can't disable

```bash
aws cloudtrail create-trail --name org --s3-bucket-name org-trail-logs --is-organization-trail --is-multi-region-trail
```

## Lake (CloudTrail Lake)

Newer: SQL-queryable event store:
```bash
aws cloudtrail create-event-data-store --name lake --advanced-event-selectors ...
```

Built-in SQL; no Athena setup. 7-year retention.

Cost: per ingestion + per query.

For: long-term audit query.

## Best Practices

- Org trail (all accounts)
- Multi-region
- Log file validation
- Logs to S3 (cheap long-term)
- Optional: Lake for SQL query
- Alerts on critical events
- SCP prevents disable trail

## What CloudTrail Doesn't Log

- Data plane (S3 GetObject is Data Event; not default)
- App-level events (only AWS API)
- Worker app errors (use CloudWatch Logs)

## Pricing

Management Events: first copy free.
Additional trails: $2/100k events.
Data Events: $0.10/100k.
Insights: $0.35/100k.
Lake: $2.50/GB ingested + queries.

For typical account: $50-500/mo.

## Data Events Strategy

Enabling all = expensive.

Selective:
- S3 buckets with sensitive data
- Specific Lambda functions
- Critical DynamoDB tables

```bash
--data-resources '[{"Type":"AWS::S3::Object","Values":["arn:aws:s3:::sensitive-bucket/"]}]'
```

## Real-Time Alerting

```
CloudTrail → CloudWatch Logs → Subscription Filter (pattern match) → Lambda → PagerDuty
```

Sub-second alerts on dangerous actions.

## Common Mistakes

- No org trail (per-account chaos)
- Logging to bucket without protection (deletable)
- No alerting (just sit in S3)
- Disabling trails for cost (compliance fail)

## Integration

- Security Hub: aggregates findings
- GuardDuty: uses CloudTrail data
- Config: complements (state vs activity)

## CloudTrail vs CloudWatch Logs

| | CloudTrail | CW Logs |
|---|---|---|
| Captures | AWS API | App logs |
| Format | Defined | Free-form |
| Retention | S3 long-term | CW Logs (configurable) |
| Search | Athena | Insights |

Both important; different purposes.

## Audit Use Cases

- Who deleted that S3 bucket?
- When was this role created?
- Who accessed prod from new IP?
- Compliance evidence

## Incident Response

CloudTrail timeline:
- Detection
- Container actions
- Containment audit

Critical for forensics.

## Quick Refs

```bash
# Create trail
aws cloudtrail create-trail --name org --s3-bucket-name ... --is-multi-region-trail

# Start logging
aws cloudtrail start-logging --name org

# Lookup recent events (90-day Event History)
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket

# Validate logs
aws cloudtrail validate-logs --trail-arn ...
```

## Interview Prep

**Mid**: "CloudTrail use cases."

**Senior**: "Detect malicious activity."

**Staff**: "Audit strategy multi-account."

## Next Topic

→ Move to [L08/C12 — Infrastructure as Code on AWS](../C12/README.md)
