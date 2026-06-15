# L13/C20/T04 — Compliance Posture

## Learning Objectives

- Map K8s controls to compliance
- Build compliance program

## Compliance Frameworks

| Framework | Scope |
|---|---|
| SOC 2 | Service org operational controls |
| ISO 27001 | Information security |
| PCI DSS | Payment card data |
| HIPAA | Healthcare |
| FedRAMP | US federal |
| GDPR | EU privacy |
| CIS Benchmark | Security best practices |

## K8s Controls Map

For SOC 2 / ISO 27001:

### Access Control
- IRSA / Workload Identity (no static creds)
- RBAC scoped
- MFA on cluster access
- SSO via OIDC

Evidence: audit logs.

### Encryption
- etcd at rest (KMS)
- TLS in transit (mesh + Ingress)
- Customer-managed keys for sensitive

Evidence: encryption config + KMS audit.

### Logging
- CloudTrail
- API server audit log
- Application logs
- Retention per requirement

Evidence: logs in SIEM.

### Monitoring
- Metrics, traces
- Alerting on security events
- Incident response

Evidence: dashboards + runbooks.

### Change Management
- GitOps (Git as record)
- PR reviews
- Approval workflows
- Audit trail

Evidence: Git history.

### Vulnerability Management
- Image scanning (Trivy / Snyk)
- Cluster scanning (kube-bench)
- Runtime (Falco)
- Patch cadence

Evidence: scan reports.

### Backup + DR
- etcd snapshots
- Velero
- Cross-region
- Tested annually

Evidence: backup logs + test reports.

## Audit Logging

API server audit:
```yaml
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods/exec", "pods/portforward"]
  - group: "rbac.authorization.k8s.io"
- level: Request
  verbs: ["delete", "patch"]
```

Ship to SIEM. Retain per compliance.

## Policy Engines

Enforce compliance:
- OPA Gatekeeper
- Kyverno

Examples:
- No privileged containers
- Required labels (team, owner)
- Image registry allowlist
- Resource limits required

For: SOC 2 control automation.

## Documentation

For audits:
- Architecture diagrams
- Control statements
- Procedures (runbooks)
- Test results
- Incident records

Audit-ready evidence.

## Continuous Compliance

Tools:
- AWS Audit Manager
- Vanta, Drata (compliance automation)
- Custom dashboards

For: ongoing posture vs annual audit.

## Audit Trail

For any change:
- Who: identity
- What: changed resource
- When: timestamp
- Why: PR description / ticket

K8s audit log + Git provides.

## NetworkPolicy Compliance

Default deny + explicit allows. Documented.

For: zero-trust per PCI / HIPAA.

## Encryption Compliance

For HIPAA / PCI:
- All PII / PHI / cardholder data encrypted
- At rest + in transit
- Key management

KMS + Secrets Manager + mTLS (mesh) covers.

## Data Residency

For GDPR / similar:
- Data stays in region
- Backups in region
- Restrict transfers

For: cluster per region; data stays.

## Multi-Tenancy

For SaaS:
- Per-tenant namespace
- ResourceQuota
- NetworkPolicy isolation
- Audit per tenant

For: data isolation compliance.

## Compliance as Code

- IaC for infrastructure (Terraform)
- GitOps for K8s (ArgoCD)
- Policies as Code (Kyverno)
- Tests for controls (kube-bench)

For: reproducible, auditable.

## Evidence Collection

Automate:
- Daily compliance reports
- Per-rule pass/fail
- Trend over time

For audit: hand auditor.

## Penetration Testing

Annually:
- External pentest
- kube-hunter scan
- Findings tracked

For: real-world security.

## Incident Response

Documented:
- Who responds
- Severity levels
- Communication
- Postmortem
- Continuous improvement

For SOC 2: required.

## Vendor Management

K8s vendors used:
- Cloud provider (EKS / GKE / AKS)
- Third-party charts
- Operators

Vendor risk assessment + SLAs.

## Change Management

For K8s:
- All changes via Git PR
- Reviewed
- Tested in non-prod
- Approved
- Applied via ArgoCD
- Auditable

For: change control compliance.

## Specific Frameworks

### PCI DSS
- Cardholder data encrypted
- Network segmentation (NetworkPolicy)
- Access logging
- Vulnerability scanning
- Annual audit

### HIPAA
- PHI encrypted (transit + rest)
- Access controls
- Audit logs
- BAA with cloud
- DR plan

### SOC 2 Type II
- Operational over time
- Controls tested over 6-12 months
- Evidence collected continuously

### FedRAMP
- US federal
- Strict controls
- AWS GovCloud / Azure Gov
- Long certification process

## Compliance Calendar

- Daily: monitor controls
- Weekly: review findings
- Monthly: dashboard
- Quarterly: internal audit
- Annually: external audit / cert renewal

## Best Practices

- Compliance as Code
- Automate evidence
- Per-framework mapping documented
- Continuous improvement
- Cross-functional team
- Pre-audit prep

## Common Mistakes

- Manual evidence (slow + error-prone)
- One-time setup; no maintenance
- Single person owning compliance
- Treating audit as event vs ongoing
- Compliance theater (looks good; not real)

## Real Compliance Posture

Beyond checkboxes:
- Actual security improvements
- Embedded in workflow
- Engineering owns
- Continuous

## Quick Refs

```bash
# kube-bench
docker run --rm aquasec/kube-bench:latest run

# Policy reports
kubectl get policyreport -A

# Audit logs
aws s3 ls s3://my-cluster-audit-logs/

# Access analyzer
aws accessanalyzer list-findings
```

## Production Readiness Checklist

For tier-0 K8s:

### Security
- ☐ PSS restricted
- ☐ NetworkPolicy default deny
- ☐ etcd encryption at rest
- ☐ API server audit logging
- ☐ IRSA / Workload Identity
- ☐ Image signing + verification
- ☐ Runtime detection (Falco)
- ☐ Secrets externalized

### Reliability
- ☐ Multi-AZ
- ☐ HA control plane
- ☐ Backup (etcd + Velero)
- ☐ Tested restore
- ☐ Monitoring + alerting
- ☐ Documented runbooks
- ☐ HPA configured
- ☐ PDBs on critical

### Observability
- ☐ Prometheus + Grafana
- ☐ Logs centralized (Loki/ELK)
- ☐ Traces (X-Ray/Jaeger/Tempo)
- ☐ Dashboards
- ☐ Alerts SLI-based

### Cost
- ☐ Kubecost installed
- ☐ Karpenter / Cluster Autoscaler
- ☐ Spot for tolerant
- ☐ Reserved for baseline
- ☐ Right-sized
- ☐ Cost dashboards

### Compliance
- ☐ Audit logging
- ☐ Change management (GitOps)
- ☐ Documented controls
- ☐ Evidence collected
- ☐ Pen test annual

### Operations
- ☐ Upgrade procedure documented
- ☐ Test environments
- ☐ Capacity planning
- ☐ DR drills
- ☐ Incident response

## Interview Prep

**Mid**: "K8s compliance."

**Senior**: "Map SOC 2 to K8s."

**Staff**: "Compliance program for SaaS platform."

## Next Lecture

L13 Kubernetes (86 topics) COMPLETE.

→ Move to [L14 — Service Mesh](../../L14/README.md)
