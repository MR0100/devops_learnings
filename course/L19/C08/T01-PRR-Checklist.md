# L19/C08/T01 — PRR Checklist

## Learning Objectives

- Use PRR
- Productionize services

## PRR

Production Readiness Review:
- Checklist before launch
- Ensures ops ready

## Sections

### Monitoring
- Metrics (Prometheus)
- Logs (structured)
- Traces (OTel)
- Dashboards
- Alerts

### Alerting
- SLO-based
- Runbooks linked
- Tested

### On-Call
- Team assigned
- Rotation set
- Trained

### Capacity
- Forecast
- Headroom
- Auto-scale
- Load tested

### Resilience
- Multi-AZ
- Auto-restart
- Circuit breakers
- Retries
- Timeouts

### Security
- IAM roles
- Secrets rotation
- TLS
- Audit logs
- Pen test passed

### Deployment
- CI/CD
- Canary / rolling
- Rollback tested
- IaC

### DR
- Backup
- Restore tested
- RPO/RTO defined

### Data
- Encryption at rest + transit
- Backup
- Retention
- Compliance

### Performance
- Benchmarks
- SLO targets
- Limits set

### Cost
- Budget alert
- Tagging
- Optimization

### Docs
- Runbooks
- Architecture
- API docs
- Onboarding

## Severity

Per item:
- Required
- Recommended
- Optional

For: launch criteria.

## Process

### Self-Review
Team fills out.

### SRE Review
Sign-off.

### Launch

Or:
- Conditional launch
- Time-boxed waivers
- Follow-up items

## Anti-Patterns

### Skip PRR
"We'll address later."

Result: incident in week 1.

### Rubber Stamp
Check boxes without verifying.

### One-Time
Never revisited.

For: PRR is gate + ongoing.

## Continuous PRR

Quarterly:
- Re-review
- Update for changes
- Address gaps

## Templates

```markdown
## PRR Checklist: [Service Name]

### Owner
- Team:
- TL:

### Monitoring
- [ ] Metrics exposed
- [ ] Dashboards created
- [ ] SLI/SLO defined
- [ ] Alerts configured

### Alerting
- [ ] PagerDuty integration
- [ ] Runbooks for each alert
- [ ] Severity assigned

### On-Call
- [ ] Rotation defined
- [ ] Training done
- [ ] Escalation path

### Capacity
- [ ] Load tested at projected peak + 50%
- [ ] Auto-scale configured
- [ ] Resource limits set

### Resilience
- [ ] Multi-AZ deployment
- [ ] Health checks
- [ ] Graceful shutdown
- [ ] Retries
- [ ] Circuit breakers (if applicable)

### Security
- [ ] IAM least privilege
- [ ] Secrets in Vault
- [ ] TLS configured
- [ ] Security scan passed
- [ ] Pen test done

### Deployment
- [ ] CI/CD pipeline
- [ ] Canary or rolling
- [ ] Rollback tested

### DR
- [ ] Backup schedule
- [ ] Restore tested
- [ ] RPO documented
- [ ] RTO documented

### Data
- [ ] Encrypted at rest
- [ ] Encrypted in transit
- [ ] Backup verified
- [ ] Retention policy
- [ ] PII handling

### Docs
- [ ] Architecture diagram
- [ ] Runbooks
- [ ] API documentation
- [ ] Onboarding guide

### Sign-off
- Owner: ___
- SRE: ___
- Security: ___
- Date: ___
```

## Real PRRs

Google: "Production Readiness Review."
Netflix: similar gate.
Many enterprises: variations.

## Customizing

Per org:
- Add compliance items
- Add SOC 2
- Add HIPAA
- Add cost

For: tailored.

## Common Mistakes

- Skip entirely
- Check boxes; don't verify
- No follow-up
- Single launch (no quarterly)

## Best Practices

- Mandatory before launch
- Verified, not checked
- Quarterly review
- Waivers documented
- Templated + customized

## Quick Refs

```
PRR sections:
- Monitoring
- Alerting
- On-call
- Capacity
- Resilience
- Security
- Deployment
- DR
- Data
- Docs
```

## Interview Prep

**Mid**: "What's PRR."

**Senior**: "PRR template."

**Staff**: "Launch readiness."

## Next Topic

→ [T02 — Launch Reviews](T02-Launch-Reviews.md)
