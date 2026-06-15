# L20/C09/T04 — HIPAA, GDPR, FedRAMP

## Learning Objectives

- Know specialty compliance
- Apply per domain

## HIPAA

US healthcare:
- Protect PHI (Protected Health Information)
- Covered entities + business associates

## PHI

Identifiable health info:
- Name + diagnosis
- SSN + treatment
- Image + name

For: handle carefully.

## HIPAA Requirements

### Privacy Rule
- Use minimum necessary
- Patient access
- Authorization

### Security Rule
- Admin: training, policies
- Physical: facility access
- Technical: encryption, audit

### Breach Notification
- 60 days disclosure
- HHS notification

## BAA

Business Associate Agreement:
- Between covered entity + vendor
- Vendor obligations

Cloud providers: BAA available (AWS, Azure, GCP).

## Cloud HIPAA

- AWS HIPAA-eligible services
- Azure HITRUST + HIPAA
- GCP HIPAA-eligible

Use compliant services only.

## Implementation

- Encrypt at rest + transit
- MFA
- Access logs
- Audit (6 years)
- BAA with vendors

## Penalties

- Up to $1.5M per violation
- Criminal in severe cases

For: real consequences.

## GDPR

EU General Data Protection Regulation (2018):
- Personal data of EU residents
- Anywhere in world (extraterritorial)

## Data Subject Rights

- Access
- Rectification
- Erasure (right to be forgotten)
- Portability
- Object

Implement in product.

## Lawful Basis

For processing:
- Consent
- Contract
- Legal obligation
- Vital interests
- Public interest
- Legitimate interests

Document for each.

## Privacy by Design

Build privacy in:
- Minimize data
- Pseudonymize
- Encrypt
- Time-limited retention

## DPA

Data Processing Agreement:
- Between controller + processor
- Required for vendors

Cloud providers: DPA available.

## Penalties

- Up to 4% global revenue
- Or €20M

## Examples

### Right to Erasure
User deletes:
- Remove from primary DB
- Remove from backups (within reason)
- Anonymize for analytics

### Data Export
User requests:
- Provide JSON of all data
- Within 30 days

### Breach
- Notify within 72 hr
- Detail nature, impact

## Schrems II

EU → US data transfer:
- Privacy Shield invalid
- Standard Contractual Clauses
- Or EU data residency

For: many SaaS choose EU regions.

## FedRAMP

US federal cloud auth:
- 3 levels (Low / Moderate / High)
- For SaaS selling to gov
- NIST 800-53 based

## Process

- Sponsor agency
- 3PAO (3rd Party Assessment)
- ATO (Authorization to Operate)
- Continuous monitoring

Long: 1-3 years.

## Cost

- $500k-2M+ first time
- Continuous monitoring ongoing

For: large federal contracts.

## Cloud Options

- AWS GovCloud
- Azure Government
- GCP for Gov

In-scope.

## Other Standards

### HITRUST
Healthcare HITRUST CSF.

### CCPA / CPRA
California privacy.

### LGPD
Brazil's GDPR equivalent.

### PIPEDA
Canada.

For: multi-region.

## Best Practices

### Universal
- Encrypt at rest + transit
- MFA
- Logs
- Access control
- Backup tested
- Incident response
- Vendor management

### Per Specific
- HIPAA: BAA, PHI tracking
- GDPR: DPA, subject rights
- FedRAMP: NIST 800-53

## Tools

- Drata / Vanta (multi-framework)
- OneTrust (privacy)
- TrustArc

## When Each

### HIPAA
- US healthcare
- Plus health insurance, providers, etc.

### GDPR
- EU customers
- EU residents data

### FedRAMP
- US federal customers

## Implementation Tips

- Map data flows
- Tag data classification
- Tools enforce policies
- Annual training
- Continuous audit

## Common Mistakes

- Skip BAA (HIPAA violation)
- Ignore GDPR for global (still applies)
- Underestimate FedRAMP timeline
- Wrong cloud region

## Multi-Compliance

Map controls:
- Many overlap
- Reuse evidence

Tools like Drata: cross-reference.

## Quick Refs

```
HIPAA: US healthcare (PHI)
GDPR:  EU data subjects (anywhere)
FedRAMP: US federal cloud

Tools:
- Drata / Vanta (SaaS multi-framework)
- OneTrust (privacy)

Cloud:
- BAA / DPA available
- Region selection matters
```

## Interview Prep

**Junior**: "What do HIPAA, GDPR, and FedRAMP each cover?" — HIPAA protects US healthcare data (PHI), GDPR protects EU residents' personal data and privacy rights, and FedRAMP standardizes security authorization for cloud services used by US federal agencies.

**Mid**: "What does running PHI in the cloud (HIPAA) require?" — A signed Business Associate Agreement (BAA) with the cloud provider, use of only HIPAA-eligible services, encryption of PHI in transit and at rest, strict access controls, and audit logging of PHI access.

**Senior**: "What are the key engineering implications of GDPR?" — Data-subject rights drive design: you need data inventory/mapping, a lawful basis, the ability to honor access/erasure ('right to be forgotten') and portability requests, data-minimization and retention limits, and controls on cross-border transfer of EU personal data.

**Staff**: "How do you handle compliance across multiple regions and frameworks at once?" — Map a unified control baseline to each framework, use data residency and regional isolation to keep data under the right jurisdiction (EU data in EU, FedRAMP workloads in authorized US boundaries), automate evidence per framework, and design data flows so cross-border transfer is deliberate and lawful rather than incidental.

## Next Topic

→ Move to [L21 — Databases & Data Management](../../L21/README.md)
