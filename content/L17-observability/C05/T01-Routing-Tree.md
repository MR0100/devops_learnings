# L17/C05/T01 — Alertmanager Routing Tree

## Learning Objectives

- Route alerts properly
- Group + deduplicate

## Alertmanager

Handles alerts from Prom:
- Dedupe
- Group
- Route
- Silence
- Inhibit
- Notify (PagerDuty, Slack, etc.)

## Config

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: default
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  routes:
    - matchers:
        - severity = critical
      receiver: pagerduty
      continue: true
    - matchers:
        - team = frontend
      receiver: frontend-slack

receivers:
  - name: default
    slack_configs:
      - api_url: https://hooks.slack.com/...
        channel: '#alerts'
  - name: pagerduty
    pagerduty_configs:
      - service_key: KEY
  - name: frontend-slack
    slack_configs:
      - channel: '#frontend-alerts'
```

## Routing Tree

```
Root route
├─ Severity=critical → PagerDuty
└─ Team=frontend → #frontend-alerts
   ├─ Severity=warning → Slack only
   └─ Severity=critical → Slack + PagerDuty
```

Tree-walked; first match wins (unless continue).

## Match by Labels

```yaml
- matchers:
    - severity = critical
    - team =~ "backend|infra"
  receiver: backend-pager
```

## Group By

```yaml
group_by: ['alertname', 'cluster', 'service']
```

Alerts with same group values: one notification (with list).

For: avoid alert storm.

## Group Wait / Interval

```yaml
group_wait: 30s        # wait before sending first
group_interval: 5m     # wait before sending updates
repeat_interval: 4h    # remind
```

## continue: true

```yaml
- matchers:
    - severity = critical
  receiver: pagerduty
  continue: true       # also match subsequent routes
```

For: multiple receivers per alert.

## Receivers

```yaml
receivers:
  - name: NAME
    pagerduty_configs: [...]
    slack_configs: [...]
    email_configs: [...]
    webhook_configs: [...]
    opsgenie_configs: [...]
    pushover_configs: [...]
    victorops_configs: [...]
    discord_configs: [...]
```

## Slack

```yaml
slack_configs:
  - api_url: WEBHOOK_URL
    channel: '#alerts'
    title: '{{ .GroupLabels.alertname }}'
    text: |
      *Severity:* {{ .CommonLabels.severity }}
      *Service:* {{ .CommonLabels.service }}
      
      {{ range .Alerts }}
      *Description:* {{ .Annotations.description }}
      *Runbook:* {{ .Annotations.runbook_url }}
      {{ end }}
```

## PagerDuty

```yaml
pagerduty_configs:
  - service_key: INTEGRATION_KEY
    description: '{{ .CommonAnnotations.summary }}'
    severity: '{{ .CommonLabels.severity }}'
```

## OpsGenie

```yaml
opsgenie_configs:
  - api_key: KEY
    teams: 'backend'
    priority: P1
```

## Webhook

```yaml
webhook_configs:
  - url: 'https://my-handler/'
    send_resolved: true
```

For: custom integration.

## Templates

```yaml
templates:
  - '/etc/alertmanager/templates/*.tmpl'
```

```
{{ define "slack.title" }}
[{{ .Status }}] {{ .GroupLabels.alertname }}
{{ end }}
```

Use:
```yaml
slack_configs:
  - title: '{{ template "slack.title" . }}'
```

## High Availability

```yaml
cluster:
  peers:
    - 'alertmanager-1:9094'
    - 'alertmanager-2:9094'
```

Mesh sharing alert state. Dedupe across.

For: 3-node cluster typical.

## Common Patterns

### By Severity → Channel
```
critical → PagerDuty + Slack
warning → Slack ticket channel
info → log only
```

### By Team
```
team=backend → backend-team
team=frontend → frontend-team
```

### By Time
```yaml
- match:
    severity: critical
  active_time_intervals:
    - business-hours   # only during business hours
  receiver: pagerduty
- match:
    severity: critical
  receiver: night-pager
```

## Time Intervals

```yaml
time_intervals:
  - name: business-hours
    time_intervals:
      - weekdays: ['monday:friday']
        times:
          - start_time: 09:00
            end_time: 17:00
        location: America/New_York
```

For: route by time.

## Inhibit Rules

```yaml
inhibit_rules:
  - source_matchers:
      - severity = critical
      - alertname = NodeDown
    target_matchers:
      - severity =~ warning|info
    equal: ['cluster', 'instance']
```

NodeDown critical → suppress warning/info for same node.

For: reduce noise.

## Validate

```bash
amtool check-config alertmanager.yml
amtool config routes test
```

## Test Routing

```bash
amtool config routes show
amtool alert add alertname=Test severity=critical
```

## Best Practices

- Group_by service/cluster
- Sensible group_wait (avoid spam)
- Inhibit dependent alerts
- Per-team receivers
- Templates for consistency
- HA cluster
- Test routing

## Common Mistakes

- group_by too broad (huge groups)
- repeat_interval too short (spam)
- No HA (alert miss on restart)
- Wrong matchers
- No templates (inconsistent notifications)

## Quick Refs

```yaml
route:
  receiver: default
  group_by: [...]
  routes:
    - matchers: [...]
      receiver: ...
      continue: true|false

receivers:
  - name: ...
    pagerduty_configs / slack_configs / ...

inhibit_rules:
  - source_matchers: [...]
    target_matchers: [...]
```

## Interview Prep

**Mid**: "Alertmanager routing."

**Senior**: "Inhibit + group."

**Staff**: "Alert architecture."

## Next Topic

→ [T02 — Silences, Inhibitions](T02-Silences-Inhibitions.md)
