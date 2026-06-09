# L08/C11/T02 — CloudWatch Insights & Contributor Insights

## Learning Objectives

- Query logs with Insights
- Identify top contributors

## CloudWatch Logs Insights

SQL-like query for logs.

```
fields @timestamp, @message, level
| filter level = "ERROR"
| stats count() by service
| sort count desc
| limit 20
```

## Commands

- `fields`: select
- `filter`: WHERE
- `stats`: aggregate
- `sort`: ORDER BY
- `limit`: LIMIT
- `parse`: extract via pattern
- `display`: present

## Filter Patterns

```
filter level = "ERROR"
filter @message like /timeout/
filter status_code >= 500
filter @message =~ /^Failed to/
```

## Parse

```
parse @message "user=*, action=*" as user, action
| stats count() by user, action
```

Extract structured fields from text.

## Stats Functions

- count()
- sum(field)
- avg(field)
- min, max
- percentile(field, 99)
- stddev
- earliest, latest

## Time Range

In console: picker.
CLI:
```bash
aws logs start-query \
  --log-group-name /myapp \
  --start-time 1717584000 \
  --end-time 1717587600 \
  --query-string 'fields @message | filter level = "ERROR"'
```

## Cross-Log-Group

Query multiple:
```
fields @timestamp, @log
| filter level = "ERROR"
```

Add log groups via `--log-group-names`.

## Performance Tips

- Limit time range
- Filter early (less data to process)
- Specific log group
- Index frequently-queried fields (log group level)

## Common Queries

### Top Errors
```
fields @message
| filter level = "ERROR"
| stats count() as freq by @message
| sort freq desc
| limit 10
```

### Slow Requests
```
fields @timestamp, request_id, duration
| filter duration > 1000
| sort duration desc
| limit 50
```

### Error Rate Over Time
```
fields level
| stats count() as total, sum(if(level="ERROR", 1, 0)) as errors by bin(5m)
| display total, errors, errors/total*100 as error_pct
```

### User Impact
```
fields user_id, level
| filter level = "ERROR"
| stats count() by user_id
| sort count desc
```

## Pricing

$0.005 per GB scanned.

For 100 GB scan: $0.50. Cheap for ad-hoc.

## vs CloudWatch Logs API

Direct API: filter-log-events.
Insights: more powerful queries.

For automation: API. For investigation: Insights.

## Contributor Insights

Identify top contributors to metric:
- Top 10 IPs causing 5xx errors
- Top users in slow queries
- Top API consumers

```bash
aws cloudwatch put-insight-rule --rule-name TopErrorIPs --rule-definition '{
  "Schema": {"Name": "CloudWatchLogRule", "Version": 1},
  "LogGroupNames": ["/myapp/api"],
  "LogFormat": "JSON",
  "Contribution": {
    "Keys": ["$.source_ip"],
    "Filters": [{"Match": "$.status_code", "GreaterThan": 499}]
  }
}'
```

Time-series of top N keys.

## Use Cases

- DDoS detection (top IPs)
- Top users in slow queries
- API consumer breakdown
- Cost attribution

## Cost

$0.50/M log events processed.

## Subscription Filters

Stream logs to other destinations:
```bash
aws logs put-subscription-filter \
  --log-group-name /myapp/api \
  --filter-name errors-to-kinesis \
  --filter-pattern '{$.level = "ERROR"}' \
  --destination-arn arn:aws:kinesis:...
```

For:
- Aggregating to central
- Real-time processing
- Cheaper external storage

## Log Format

Structured (JSON):
```json
{"timestamp": "...", "level": "ERROR", "user": "...", "message": "..."}
```

Insights handles JSON automatically.

Plain text: use `parse`.

## Anomaly Detection on Logs

Recently added: detect anomalous log patterns.

```bash
aws logs create-log-anomaly-detector --log-group-arn-list ... --anomaly-visibility-time 7
```

Identifies unusual events. For alerting on novel issues.

## Pattern Tab

Insights auto-identifies frequent patterns:
- "Login failed for user *"
- "Timeout after * seconds"

For: top events, deduplication.

## Saved Queries

Save frequent:
```bash
aws logs put-query-definition --name top-errors --query-string '...'
```

Teams share queries.

## Best Practices

- Structured (JSON) logs
- Log group per app/env
- Retention policy
- Subscription to S3 for long-term
- Saved queries for team
- Anomaly detection on critical

## Common Mistakes

- Plain text logs (parse painful)
- No retention (cost)
- Full scan everywhere (cost)
- Per-event PutLogEvents (use batch)

## CLI Workflow

```bash
# Start query
QUERY_ID=$(aws logs start-query --log-group-name /myapp --start-time ... --query-string '...' --query "queryId" --output text)

# Wait + get results
aws logs get-query-results --query-id $QUERY_ID
```

## Other Tools

- Athena over S3 logs (cheaper at scale)
- Loki (Grafana stack)
- Datadog / Splunk

For high volume: subscription to S3; Athena queries.

## Insights vs Athena

| | Insights | Athena |
|---|---|---|
| Source | Log groups | S3 |
| Setup | None | Glue catalog |
| Cost | $0.005/GB | $5/TB |
| Speed | Fast (small) | Fast (parallel) |

Insights for live; Athena for historical.

## Interview Prep

**Mid**: "Find errors in logs."

**Senior**: "Top API consumers — query."

**Staff**: "Log strategy for cost."

## Next Topic

→ [T03 — X-Ray Tracing](T03-XRay.md)
