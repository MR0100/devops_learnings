# L20 — Security & DevSecOps

## Overview

Security is everyone's job now. This lecture covers shift-left security, supply-chain integrity, secrets, zero trust, and compliance — the dimensions that staff engineers must own at FAANGM.

**9 chapters, 35 topics.**

## Chapter Map

### [C01](C01/) — Security Mindset
- T01 Threat Modeling (STRIDE, PASTA)
- T02 Defense in Depth
- T03 Least Privilege

### [C02](C02/) — Shift Left Security
- T01 IDE Security Plugins
- T02 Pre-Commit Hooks
- T03 Developer Security Training

### [C03](C03/) — Application Security Testing
- T01 SAST (SonarQube, Semgrep, CodeQL)
- T02 DAST (OWASP ZAP, Burp)
- T03 IAST & RASP
- T04 Software Composition Analysis (SCA)

### [C04](C04/) — Container & Image Security
- T01 Image Scanning Pipelines
- T02 Image Signing (Cosign / Sigstore)
- T03 SBOM (CycloneDX, SPDX)
- T04 Admission Controllers

### [C05](C05/) — Secrets Management
- T01 HashiCorp Vault Deep Dive
- T02 AWS Secrets Manager, Parameter Store
- T03 Sealed Secrets, External Secrets Operator
- T04 SOPS

### [C06](C06/) — Supply Chain Security
- T01 SLSA Framework
- T02 in-toto Attestations
- T03 Dependency Pinning & Reproducible Builds
- T04 Lessons from SolarWinds, Codecov, xz Utils

### [C07](C07/) — Cloud Security Posture
- T01 CSPM Tools (Wiz, Lacework, Prisma)
- T02 IaC Scanning (Checkov, tfsec)
- T03 CIEM (Identity Posture)

### [C08](C08/) — Zero Trust
- T01 BeyondCorp Model
- T02 Service-to-Service Identity (SPIFFE/SPIRE)
- T03 mTLS Everywhere

### [C09](C09/) — Compliance
- T01 SOC 2
- T02 ISO 27001
- T03 PCI DSS
- T04 HIPAA, GDPR, FedRAMP

## Threat Modeling: STRIDE

- **S**poofing — identity
- **T**ampering — data integrity
- **R**epudiation — accountability
- **I**nformation disclosure
- **D**enial of service
- **E**levation of privilege

For each component in your design, ask which STRIDE risks apply, then add mitigations.

## SLSA Levels (Supply-Chain Levels for Software Artifacts)

| Level | Requirements |
|---|---|
| 1 | Build process scripted, provenance generated |
| 2 | Hosted build service, signed provenance |
| 3 | Hardened build platform, non-falsifiable provenance |
| 4 | Two-party review, hermetic builds |

Most companies aim for SLSA 2–3.

## Secrets Management Decision

| Need | Pick |
|---|---|
| K8s-only, easy | Sealed Secrets |
| K8s + cloud-native pull | External Secrets Operator + cloud secret manager |
| Multi-cloud, dynamic creds | HashiCorp Vault |
| Just commit them encrypted | SOPS + KMS |

## Zero Trust Core Tenets

1. Verify explicitly (every request)
2. Least privilege access
3. Assume breach (design for the worst)

Implementation:
- Workload identity (SPIFFE/SPIRE, IRSA, Workload Identity)
- mTLS service-to-service (often via mesh)
- Per-request authn/authz, not perimeter-only
- Continuous evaluation (not session-based trust)

## Real Supply Chain Incidents (Lessons)

- **SolarWinds (2020)** — build system compromise; pushed signed updates
- **Codecov (2021)** — bash uploader compromise; credentials exfiltrated
- **Log4Shell (2021)** — log4j RCE; everyone scrambled
- **xz Utils (2024)** — multi-year social engineering of a maintainer

Lessons: pin everything, sign everything, verify everything, monitor build infrastructure.

## Recommended Reading

- *Building Secure & Reliable Systems* — Google (FREE online)
- *DevSecOps* — Sonatype, various authors
- OWASP Top 10
- SLSA framework spec

## Interview Themes

- "How do you secure a CI/CD pipeline?"
- "Supply chain attacks — what defenses?"
- "Zero trust — what does it mean concretely?"
- "Vault vs cloud secrets managers"
- "Run me through threat modeling for a service"

## Next

→ [L21 — Databases & Data Management for DevOps](../L21/README.md)
