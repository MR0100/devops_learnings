# L20/C09/T01 — SOC 2

## Learning Objectives

- Understand SOC 2
- Prepare for audit

## SOC 2

Service Organization Control 2:
- AICPA standard
- SaaS / service providers
- Trust Services Criteria

## Trust Services Criteria

- **S**ecurity (required)
- **A**vailability
- **C**onfidentiality
- **P**rocessing integrity
- **P**rivacy

Pick which apply.

## Types

### SOC 2 Type 1
Point-in-time:
- Controls designed
- Implemented at date

### SOC 2 Type 2
Period-over-time:
- Controls operating effectively
- 3-12 month observation

Type 2: more rigorous; required by most enterprises.

## Audit

Independent CPA firm.

Process:
1. Define scope
2. Document controls
3. Implement / operate
4. Audit period (Type 2)
5. Auditor reviews
6. Report issued

Cost: $20k-100k+ first year.

## Common Controls

### Access Control
- MFA
- Least privilege
- Quarterly access reviews
- Onboarding / offboarding

### Encryption
- At rest
- In transit
- Key management

### Logging
- Centralized
- Retention 1+ year
- Reviewed

### Change Management
- PRs reviewed
- Tests required
- Deployment gates

### Incident Response
- Documented
- Postmortems
- Practice

### Vendor Management
- Risk assessment
- SOC 2 of vendors
- DPA agreements

### Business Continuity
- DR plan
- Backups tested
- RTO/RPO defined

### HR
- Background checks
- Training (security awareness)
- Confidentiality agreements

## Documentation

Each control:
- Description
- Owner
- Evidence
- Periodicity

For: auditor reviews.

## Tools

- Drata
- Vanta
- Secureframe
- Thoropass

SaaS:
- Automate evidence collection
- Track controls
- Integrate cloud + GitHub + Slack

## Workflow

```
1. Pick scope (Security minimum)
2. Drata / Vanta sets up
3. Controls defined
4. Connect: AWS, GitHub, Slack, etc.
5. Auto-collect evidence
6. Address gaps
7. Audit (Type 1 first)
8. Operate 6 months
9. Type 2 audit
10. Report
```

## Continuous

Type 2 ongoing:
- Quarterly review
- Yearly audit
- Annual renewal

## CIS Benchmark

Implementation guide:
- AWS, GCP, Azure
- K8s
- Linux

Maps to SOC 2 controls.

## Evidence Examples

### Access Review
Quarterly:
- Export AWS IAM users
- Review by manager
- Remove unused

### Patching
- Track patches applied
- < 30 days for critical

### Monitoring
- Alert on access patterns
- Logs reviewed weekly

## Auditor Questions

- Show me access reviews
- Show me patching cadence
- Show me incident response example
- Show me change management

Be ready with evidence.

## Time to Compliance

- Type 1: 3-6 months prep
- Type 2: 1 year+ total
- Renewal: annual

## Cost

- First audit: $30-100k
- Annual: $20-50k
- Plus tooling ($1k-5k/month)

For: B2B SaaS often required.

## ROI

- Win enterprise deals
- Lower insurance
- Investor confidence

## SOC 2 vs ISO 27001

| | SOC 2 | ISO 27001 |
|---|---|---|
| Origin | US (AICPA) | International (ISO) |
| Scope | service orgs | any org |
| Audit | yearly | 3-year cert |
| Detail | controls per category | full ISMS |

US: SOC 2 dominant.
International: ISO 27001 + SOC 2.

## Best Practices

- Drata / Vanta from start
- Map controls to current practices
- Quarterly access reviews
- Documented incident response
- Annual training

## Common Mistakes

- Last-minute (months not enough)
- Skip evidence (audit fail)
- No continuous monitoring
- Drift from controls

## Specific SOC 2 Examples

### Access (CC6)
- MFA enforced (evidence: AWS reports)
- Quarterly review (evidence: ticket per quarter)
- Onboarding (evidence: HR system)

### Risk Assessment (CC3)
- Annual
- Documented
- Mitigations

### Vendor Management (CC9)
- List vendors
- Sub-SOC 2 reports collected

## Quick Refs

```
TSC: Security (req), Availability, Confidentiality, Processing Integrity, Privacy
Types: Type 1 (point-in-time), Type 2 (period)

Tools: Drata, Vanta, Secureframe
Time: 6 months prep + 6+ months for Type 2
Cost: $50k+ first year
```

## Interview Prep

**Junior**: "What is SOC 2?" — An attestation report (by an external auditor) that a service organization's controls meet the Trust Services Criteria — Security is required, plus optionally Availability, Confidentiality, Processing Integrity, and Privacy.

**Mid**: "SOC 2 Type I vs Type II — what's the difference?" — Type I attests controls are designed appropriately at a point in time; Type II tests that they operated effectively over a period (typically 3–12 months), which is what customers actually want to see.

**Senior**: "How do you prepare for a SOC 2 Type II audit?" — Define the controls (access, change management, monitoring, incident response), automate evidence collection over the observation window (logs, access reviews, ticket trails), run a readiness/gap assessment, then provide the auditor continuous evidence rather than a last-minute scramble.

**Staff**: "How do you build a compliance program that scales across frameworks?" — Implement controls once and map them to multiple frameworks (SOC 2, ISO 27001, etc.), automate evidence via a GRC tool wired to your systems, treat controls as code in CI/CD where possible, and make audit readiness a continuous state so adding a new framework is mostly re-mapping, not re-building.

## Next Topic

→ [T02 — ISO 27001](T02-ISO27001.md)
