# L01/C04/T04 — Cloud Engineer / Infrastructure Engineer

## Learning Objectives

- Identify cloud engineer scope and how it differs from DevOps and SRE
- Map your skills to cloud-engineer-specific career paths
- Choose specialization tracks (networking, security, data infra, FinOps)

## Typical Day-to-Day

- Designing cloud architectures (multi-AZ, multi-region)
- Setting up VPC, subnetting, routing, peering
- Implementing IAM, encryption, KMS
- Cost analysis and rightsizing
- Building landing zones and account structures
- Migrating workloads from on-prem to cloud or cross-cloud

## Where Cloud Engineering Sits

```
   Software Engineer ──► Infrastructure Engineer ──► Cloud Engineer
                              │
                              ├──► DevOps Engineer (more dev tooling)
                              ├──► SRE (more reliability)
                              └──► Platform Engineer (more product)
```

## Common Specializations

- **Cloud Networking**: VPC at scale, Transit Gateway hubs, BGP/DX
- **Cloud Security**: IAM, KMS, posture management (CSPM/CIEM)
- **Cloud Data Infrastructure**: RDS/Aurora/Spanner/BigQuery operations
- **FinOps Engineer**: cloud cost optimization at scale
- **Cloud Migration Specialist**: lift-and-shift, replatforming, refactoring

## Skill Profile

- One cloud at expert depth (AWS most common); broad on the other two
- IaC (Terraform / Pulumi / native templates)
- Deep networking and security
- Strong cost awareness
- Comfortable with compliance frameworks

## Certification Reality

- Useful as a baseline at junior/mid levels
- Diminishing returns at senior+; experience and depth matter more
- Notable ones (if doing them): AWS Solutions Architect Pro, GCP Professional Cloud Architect, Azure Solutions Architect Expert
- Skip "DevOps Engineer" certs unless your employer reimburses

## Interview Prep

**Mid**: "Design a 2-tier web app on AWS."

**Senior**: "How would you design a multi-account AWS organization for a 500-engineer company?"

**Staff**: "Walk through a migration of a stateful on-prem monolith to AWS, considering network, security, data, and cost."

## Next Topic

→ [T05 — Career Progression: IC1 → Staff → Principal → Distinguished](T05-Career-Progression.md)
