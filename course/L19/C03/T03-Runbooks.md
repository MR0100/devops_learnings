# L19/C03/T03 — Runbooks

## Learning Objectives

- Write runbooks
- Maintain effectively

## Runbook

Step-by-step guide:
- For specific alert / scenario
- Reduce MTTR
- Knowledge sharing

## Structure

```markdown
# Runbook: High Error Rate (API)

## Alert
Alertname: HighErrorRate
Severity: critical

## Symptoms
- Error rate > 5% for 10 min
- User reports of failures

## Likely Causes
- Recent deploy
- DB issue
- Upstream service down
- Cert expiration

## Investigation
1. Check recent deploys: kubectl rollout history deploy/api
2. Check DB status: kubectl get pods -l app=db
3. Check upstream: curl https://upstream/health
4. Check logs: kubectl logs -l app=api --since=10m | grep ERROR

## Mitigation
- If recent deploy: rollback (kubectl rollout undo)
- If DB issue: see DB runbook
- If upstream: failover or wait

## Escalation
If unresolved in 30 min:
- Page secondary on-call
- Notify product manager

## Related
- /runbooks/db-down
- /runbooks/upstream-failure
```

## Trigger Linkage

In alert:
```yaml
annotations:
  runbook_url: 'https://runbooks/api/high-error-rate'
```

PagerDuty shows; on-call clicks.

## Investigation Steps

Specific commands:
```
kubectl get pods -n prod
curl localhost:8080/health
SELECT COUNT(*) FROM events WHERE ts > now() - INTERVAL '5 min';
```

Not vague:
"check the database"

## Mitigation Steps

Order by cost:
1. Quick fixes (restart pod)
2. Workarounds (failover)
3. Deeper diagnosis

## Don't Page Without Runbook

If alert has no runbook: don't alert.

For: forces documentation.

## Sources

- Wiki (Confluence, Notion)
- Git repo
- PagerDuty Operations Console
- FireHydrant
- internal portal

## Format

Markdown common:
- Readable
- Version controlled
- Easy update

## Searchability

For: find in middle of night.
- Index
- Common terms
- Linked from alerts

## Living Document

Update:
- After incident (postmortem action)
- New finding
- Old commands change

## Anti-Patterns

### Stale
3 years old; commands wrong.

### Theory Only
"Diagnose the issue." Not actionable.

### Decision Trees Too Deep
Confusing.

### No Mitigation
"Investigate" without "fix".

### Hidden
On someone's laptop. Useless.

## Best Practices

- Per-alert runbook
- Linked in annotation
- Tested (drill)
- Updated after incidents
- Searchable
- Clear language

## Common Mistakes

- No runbook (start)
- Outdated
- Vague
- Long-winded
- Skip mitigation

## Templates

```
# Runbook: <Name>

## Alert
- Name
- Severity

## Symptoms
- ...

## Likely Causes
- ...

## Investigation
1. Step
2. Step

## Mitigation
1. Step
2. Step

## Escalation
- When + who

## Related
- Other runbooks
- Dashboards
```

## Drill

Quarterly:
- Pick runbook
- Have engineer follow
- Identify gaps
- Update

For: test usability.

## Auto-Runbooks

Some systems (ResolveAI, AI):
- Generate runbook draft from postmortem
- Suggest steps based on alert

For: speed.

## On-Call Onboarding

New on-call:
- Review top 10 runbooks
- Drill 3-5
- Shadow

For: prepared.

## Patterns

### Quick Diagnosis
3-5 commands.

### Common Causes
Listed.

### Specific Mitigations
Per cause.

### Escalation Triggers
Time-based.

## Examples

### Disk Full
```
Investigate:
  df -h
  du -sh /var/log/*

Mitigation:
  Rotate logs: logrotate -f /etc/logrotate.conf
  Expand: aws ec2 modify-volume --volume-id ...
```

### Service Down
```
Investigate:
  kubectl get pods -l app=X
  kubectl describe pod X
  kubectl logs X

Mitigation:
  Restart: kubectl rollout restart deploy/X
  Rollback: kubectl rollout undo deploy/X
```

## Quick Refs

```markdown
# Runbook structure
## Alert
## Symptoms
## Likely Causes
## Investigation (commands)
## Mitigation (commands)
## Escalation
## Related
```

## Interview Prep

**Mid**: "What's a runbook."

**Senior**: "Runbook patterns."

**Staff**: "On-call enablement."

## Next Topic

→ [T04 — Healthy On-Call Practices](T04-Healthy-On-Call.md)
