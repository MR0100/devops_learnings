# L08/C11/T01 — CloudWatch Metrics, Logs, Alarms

## Learning Objectives

- Use CloudWatch monitoring
- Set alarms

## CloudWatch

AWS native monitoring:
- Metrics
- Logs
- Alarms
- Dashboards
- Synthetics
- Application Insights

## Metrics

AWS services emit default metrics:
- EC2: CPUUtilization, NetworkIn, etc.
- RDS: ReadIOPS, DatabaseConnections, etc.
- Lambda: Invocations, Errors, Duration

15-month retention.

## Custom Metrics

```python
import boto3
cw = boto3.client("cloudwatch")
cw.put_metric_data(
    Namespace="MyApp",
    MetricData=[{
        "MetricName": "OrderProcessed",
        "Value": 1,
        "Unit": "Count",
        "Dimensions": [{"Name": "Service", "Value": "Orders"}]
    }]
)
```

Pricing:
- $0.30 per metric per month (after free tier)
- Or use EMF (Embedded Metric Format)

## EMF (Embedded Metric Format)

Log structured JSON; CloudWatch extracts as metric. No PutMetric call.

```python
import json
print(json.dumps({
    "_aws": {
        "Timestamp": 1717584000,
        "CloudWatchMetrics": [{
            "Namespace": "MyApp",
            "Dimensions": [["Service"]],
            "Metrics": [{"Name": "Latency", "Unit": "Milliseconds"}]
        }]
    },
    "Service": "Orders",
    "Latency": 123
}))
```

Cheaper at scale (logs ingestion vs PutMetric).

## Logs

Log groups (per app); streams (per source). Search via Insights.

```bash
aws logs create-log-group --log-group-name /myapp/api
aws logs put-log-events --log-group-name /myapp/api --log-stream-name stream1 ...
```

Pricing:
- $0.50/GB ingestion
- $0.03/GB storage

For high-log apps: significant. Sample / filter.

## Log Retention

Default: indefinite (expensive). Configure:
```bash
aws logs put-retention-policy --log-group-name /myapp/api --retention-in-days 30
```

For dev: 7 days. Prod: 30-90 days. Compliance: 1-7 years (cheap storage tier).

## Log Insights

SQL-like query:
```
fields @timestamp, @message
| filter level = "ERROR"
| stats count() by service
| sort count desc
```

For ad-hoc analysis.

Cost: $0.005/GB scanned.

## Alarms

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name HighCPU \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --evaluation-periods 2 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:...
```

Alarm states:
- OK
- ALARM
- INSUFFICIENT_DATA

Actions: SNS, Auto Scaling, EC2 (stop/terminate).

## Composite Alarms

Combine alarms:
```
(HighCPU OR HighMemory) AND NOT DeploymentInProgress
```

Reduce alert noise.

## Alarm Best Practices

- Page only actionable
- Alert quickly on user impact; less urgently on warnings
- Combine related signals (composite)
- Test alarms regularly
- Document runbook per alarm

## Anomaly Detection

ML-based threshold:
- CloudWatch learns metric pattern
- Alerts on deviation

No fixed threshold; adapts.

For variable load. Tunable sensitivity.

## Dashboards

```bash
aws cloudwatch put-dashboard --dashboard-name MyDash --dashboard-body file://dash.json
```

JSON-defined; widgets (metric line, log query, etc.).

For team view of service health.

## Cross-Account Sharing

Enable cross-account CloudWatch:
- Central account aggregates metrics from many accounts
- Single pane of glass

## Container Insights

Detailed metrics for ECS / EKS:
- Per-container CPU / memory
- Per-pod
- Per-task

```bash
aws ecs put-account-setting --name containerInsights --value enabled
```

Cost: small. Enable for prod.

## Lambda Insights

Per-invocation detailed metrics:
- Init duration
- Memory usage
- Network
- Cold start

Enable per function. Extra cost.

## Synthetics

Canaries: scheduled scripts test endpoints:
- Heartbeat: hit URL
- API: complex API check
- UI: Selenium

Detects issues before users.

## Application Insights

Auto-discover apps; auto-generate dashboards / alarms.

For .NET, Java, SQL Server typical.

## Costs to Watch

- Custom metrics ($0.30 each)
- Log ingestion ($0.50/GB)
- Log Insights queries ($0.005/GB)
- Detailed monitoring (extra metrics; per-resource)

For typical app: $50-500/mo CloudWatch.

## Cost Optimization

- EMF over PutMetric
- Sampling
- Log retention policies
- Detailed monitoring only where needed
- Cross-account aggregation
- Subscriptions to S3 / external (cheaper storage)

## Subscription Filters

Stream logs to:
- Lambda (process)
- Kinesis (downstream pipeline)
- Firehose (S3 / OpenSearch)

For: real-time alerting, aggregation, cheaper long-term storage.

## Alarms on Logs

Metric Filter: extract metric from logs:
```
[$.ERROR]   # if "ERROR" appears
```

Alarm on metric: HighErrorRate.

## Anomaly Detection

For metrics with patterns (daily seasonality):
- Auto-learn band
- Alert outside band

## CloudWatch Alarms vs Targets

| Need | Use |
|---|---|
| 5-min granularity user-impact | Metric alarm |
| Anomaly | Anomaly detector |
| Multi-signal | Composite |
| Log keyword | Metric filter + alarm |
| Endpoint health | Synthetics canary |

## Common Mistakes

- Too many alarms (alert fatigue)
- Alarming on indirect causes
- No runbook
- Single threshold for variable load (use anomaly)
- Forgetting INSUFFICIENT_DATA state

## Best Practices

- SLI-based alarms (user impact metrics)
- Documented runbook per alarm
- Test alarms (chaos drill)
- Anomaly for variable
- Composite to reduce noise
- Cross-account aggregation

## Datadog / Vendor

Many use Datadog / NewRelic / Honeycomb for observability:
- Better UX
- More features
- More expensive
- Less AWS-native

CloudWatch baseline; vendor for advanced.

## Quick Refs

```bash
# Put metric
aws cloudwatch put-metric-data --namespace MyApp --metric-data MetricName=X,Value=1

# Get metric
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --statistics Average --period 300 --start-time ... --end-time ...

# Alarm
aws cloudwatch put-metric-alarm --alarm-name HighCPU ...

# Logs
aws logs tail /myapp/api --follow
aws logs filter-log-events --log-group-name /myapp/api --filter-pattern "ERROR"
```

## Interview Prep

**Mid**: "CloudWatch metrics."

**Senior**: "Alerting strategy."

**Staff**: "Observability for 100 microservices."

## Next Topic

→ [T02 — CloudWatch Insights & Contributor Insights](T02-Logs-Insights.md)
