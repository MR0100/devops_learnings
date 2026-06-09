# L17/C05 — Alertmanager

## Topics

- **T01 Routing Tree** — Match alerts to receivers
- **T02 Silences, Inhibitions** — Reduce noise during incidents
- **T03 Receivers (PagerDuty, Slack, OpsGenie)** — Where alerts go
- **T04 Alert Hygiene** — Avoiding alert fatigue

## Architecture

```
Prometheus (evaluates rules) → fires alerts via HTTP
   ↓
Alertmanager (one or HA cluster)
   - Receives
   - Groups
   - Deduplicates
   - Silences
   - Inhibits
   - Routes
   ↓
Receivers: PagerDuty, Slack, OpsGenie, email, webhook
```

Alertmanager runs separately from Prometheus. Should be HA (3 replicas) and use gossip for dedup.

## Routing Tree

```yaml
route:
  receiver: default-slack
  group_by: [alertname, cluster, service]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [severity="critical"]
      receiver: pagerduty
      continue: true   # also send to next match
    - matchers: [team="payments"]
      receiver: payments-slack
    - matchers: [severity="warning", env="prod"]
      receiver: ops-slack

receivers:
  - name: default-slack
    slack_configs:
      - channel: '#alerts'
        api_url: <webhook>
        title: '{{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: pagerduty
    pagerduty_configs:
      - service_key: <key>
        severity: '{{ .CommonLabels.severity }}'
        description: '{{ .CommonAnnotations.summary }}'

  - name: payments-slack
    slack_configs:
      - channel: '#payments-alerts'
        ...
```

### Group
- `group_by: [alertname, cluster]` — alerts with same labels become ONE notification
- `group_wait: 30s` — wait this long for more alerts to join group
- `group_interval: 5m` — between updates to same group
- `repeat_interval: 4h` — re-send if still firing

## Silences

Suppress alerts matching labels:
- During maintenance windows
- During incidents you already know about
- For known noisy alerts during investigation

```bash
amtool silence add severity="warning" cluster="prod-us" --duration=2h --comment="Maintenance"
```

Or via web UI / API.

## Inhibitions

Suppress alerts when other alerts are firing.

```yaml
inhibit_rules:
  - source_matchers: [severity="critical", service="api"]
    target_matchers: [severity="warning", service="api"]
    equal: [cluster]
```

If a critical alert is firing for api in prod, suppress warning alerts for api in same prod (avoid duplicates).

Use case: `NodeDown` inhibits all per-pod alerts on that node.

## Receivers

### PagerDuty
```yaml
pagerduty_configs:
  - service_key: <key>     # or routing_key for events API v2
    severity: '{{ .CommonLabels.severity }}'
    description: '{{ .CommonAnnotations.summary }}'
    links:
      - href: '{{ .CommonAnnotations.runbook }}'
        text: 'Runbook'
```

### Slack
```yaml
slack_configs:
  - api_url_file: /etc/secrets/slack-webhook
    channel: '#alerts'
    title: '{{ template "slack.default.title" . }}'
    text: '{{ template "slack.default.text" . }}'
    actions:
      - type: button
        text: 'Silence'
        url: '{{ .ExternalURL }}/...silence-url...'
```

### Webhook
Generic; useful for custom routing or in-house systems:
```yaml
webhook_configs:
  - url: https://hooks.example.com/alerts
    send_resolved: true
```

### Email
Less common today; useful for low-urgency:
```yaml
email_configs:
  - to: ops@example.com
    from: alertmanager@example.com
    smarthost: smtp.example.com:587
```

## Templates

Customize alert formatting:
```yaml
templates:
  - /etc/alertmanager/templates/*.tmpl
```

```
{{ define "slack.custom.title" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }}
{{ end }}
```

## Alert Hygiene

### Symptoms vs Causes
- **Symptoms** (page these): customer-impacting (high error rate, latency)
- **Causes** (log these): high CPU, high memory, queue depth

Prefer symptom-based alerts. Causes are often co-incidental; chasing them creates noise.

### SLO-Based Alerts
Use error budget burn rate (Google SRE). Multi-window, multi-burn-rate. Far fewer false positives than threshold alerts.

### Critical vs Warning vs Info
- **Critical**: page someone now
- **Warning**: handled in business hours
- **Info**: dashboard / log; no notification

If everything is critical, nothing is.

### Per-Alert SLO
Every alert should have:
- Severity
- Owner (team label)
- Summary (one line, business impact)
- Description (details)
- Runbook (link)
- Dashboard link

Without these, on-call doesn't know what to do.

### Quarterly Alert Review
- Which alerts fired most? Top noise sources.
- Which never fired? Remove or tune.
- Which page-but-don't-act? Remove (low value).
- New alerts needed?

## HA

```
3 Alertmanager replicas with gossip (—cluster.peer)
Prometheus sends to all 3
Alertmanagers gossip state; only one sends notification
```

## Common Mistakes

- Threshold alerts ("CPU > 80%") that page without business impact
- No `for:` clause (alerts on transient spikes)
- Vague summaries ("disk problem")
- No runbook link
- One mega-alert that's hard to interpret
- Silence forever instead of fixing root cause

## Interview Themes

- "Walk me through routing tree"
- "Silences vs inhibitions"
- "Avoid alert fatigue — how?"
- "SLO burn rate alerts vs threshold"
- "Receiver options"
