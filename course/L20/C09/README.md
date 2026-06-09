# L20/C09 — Compliance

## Topics

- **T01 SOC 2** — Service org controls
- **T02 ISO 27001** — International standard
- **T03 PCI DSS** — Payment card security
- **T04 HIPAA, GDPR, FedRAMP** — Specialty

## Why Compliance Matters

- Required for many B2B sales
- Regulatory requirement (PCI for cards, HIPAA for health, GDPR for EU)
- Customer demand
- Insurance discounts
- Investor / partner requirement

Not the same as security; complementary.

## SOC 2 (Service Organization Control 2)

For service organizations handling customer data. AICPA-defined.

### Trust Service Criteria
- **Security** (mandatory)
- **Availability** (optional)
- **Processing Integrity** (optional)
- **Confidentiality** (optional)
- **Privacy** (optional)

### Type 1 vs Type 2
- **Type 1**: snapshot of controls at a point in time
- **Type 2**: controls operated effectively over a period (usually 12 months)

Customers expect Type 2.

### Common Controls
- Access reviews (quarterly)
- Change management (code review, CI gates)
- Vulnerability management (scanning, patching)
- Incident response process
- Backup + DR
- Audit logs
- Encryption at rest + transit
- Vendor management

### Evidence
Auditor sampling: "show me 25 random PRs from Q3 with reviewer approval, with linked Jira ticket, with status check passed."

Automated evidence collection (Drata, Vanta, Secureframe, Sprinto) reduces audit pain.

## ISO 27001

International, broader than SOC 2.

### Information Security Management System (ISMS)
- Risk assessment
- Risk treatment plan
- Statement of Applicability
- Continuous improvement

### Annex A Controls (114 in 2022 version)
Including:
- Information security policies
- Organization of information security
- HR security
- Asset management
- Access control
- Cryptography
- Physical security
- Operations security
- Communications security
- System acquisition, development, maintenance
- Supplier relationships
- Incident management
- Business continuity
- Compliance

### Why ISO
- More respected in EU and globally
- More prescriptive than SOC 2 (different framing)
- Some customers require ISO over SOC 2

## PCI DSS

For anyone handling cardholder data. Required by card brands.

### Levels
- Level 1: >6M transactions/year → annual on-site audit
- Level 2-4: lighter requirements

### 12 Requirements
1. Firewall + segmentation
2. No vendor defaults
3. Protect stored cardholder data
4. Encrypt transmission
5. Anti-malware
6. Secure development
7. Restrict access by need
8. Identify + authenticate
9. Restrict physical access
10. Log + monitor
11. Test security
12. Information security policy

### Scope Reduction
PCI scope is anything that touches cardholder data. Reduce by:
- Tokenization (replace card number with token)
- Use payment processor's iframe (cardholder data never touches your servers)
- Network segmentation (limit PCI environment to small subset)

Smaller scope = simpler audit.

## HIPAA (US Healthcare)

Protects PHI (Protected Health Information).

### Key Rules
- **Privacy Rule** — limit PHI use/disclosure
- **Security Rule** — administrative, physical, technical safeguards
- **Breach Notification Rule** — notify affected within 60 days

### Business Associate Agreement (BAA)
- Required between covered entity and any vendor handling PHI
- AWS, GCP, Azure offer BAAs (for HIPAA-eligible services)
- Use only HIPAA-eligible services (subset of full catalog)

### Tech Safeguards
- Encryption (at rest, transit)
- Access controls
- Audit logs
- Integrity controls

## GDPR (EU Privacy)

For any data processing affecting EU residents.

### Key Rights
- Right to access
- Right to rectification
- Right to deletion ("right to be forgotten")
- Right to data portability
- Right to object

### Implications
- Data inventory (where is each piece of PII?)
- Deletion mechanism (delete user's data when requested)
- Data residency (some data must stay in EU)
- Consent for marketing
- 72-hour breach notification

### Sub-Processor Management
- Document every vendor that processes EU data
- Make available to customers
- DPA (Data Processing Agreement) with each

## FedRAMP

US federal cloud authorization.

### Levels
- **Low**: low impact systems
- **Moderate**: most workloads
- **High**: sensitive

### Authorization Paths
- **Agency ATO** — single agency authorizes
- **JAB P-ATO** — Joint Authorization Board (faster reuse)

Cost: $1M-$5M+, 1-2 years effort. Reserved for products targeting federal government.

## Compliance Automation

### Tools
- **Vanta**, **Drata**, **Secureframe**, **Sprinto** — automated evidence collection for SOC 2 / ISO / HIPAA
- **Tugboat Logic** (OneTrust)

### How They Help
- Connect to cloud accounts, GitHub, identity providers, Jira, etc.
- Auto-collect evidence
- Track control status
- Auditor portal

### Limitations
- Don't replace security
- "Auto-passed" controls still need real implementation
- Audit prep faster, audit not eliminated

## Compliance as Code

Express controls as code:
- AWS Config rules / Azure Policy / GCP Org Policy
- OPA Gatekeeper / Kyverno (K8s)
- Sentinel / Checkov (IaC)

Continuous evaluation; failed controls auto-detected.

## Cost vs Benefit

- SOC 2 Type 2: $20K-$100K/year all-in (audit + tooling + people)
- ISO 27001: similar
- PCI DSS Level 1: $50K-$200K+/year
- HIPAA: depends; mainly process + tech costs
- FedRAMP: $1M+
- GDPR: ongoing program cost

Required for many revenue paths. Don't fight compliance; engineer for it.

## Interview Themes

- "SOC 2 — what is it, why?"
- "PCI scope reduction strategies"
- "GDPR right to deletion — implementation"
- "Compliance as code — concretely"
- "Compliance vs security — same?"
