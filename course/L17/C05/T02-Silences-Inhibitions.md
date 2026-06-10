# L17/C05/T02 — Silences, Inhibitions

## Learning Objectives

- Use silences temporarily
- Configure inhibit rules

## Silence

Suppress alerts for a window:
- Maintenance
- Known issue
- Investigation

## Create

UI: Alerts → Silences → New.

Or CLI:
```bash
amtool silence add alertname=HighErrorRate \
  service=api \
  -d 4h \
  -c "Investigating"
```

Or API:
```bash
curl -X POST http://alertmanager/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [
      {"name": "service", "value": "api", "isRegex": false}
    ],
    "startsAt": "...",
    "endsAt": "...",
    "comment": "Investigating",
    "createdBy": "alice"
  }'
```

## Matchers

Match alerts by labels:
```
service = api
severity =~ "critical|warning"
```

## Duration

- Specific time range
- Or duration (4h, 1d)

For: maintenance windows.

## Auto-Expire

End time required. Auto-removed.

For: no orphan silences.

## Best Practice

- Always include comment + author
- Short windows
- Targeted matchers (not too broad)
- Review weekly

## Inhibition

Auto-suppress alerts based on others:
```yaml
inhibit_rules:
  - source_matchers:
      - severity = critical
      - alertname = NodeDown
    target_matchers:
      - severity =~ warning|info
    equal: ['cluster', 'instance']
```

If NodeDown critical fires, all warning/info on same node suppressed.

For: cascade alerts.

## Use Cases

### Cluster Down → Suppress Pod Alerts
```yaml
- source_matchers:
    - alertname = ClusterDown
  target_matchers: []
  equal: ['cluster']
```

When cluster down: don't page about pods.

### Datacenter Outage → Suppress Service
```yaml
- source_matchers:
    - alertname = DataCenterOutage
  target_matchers:
    - severity = warning
  equal: ['region']
```

### Critical → Suppress Warning Same Alert
```yaml
- source_matchers:
    - severity = critical
  target_matchers:
    - severity = warning
  equal: ['alertname', 'service']
```

## Cascade Cleanup

```
NodeDown critical
  → suppress PodNotReady warnings on same node
  → suppress HighLatency on same node
```

For: fewer false fires.

## Test Inhibits

```bash
amtool config routes test \
  alertname=PodNotReady \
  severity=warning \
  cluster=A \
  node=n1
```

See if any matched + inhibited.

## Silence vs Inhibit

| | Silence | Inhibit |
|---|---|---|
| Source | Manual | Other alert |
| Duration | Time-bound | While source active |
| Use | Maintenance, investigation | Cascade |
| Removal | Manual or auto-expire | When source resolves |

## Best Practices

### Silences
- Required comment
- Short duration
- Specific matchers
- Review regularly (find stale)

### Inhibits
- Document each
- Common cascade rules
- Test config

## Common Mistakes

- Silence too broad (miss other issues)
- Silence forever (forgot)
- No inhibit (alert storms)
- Wrong equal (suppress wrong things)

## Audit

```bash
amtool silence list
```

Find:
- Expiring soon
- Long-running
- Broad matchers

## Maintenance Window Pattern

Before maintenance:
```bash
amtool silence add cluster=stage -d 2h -c "Maintenance"
```

After:
```bash
amtool silence expire SILENCE_ID
```

## On-Call Silence

For: investigation; remember to remove.

```bash
amtool silence add alertname=X -d 30m -c "Investigating: TICKET-123"
```

Short. Forces follow-up.

## Track Silences

Dashboard:
- Active silences
- Created by
- Expiry

For: avoid forgotten ones.

## Time-Window Routing (Alternative)

Instead of silence:
```yaml
- match:
    severity: critical
  receiver: pagerduty
  active_time_intervals:
    - business-hours
- match:
    severity: critical
  receiver: nighttime-mute
  active_time_intervals:
    - off-hours
```

Mute receiver: no notification.

For: scheduled quiet.

## Notifications

When silence created/expired:
- Webhook
- Audit log

For: ops awareness.

## Quick Refs

```bash
# Create
amtool silence add MATCHERS -d DURATION -c COMMENT

# List
amtool silence list

# Expire
amtool silence expire ID

# Query
amtool silence query MATCHERS
```

```yaml
# Inhibit
inhibit_rules:
  - source_matchers: [...]
    target_matchers: [...]
    equal: [...]
```

## Interview Prep

**Mid**: "Silence vs inhibit."

**Senior**: "Cascade alerts."

**Staff**: "Alert hygiene."

## Next Topic

→ [T03 — Receivers (PagerDuty, Slack, OpsGenie)](T03-Receivers.md)
