# L08/C11 — Observability on AWS

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-CloudWatch.md) | CloudWatch Metrics, Logs, Alarms | 1 hr |
| [T02](T02-Logs-Insights.md) | CloudWatch Insights & Contributor Insights | 0.5 hr |
| [T03](T03-XRay.md) | X-Ray Tracing | 1 hr |
| [T04](T04-Managed-Prom-Grafana.md) | Managed Prometheus & Grafana | 0.5 hr |
| [T05](T05-CloudTrail.md) | CloudTrail for Audit | 1 hr |

## CloudWatch Metrics

### Default Metrics
- EC2: CPUUtilization, NetworkIn/Out, etc. (1-min for detailed monitoring, $)
- ELB: RequestCount, TargetResponseTime, HTTPCode_Target_5XX_Count
- RDS: CPU, Connections, FreeableMemory, ReadIOPS
- Lambda: Invocations, Errors, Duration, Throttles
- ECS/EKS: CPU/MemoryUtilization, container insights
- API Gateway: Latency, 4XX/5XX Error
- DynamoDB: ConsumedRead/WriteCapacityUnits, ThrottledRequests

### Custom Metrics
Push via PutMetricData or CloudWatch Agent (high-resolution: 1-sec).
- Per-metric cost (small but accumulates with cardinality)
- Use dimensions sparingly

### Embedded Metric Format (EMF)
Lambda logs structured JSON; CloudWatch extracts metrics automatically:
```json
{
  "_aws": {
    "Timestamp": 1234567890,
    "CloudWatchMetrics": [{
      "Namespace": "myapp",
      "Dimensions": [["service"]],
      "Metrics": [{"Name": "latency", "Unit": "Milliseconds"}]
    }]
  },
  "service": "payments",
  "latency": 123
}
```

## CloudWatch Logs

### Concepts
- **Log Group**: collection of streams
- **Log Stream**: sequential events from one source
- **Retention**: per log group (1 day to never; default never — costly)
- **Metric Filter**: extract metrics from log patterns (count errors, latency)
- **Subscription Filter**: stream logs to Lambda/Kinesis/Firehose

### Always Set Retention
Default is "never expire" — set to 7-30-90 days based on need.

```bash
aws logs put-retention-policy --log-group-name X --retention-in-days 30
```

### Centralized Logging
- Org CloudTrail + cross-account log destination
- Subscription to send to log archive account
- Or ship to 3rd-party (Datadog, Splunk, ELK)

## CloudWatch Alarms

```
Metric → Statistic → Period → Threshold
                                  ↓
                          Alarm State (ALARM, OK, INSUFFICIENT)
                                  ↓
                          SNS Topic → Email, Slack, PagerDuty
```

### Composite Alarms
Combine multiple alarms with AND/OR logic; reduce false pages.

### Anomaly Detection Alarms
ML model on metric history; alarm on deviation rather than absolute threshold.

## CloudWatch Logs Insights

Ad-hoc query language for logs:
```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
| sort @timestamp desc
| limit 100
```

```
parse @message "user=* status=*" as user, status
| filter status >= 400
| stats count() by user
| sort count desc
```

Useful for incident investigation. Pay per GB scanned.

## Contributor Insights

Real-time analysis of high-cardinality logs:
- "Top IPs hitting /api/login"
- "Top error sources"
- Continuously runs; surfaces top-N

## X-Ray

AWS-native distributed tracing.

### Concepts
- **Trace**: end-to-end request
- **Segment**: work in a single service
- **Subsegment**: nested work (e.g., DB call)
- **Annotation**: indexed key-value
- **Metadata**: unindexed key-value

### Instrumentation
- Auto via AWS SDK integration (boto3, AWS SDK for JS, etc.)
- Lambda has built-in X-Ray opt-in
- ECS/EKS: X-Ray daemon as sidecar
- Manual via X-Ray SDK

### Service Map
Auto-derived from traces; shows latency and error rates per service.

### X-Ray vs OpenTelemetry
- OTel is the open standard; portable
- X-Ray is AWS-specific
- AWS Distro for OpenTelemetry (ADOT) bridges — recommended for new builds

## Managed Prometheus (AMP)

AWS-managed Prometheus-compatible service:
- Scrapes your endpoints (or remote_write from your Prometheus)
- Scales to billions of samples
- PromQL via API
- IAM auth (no in-product user mgmt)

## Managed Grafana (AMG)

AWS-managed Grafana:
- IAM Identity Center integration
- Plugin pre-approved
- Datasources: AMP, CloudWatch, RDS, OpenSearch, Athena, etc.

## CloudTrail

API call audit log. Three types:
- **Management Events**: control-plane (every API call by default)
- **Data Events**: data-plane (S3 object reads, Lambda invokes; off by default; expensive)
- **Insights Events**: AWS-detected anomalies in API patterns

### Trail Configuration
- Single-region or all-regions (use all-regions)
- Org Trail: covers all accounts in org
- Logs to S3 + optional CloudWatch Logs + optional CloudWatch Events/EventBridge

### Best Practices
- Org trail with all-regions
- Logs to centralized log archive account
- S3 bucket policy locks logs (Object Lock)
- Forward to SIEM (Splunk, Datadog)
- Configure CloudTrail Lake for SQL queries

## Cost Considerations

Observability cost can spiral:
- **CloudWatch Logs**: $0.50/GB ingest + $0.03/GB stored + $0.005/GB Insights queried
- **Custom Metrics**: $0.30/metric/month
- **X-Ray**: $5/M traces + $0.50/M scanned
- **CloudTrail Data Events**: $0.10/100K events
- **Datadog/New Relic**: $$$/host/month

Tactics:
- Set log retention
- Sample high-volume traces
- Drop noisy logs at source
- Use EMF instead of custom PutMetric for high-cardinality
- Move historical logs to S3 (Glacier eventually)

## Interview Themes

- "Walk me through observability stack on AWS"
- "Compare CloudWatch and Prometheus"
- "Design centralized logging across 100 accounts"
- "X-Ray vs OpenTelemetry"
- "Reduce CloudWatch bill — strategies"
- "What does CloudTrail capture?"
