# L08/C14/T01 — Six Pillars

## Learning Objectives

- Apply Well-Architected pillars
- Use as design checklist

## Six Pillars

1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability (added 2021)

Each pillar: design principles + questions to ask.

## 1. Operational Excellence

Run + monitor systems to deliver business value.

Design principles:
- Operations as code (IaC, runbooks as code)
- Frequent, small, reversible changes
- Refine procedures frequently
- Anticipate failure
- Learn from operational events

Key questions:
- How prepare?
- How operate?
- How evolve?

Tools: CloudFormation, CDK, Systems Manager, X-Ray, CloudWatch.

## 2. Security

Protect info + systems.

Design principles:
- Strong identity foundation (IAM, IdP)
- Traceability (CloudTrail, GuardDuty)
- Security at all layers (defense in depth)
- Automate security best practices
- Protect data in transit + at rest
- Keep people away from data (automate)
- Prepare for security events

Key questions:
- How secure workload?
- How manage identities?
- How detect events?
- How protect networks?
- How protect compute?
- How classify + protect data?
- How respond to incidents?

Tools: IAM, KMS, GuardDuty, Security Hub, WAF, Shield, Macie.

## 3. Reliability

Workload performs intended function correctly + consistently.

Design principles:
- Test recovery procedures
- Automatically recover
- Scale horizontally
- Stop guessing capacity
- Manage change in automation

Key questions:
- How manage service quotas + constraints?
- How plan network topology?
- How design for failure?
- How back up data?
- How manage change?

Tools: Multi-AZ, Auto Scaling, Route 53 health checks, ELB, Backup, Step Functions.

## 4. Performance Efficiency

Use compute efficiently to meet requirements; maintain as demand changes.

Design principles:
- Democratize advanced tech (managed services)
- Go global in minutes
- Use serverless
- Experiment more often
- Mechanical sympathy (use right hardware)

Key questions:
- How select architecture?
- How select compute?
- How select storage?
- How select database?
- How select network?
- How review architecture?

Tools: Lambda, Fargate, ALB, CloudFront, Aurora, DynamoDB.

## 5. Cost Optimization

Deliver value at lowest price point.

Design principles:
- Implement cloud financial management
- Adopt consumption model (pay for what you use)
- Measure overall efficiency
- Stop spending on undifferentiated heavy lifting
- Analyze + attribute expenditure

Key questions:
- How awareness + governance?
- How cost-effective resources?
- How match supply + demand?
- How optimize over time?

Tools: Cost Explorer, Budgets, Compute Optimizer, Trusted Advisor, Savings Plans.

## 6. Sustainability

Environmental impact.

Design principles:
- Understand impact
- Establish goals
- Maximize utilization
- Anticipate new efficient services
- Use managed services
- Reduce downstream impact

Tools: AWS Customer Carbon Footprint Tool.

For: ESG; cost typically aligns (less waste = lower CO2).

## Trade-offs

Pillars often pull against each other:
- Reliability vs Cost (more redundancy = more cost)
- Performance vs Cost (bigger = expensive)
- Security vs Operations (process slows ops)
- Sustainability vs Performance (lower-power CPU might be slower)

Architect explicitly trades.

## How To Use

For new system / review:
1. Walk through pillars
2. Per question: how do we handle?
3. Identify gaps
4. Prioritize improvements
5. Iterate

## Trusted Advisor

AWS service; gives recommendations across pillars:
- Cost: idle resources, low-utilization
- Performance: service limits, throughput
- Security: open ports, IAM
- Fault Tolerance: backups, multi-AZ
- Service Limits

For Business / Enterprise Support: full set.

## Well-Architected Tool

AWS service; structured review:
```bash
aws wellarchitected create-workload --workload-name myApp ...
```

Answer questions per pillar; get report; track over time.

Free.

## Example: Operational Excellence

Design questions for a service:
- IaC in place?
- Deployment automated?
- Rollback tested?
- Runbooks for top 10 incidents?
- Metrics + alerting?
- Postmortems for incidents?
- Game days?

Score each; improve.

## Example: Security

- All resources encrypted?
- Least-privilege IAM?
- MFA on all humans?
- CloudTrail enabled?
- GuardDuty enabled?
- WAF on public endpoints?
- Secrets in Secrets Manager?
- Logging centralized?

## Example: Reliability

- Multi-AZ?
- Auto Scaling?
- DR plan (RTO/RPO defined)?
- Backups tested?
- Health checks?
- Circuit breakers?
- Chaos drills?

## Pattern: Lens

Domain-specific Well-Architected guidance:
- Serverless Lens
- SaaS Lens
- ML Lens
- IoT Lens
- HPC Lens
- Streaming Media Lens
- Financial Services Lens

Apply general pillars + domain specifics.

## Workload Review Cadence

- New workload: WAR before launch
- Major changes: WAR
- Quarterly / annually: review existing

## Output

- Gaps identified
- Action items per priority
- Tracked in JIRA / similar
- Owned by team
- Re-reviewed after fixes

## Common Mistakes

- WAR as one-time (no follow-up)
- Score-driven (game system; not actually improve)
- Ignoring sustainability
- Not making explicit trade-offs

## Best Practices

- Built into design process (not post-hoc)
- Multi-pillar each decision
- Document trade-offs
- Continuous improvement
- Use tools (WAR Tool, Trusted Advisor)
- Cross-functional team for review

## Anti-Patterns

- "We're WAR-aligned" without evidence
- Pillar per team (silos)
- Reliability + cost ignored for performance

## Real Examples

Tier-0 service:
- Reliability: 5 9s; multi-region active-active
- Cost: $$$; less optimization for perf
- Performance: low latency

Internal admin tool:
- Reliability: 3 9s OK
- Cost: minimize
- Performance: acceptable for users
- Operational: less automation OK

Same framework; different choices.

## Quick Refs

```bash
# WAR Tool
aws wellarchitected create-workload --workload-name myWorkload ...
aws wellarchitected list-workloads

# Trusted Advisor (Business / Enterprise support)
aws support describe-trusted-advisor-checks --language en
```

## Interview Prep

**Mid**: "Six pillars."

**Senior**: "WAR for tier-0 service."

**Staff**: "Drive WAR culture in org."

## Next Topic

→ [T02 — Running a WAR (Well-Architected Review)](T02-Well-Architected-Review.md)
