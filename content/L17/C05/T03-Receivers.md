# L17/C05/T03 — Receivers (PagerDuty, Slack, OpsGenie)

## Learning Objectives

- Configure receivers
- Pick by use case

## Receiver Types

- PagerDuty (paging)
- OpsGenie (paging)
- Slack (chat)
- Microsoft Teams
- Email
- Webhook (custom)
- Discord
- Telegram
- VictorOps (Splunk)
- Pushover

## PagerDuty

```yaml
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: INTEGRATION_KEY
        description: '{{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
        severity: '{{ if eq .CommonLabels.severity "critical" }}critical{{ else }}warning{{ end }}'
        client: 'Alertmanager'
        client_url: 'https://alertmanager.example.com'
```

Service key from PagerDuty service.

## Slack

```yaml
receivers:
  - name: slack
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#alerts'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'
        send_resolved: true
        actions:
          - type: button
            text: 'Runbook'
            url: '{{ .CommonAnnotations.runbook_url }}'
```

## Slack Templates

```
{{ define "slack.title" }}
[{{ .Status }}] {{ .GroupLabels.alertname }}
{{ end }}

{{ define "slack.text" }}
{{ range .Alerts }}
*Severity:* {{ .Labels.severity }}
*Service:* {{ .Labels.service }}
*Description:* {{ .Annotations.description }}
{{ if .Annotations.runbook_url }}*Runbook:* <{{ .Annotations.runbook_url }}>{{ end }}
{{ end }}
{{ end }}
```

## OpsGenie

```yaml
receivers:
  - name: opsgenie
    opsgenie_configs:
      - api_key: API_KEY
        message: '{{ .CommonAnnotations.summary }}'
        description: '{{ .CommonAnnotations.description }}'
        priority: '{{ if eq .CommonLabels.severity "critical" }}P1{{ else }}P3{{ end }}'
        teams: '{{ .CommonLabels.team }}'
```

## Email

```yaml
receivers:
  - name: email
    email_configs:
      - to: 'team@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp:587'
        auth_username: ...
        auth_password: ...
        send_resolved: true
```

For: less urgent.

## Webhook

```yaml
receivers:
  - name: custom
    webhook_configs:
      - url: 'https://my-service/alert'
        send_resolved: true
        http_config:
          bearer_token: TOKEN
```

For: custom integration.

## Multiple in One Receiver

```yaml
receivers:
  - name: backend-team
    slack_configs:
      - api_url: ...
        channel: '#backend'
    pagerduty_configs:
      - service_key: ...
```

Both notifications.

## Templates File

```yaml
templates:
  - '/etc/alertmanager/templates/*.tmpl'
```

External templates:
```
{{ define "slack.title" }}...{{ end }}
{{ define "slack.text" }}...{{ end }}
```

## Routing Examples

### Severity → Channel
```yaml
routes:
  - matchers: [severity = critical]
    receiver: pagerduty
  - matchers: [severity = warning]
    receiver: slack-warnings
  - matchers: [severity = info]
    receiver: slack-info
```

### Team → Receiver
```yaml
routes:
  - matchers: [team = backend]
    receiver: backend-receiver
  - matchers: [team = frontend]
    receiver: frontend-receiver
```

## Notification Config

```yaml
slack_configs:
  - send_resolved: true   # also notify on resolve
    api_url: ...
```

For: track resolution.

## Rate Limiting

PagerDuty: rate-limited by their side.
Slack: rate-limited.

Alertmanager: `group_wait`, `repeat_interval`.

For: avoid spam.

## Action Buttons (Slack)

```yaml
actions:
  - type: button
    text: 'Acknowledge'
    url: 'https://alertmanager/api/v2/silences/...'
  - type: button
    text: 'View Dashboard'
    url: 'https://grafana/...'
```

For: interactive.

## Notify On Resolve

```yaml
send_resolved: true
```

Sends "resolved" when alert clears.

For: closure clarity.

## Vendor Choice

### PagerDuty
- Standard paging
- Rich integrations
- $$$

### OpsGenie
- Similar; Atlassian
- Often cheaper

### VictorOps
- Splunk-owned
- ChatOps-friendly

### FireHydrant / incident.io
- More than paging (incident mgmt)

## Multi-Region

For HA:
- Multiple Alertmanager instances
- Cluster mode (deduplicates)
- Per-region instances

For: avoid single-paging-source.

## Test Notifications

```bash
# Send test alert
amtool alert add alertname=Test severity=critical -a "summary=test alert"
```

Or via API.

## Best Practices

- Severity → action mapping
- Runbook in every alert
- Templates consistent
- send_resolved on
- Test routing before prod
- Action buttons (Slack)
- Document receivers

## Common Mistakes

- All to Slack (no page → no response)
- No runbook
- Generic descriptions
- send_resolved off
- No HA receivers

## Quick Refs

```yaml
receivers:
  - name: NAME
    pagerduty_configs / slack_configs / opsgenie_configs / email_configs / webhook_configs:
      - ...

# Send resolved
send_resolved: true

# Template
api_url + channel + title + text
```

## Interview Prep

**Mid**: "Receiver types."

**Senior**: "Notification routing."

**Staff**: "On-call workflow."

## Next Topic

→ [T04 — Alert Hygiene](T04-Alert-Hygiene.md)
