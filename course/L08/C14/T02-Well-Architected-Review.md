# L08/C14/T02 — Running a WAR (Well-Architected Review)

## Learning Objectives

- Run a WAR
- Apply findings

## Process

1. Choose workload
2. Schedule (4-8 hours typically)
3. Cross-functional attendees
4. Use WAR Tool
5. Answer questions per pillar
6. Identify HRIs (High Risk Issues)
7. Create remediation plan
8. Re-review in 6-12 months

## Pre-Work

- Architecture diagram
- Cost report
- Reliability metrics
- Recent incidents
- Security posture (Security Hub findings)
- Owner identified

## Attendees

- Workload owner
- Architect
- DevOps/SRE
- Security rep
- Business stakeholder
- Optional: AWS SA (Solutions Architect)

## Questions

Per pillar, ~5-10 questions. Each:
- "How do you ..."
- Pick best practices applied
- Note gaps

Example (Reliability):
- OPS01: How prepare workload?
- Choices: IaC; deployments automated; rollback tested; runbooks; ...
- You select what's true
- Unselected = gap

## Risks

Each gap = risk level:
- HRI (High Risk Issue): significant impact
- MRI (Medium): important
- Low

Priority: fix HRIs first.

## Improvement Plan

Per HRI:
- Owner
- Effort estimate
- Target date
- Track in your PM tool

## Output

- WAR report (PDF)
- Workload tracked in WAR Tool
- Trend over time

## Tools

### AWS WAR Tool
Free; built-in:
```bash
aws wellarchitected create-workload --workload-name X --description "..." --environment PRODUCTION ...
```

### Trusted Advisor
Per-check recommendations; complements WAR.

### Compute Optimizer
Right-sizing recommendations.

### Security Hub
Compliance posture.

Combine: WAR + auto checks.

## Cadence

- New workload: WAR before launch
- Quarterly for tier-0
- Annually for typical
- Always after major change

## Patterns

### Lightweight WAR
For small workloads: 1-2 hours; key questions.

### Deep WAR
For tier-0: full 8 hours; multi-session.

### Lens-Based
Apply lens (Serverless, SaaS) on top.

### Continuous WAR
Automate checks; ongoing posture (vs point-in-time).

## Anti-Patterns

- WAR theater (checkbox, no action)
- One-time (no follow-up)
- Same team grades themselves (bias)
- No business stakeholder
- Ignoring trade-offs

## Best Practices

- Outside facilitator (AWS SA or other team)
- Document trade-offs explicitly
- Action items with owner + date
- Track via JIRA
- Re-review in 6 months
- Celebrate improvements

## Improving HRIs

For each:
1. Understand root cause
2. Design fix
3. Estimate effort
4. Prioritize vs other work
5. Implement
6. Validate
7. Mark resolved

## Reporting

For leadership:
- Workload risk posture (HRI count over time)
- Trend per pillar
- Investment justified by risk reduction

## Lens Examples

### Serverless Lens
For Lambda-based:
- Cold start mitigation
- Idempotency
- Async patterns
- Cost optimization
- Observability with limited tools

### SaaS Lens
Multi-tenant:
- Tenant isolation
- Per-tenant data
- Noisy neighbor
- Onboarding automation
- Tenant cost attribution

### ML Lens
- Data prep pipelines
- Training cost
- Inference latency
- Model monitoring (drift)
- Bias / fairness

## Reality

Many companies do WAR:
- Quarterly for top workloads
- Pre-launch for new
- After incident
- Before re:Invent (good time for AWS engagement)

## ROI

- Find $50k/yr cost waste
- Prevent $1M incident
- Discover compliance gap
- Improve team understanding

WAR pays for itself many times over.

## Common Findings

Almost every WAR finds:
- Missing backup tests
- No rollback procedure
- Logs not centralized
- Some over-permissive IAM
- Cost waste (idle, oversize)
- Single AZ somewhere

## AWS Pro Services

For complex / high-stakes: AWS Professional Services or partner can facilitate WAR.

Cost: $$$ but expert-driven.

## Documentation

WAR report includes:
- Architecture diagram
- Q&A per pillar
- Risk summary
- Improvement plan
- Owner contact

Stored alongside workload docs.

## Integration with Architecture Review

Many companies have ARB (Architecture Review Board):
- New systems reviewed
- WAR as one input
- Cross-team standardization

## Common Mistakes

- WAR as gate (not learning)
- Ignoring findings
- Sub-team WAR only (silos)
- No facilitator
- Too long sessions (8 hr exhausting)

## Best Practices

- Multiple shorter sessions
- Facilitator outside team
- Document assumptions
- Prioritize HRIs ruthlessly
- Track improvements visibly
- Recognize done items

## Output Template

```
Workload: X
Date: 2024-06-09
Attendees: ...

Pillar Scores:
- Operational: 80% (was 70% last review)
- Security: 75%
- Reliability: 60% (HRI: no DR plan)
- Performance: 85%
- Cost: 90% (improved RIs)
- Sustainability: 70%

HRIs:
1. No DR plan (Reliability) - owner: Alice - due: 2024-08
2. ...

Trends: improving overall.
```

## Quick Refs

```bash
# Workload
aws wellarchitected create-workload --workload-name X --description "..." --environment PRODUCTION

# Answer question
aws wellarchitected update-answer --workload-id ... --lens-alias wellarchitected --question-id ...

# Report
aws wellarchitected get-lens-review-report --workload-id ... --lens-alias wellarchitected
```

## Interview Prep

**Mid**: "What is a WAR."

**Senior**: "Drive WAR for tier-0 service."

**Staff**: "Org-wide architecture program."

## Next Topic

→ Move to [L09 — Azure / GCP](../../L09/README.md)
