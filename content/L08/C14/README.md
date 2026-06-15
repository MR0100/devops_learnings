# L08/C14 — Well-Architected Framework

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Six-Pillars.md) | Six Pillars (Operational Excellence, Security, Reliability, Performance, Cost, Sustainability) | 1.5 hr |
| [T02](T02-Well-Architected-Review.md) | Running a WAR (Well-Architected Review) | 1 hr |

## The Six Pillars

```
1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability (added 2021)
```

### Operational Excellence
- IaC for everything
- Frequent, small, reversible changes
- Anticipate failure and learn from operations
- Runbooks and playbooks
- Continuous improvement

Key services: CloudFormation/CDK, Systems Manager, CloudTrail, X-Ray.

### Security
- Strong identity foundation
- Traceability (audit, monitoring)
- Defense in depth
- Automate security best practices
- Encrypt in transit and at rest
- Prepare for incidents

Key services: IAM, KMS, GuardDuty, Security Hub, WAF, Shield, Inspector.

### Reliability
- Test recovery procedures
- Automatic failure recovery
- Scale horizontally
- Stop guessing capacity
- Manage change in automation

Key services: Multi-AZ, Auto Scaling, Route 53 failover, AWS Backup, RDS replicas.

### Performance Efficiency
- Democratize advanced tech (use managed services)
- Go global in minutes
- Use serverless when possible
- Experiment
- Mechanical sympathy (match tech to use case)

Key services: CloudFront, Global Accelerator, Aurora, Lambda, DynamoDB.

### Cost Optimization
- Cloud financial management
- Adopt a consumption model
- Measure efficiency
- Stop paying for undifferentiated heavy lifting (use managed)
- Analyze and attribute expenditure

Key services: Cost Explorer, Budgets, Savings Plans, RIs, Trusted Advisor, Cost Anomaly Detection.

### Sustainability
- Understand impact
- Set sustainability goals
- Maximize utilization
- Use newer, more efficient hardware
- Use managed services (provider amortizes overhead)
- Minimize downstream impact (reduce data transferred)

Key services: ARM (Graviton), spot instances, serverless, S3 Intelligent-Tiering.

## Design Principles Across Pillars

```
1. Stop guessing capacity
2. Test systems at production scale
3. Automate to make experimentation easier
4. Allow evolutionary architectures
5. Drive architectures with data
6. Improve through game days
```

## WAR (Well-Architected Review)

A structured review session against the framework.

### Process
1. Pick a workload (one product/service)
2. Use the Well-Architected Tool in console
3. Answer ~50 questions across the 6 pillars
4. Each question has best-practice answers; flag risks
5. Build remediation plan with priorities
6. Re-review after addressing high-risk items

### Outcomes
- High-Risk Issues (HRIs) — fix urgently
- Medium-Risk Issues
- Notes on improvements

### Frequency
- New workloads: at design and pre-launch
- Existing: yearly minimum
- Major changes: at architectural shift

### Lens
Specialized question sets for domains:
- Serverless Lens
- IoT Lens
- ML Lens
- SaaS Lens
- HPC Lens
- Hybrid Networking Lens

## Sample Risk Topics

### Operational Excellence
- "Do you have runbooks for common failures?"
- "Are deployments automated and rollback-tested?"

### Security
- "Are all S3 buckets covered by Block Public Access?"
- "Is MFA required for human users?"
- "Are secrets rotated?"

### Reliability
- "Have you load-tested at 2× peak?"
- "Are backups tested via restore?"
- "Do you have a DR plan with measured RTO/RPO?"

### Performance Efficiency
- "Have you considered ARM/Graviton?"
- "Is the database tier scaled to load?"

### Cost
- "Do you have Savings Plans / RI coverage for baseline?"
- "Are unused resources removed?"

### Sustainability
- "Are workloads scheduled when grid carbon is low?"
- "Are old log retention policies in place?"

## Building a WAR Practice

- Train staff engineers as WAR facilitators
- Include WAR results in OKRs
- Track HRI burn-down quarterly
- Share lessons across teams
- Integrate with launch readiness reviews

## Interview Themes

- "What are the six pillars of Well-Architected?"
- "Walk me through a WAR you've run"
- "Common HRIs in reliability pillar"
- "Sustainability — what AWS levers actually move the needle?"
