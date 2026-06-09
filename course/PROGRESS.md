# Course Progress Tracker

**Last Updated**: 2026-06-09 (end of session)
**Total Topic Files**: 297
**Total Markdown Files**: 567 (includes READMEs)
**Course Completion**: ~50%

## How to Resume

When starting next session, tell Claude:
> "Continue building the DevOps course from PROGRESS.md. Pick up at [next topic]."

Or simply:
> "Continue from where we left off (see PROGRESS.md)."

Claude should read this file first, identify the next topic to write, and continue with the same pattern.

## Established Topic File Pattern

Each topic file follows this structure (~150-250 lines):
1. `# LXX/CYY/TZZ — Title`
2. `## Learning Objectives` (2-4 bullets)
3. Deep technical content with:
   - Code examples (YAML, bash, Python, Go, etc.)
   - Diagrams (ASCII)
   - Tables for comparisons
   - Real-world scenarios
4. `## Common Mistakes`
5. `## Best Practices`
6. `## Quick Refs` (commands cheatsheet)
7. `## Interview Prep` (graded Junior/Mid/Senior/Staff)
8. `## Next Topic` (link to next file)

## Completed Lectures (Topics Created)

### Fully Complete (8 lectures)
| Lecture | Topics | Status |
|---|---|---|
| L01 Introduction to DevOps | 28 | ✓ |
| L02 Linux Foundations | 14 | ✓ |
| L03 Networking | 38 | ✓ |
| L04 Bash Scripting | 22 | ✓ |
| L05 Git Mastery | 29 | ✓ |
| L06 Programming for DevOps (Bash/Python/Go) | 24 | ✓ |
| L07 Cloud Foundations | 29 | ✓ |
| L08 AWS Deep Dive (all 14 chapters) | 73 | ✓ |

### Partially Complete (2 lectures)

#### L10 Terraform / IaC (14 of ~33 topics)
- ✓ C01 (T01-T03): IaC Fundamentals
- ✓ C02 (T01-T04): Terraform Fundamentals
- ✓ C03 (T01-T05): Terraform State
- ✓ C04 (T01-T02): Modules (anatomy, versioning)
- ⏳ **NEXT**: C04/T03 Composition Patterns
- ⏳ C04/T04 Module Testing
- ⏳ C05 Terraform at Scale (T01-T04)
- ⏳ C06 Writing Custom Providers (T01-T02)
- ⏳ C07 Pulumi & CDK (T01-T03)
- ⏳ C08 Best Practices
- ⏳ C09 (whatever is left)

#### L13 Kubernetes (26 of ~86 topics)
- ✓ C01 (T01-T05): Architecture (Control Plane, Data Plane, Pod Lifecycle, Scheduler, etcd)
- ✓ C02 (T01-T05): Core Workloads (Pods, Deployments, StatefulSets, DaemonSets, Jobs/CronJobs)
- ✓ C03 (T01-T04): Configuration (ConfigMaps, Secrets, Downward API, Env vs Files)
- ✓ C04 (T01-T07): Networking (Model, CNI, kube-proxy, Services, Ingress, Gateway API, NetworkPolicies)
- ✓ C05 (T01-T05): Storage (PV/PVC, StorageClasses, CSI, Stateful, Snapshots)
- ⏳ **NEXT**: C06 Security (T01-T07): RBAC, ServiceAccounts, Pod Security Standards, NetworkPolicy (security focus), Secrets Encryption, OPA Gatekeeper/Kyverno, Image Policy
- ⏳ C07 Scheduling & Resources (T01-T07): Requests/Limits, QoS, Affinity, Taints, Topology Spread, Priority, Custom Schedulers
- ⏳ C08 Autoscaling (T01-T05): HPA, VPA, Cluster Autoscaler, Karpenter, KEDA
- ⏳ C09-C20: Operators, CRDs, Multi-Cluster, Helm, Observability, GitOps with Argo, Networking Advanced, Cost, Production Patterns, Troubleshooting, Performance, Security Posture, Compliance, Disaster Recovery

### Not Started (20 lectures)

#### L09 Azure & GCP — 0 of ~30 topics
Per L09/README.md, structure exists. Topics cover:
- C01 Azure Fundamentals (Subscriptions, Resource Groups, ARM)
- C02 Azure Compute (VMs, AKS, Functions)
- C03 Azure Storage / DB
- C04 Azure Networking
- C05 GCP Fundamentals (Projects, IAM)
- C06 GCP Compute (GCE, GKE, Cloud Run)
- C07 GCP Storage / BigQuery
- C08 GCP Networking
- C09 Multi-Cloud Patterns

#### L11 Configuration Management — 0 of ~20 topics
- C01 Ansible Fundamentals
- C02 Ansible Advanced (Roles, Vault, AWX)
- C03 Chef / Puppet (overview for legacy)
- C04 Cloud-Init / User Data
- C05 Packer for Image Pipelines

#### L12 Docker Deep Dive — 0 of ~25 topics
- C01 Container Fundamentals (Namespaces, cgroups)
- C02 Image Layers / OCI Spec
- C03 Dockerfile Best Practices
- C04 Multi-Stage Builds, BuildKit
- C05 Registries (Docker Hub, ECR, GHCR)
- C06 Runtime (runc, containerd, CRI-O)
- C07 Security (Distroless, Scanning, Signing)

#### L14 Service Mesh — 0 of ~20 topics
- C01 Service Mesh Concepts
- C02 Istio Deep Dive
- C03 Linkerd
- C04 Cilium Service Mesh
- C05 Production Considerations (mTLS, Observability)

#### L15-L19 CI/CD, Observability, Logging, SRE — 0 of ~40 topics
- L15 CI/CD Deep (GitHub Actions, GitLab CI, Jenkins, ArgoCD, Spinnaker)
- L16 Observability (Prometheus, Grafana, OpenTelemetry, distributed tracing)
- L17 Logging at Scale (Loki, ELK, Fluentd, Vector)
- L18 SRE Practices (SLO/SLI/SLA, Error Budgets, Postmortems, Toil reduction)
- L19 Incident Management

#### L20-L24 Security, DB, Msg, Cache, Net Advanced — 0 of ~30 topics
- L20 DevSecOps / Supply Chain Security
- L21 Databases at Scale
- L22 Messaging & Streaming (Kafka, Pulsar)
- L23 Caching Strategies
- L24 Advanced Networking (BGP, Anycast, CDN)

#### L25-L30 Advanced/Capstone — 0 of ~45 topics
- L25 Chaos Engineering
- L26 FinOps & Cost Optimization
- L27 Disaster Recovery
- L28 System Design for DevOps Roles
- L29 Interview Preparation (questions, mock interviews)
- L30 Capstone Project

## Total Remaining Estimate

Roughly **~270 topic files remaining** across L09, L10 partial, L11, L12, L13 partial, L14-L30.

## Priority Recommendations (For FAANGM)

Given interview focus, prioritize in this order:

1. **L13 Kubernetes C06-C20** (highest FAANGM coverage) — ~60 topics
2. **L10 Terraform completion** (IaC mandatory) — ~20 topics
3. **L12 Docker Deep Dive** (containers fundamentals) — ~25 topics
4. **L14 Service Mesh** (Istio common interview topic) — ~20 topics
5. **L16 Observability** (Prometheus + OpenTelemetry) — ~15 topics
6. **L18 SRE Practices** (Google-style questions) — ~10 topics
7. **L28 System Design** (senior-level critical) — ~15 topics
8. **L29 Interview Prep** (specific Q&A) — ~10 topics
9. Then L09, L11, L15, L17, L19-L27 remaining

## Files I Should Read Tomorrow

Start by reading:
1. This file: `/Users/kgk/Desktop/projects/devops/course/PROGRESS.md`
2. Lecture README of where I'm continuing: `/Users/kgk/Desktop/projects/devops/course/LXX/README.md`
3. Chapter README: `/Users/kgk/Desktop/projects/devops/course/LXX/CYY/README.md`
4. Last completed topic in chapter to maintain style continuity

## Style Reference Files

Best examples of pattern to match:
- `/Users/kgk/Desktop/projects/devops/course/L13/C04/T07-NetworkPolicies.md`
- `/Users/kgk/Desktop/projects/devops/course/L08/C02/T05-IRSA.md`
- `/Users/kgk/Desktop/projects/devops/course/L13/C01/T05-etcd.md`

## Course Structure Summary

```
course/
├── COURSE_OUTLINE.md
├── README.md
├── PROGRESS.md  ← THIS FILE
├── L01/ to L30/
│   ├── README.md (chapter map)
│   └── C01/ to CNN/
│       ├── README.md (topic list)
│       └── T01-XXX.md, T02-YYY.md, ...
```

Every directory exists. Every chapter has a README with topic listings. Only individual topic files in the not-started lectures need creation.

## Tomorrow's First Tasks (Recommended)

Pick ONE of these to start:

**Option A — Continue Kubernetes (Most Impactful for FAANGM)**
Next file: `/Users/kgk/Desktop/projects/devops/course/L13/C06/T01-RBAC.md`
- Read `/Users/kgk/Desktop/projects/devops/course/L13/C06/README.md` first for chapter context
- Topics in C06: RBAC, ServiceAccounts, Pod Security Standards, NetworkPolicies (security), Secrets Encryption, OPA/Kyverno, Image Policy

**Option B — Finish Terraform**
Next file: `/Users/kgk/Desktop/projects/devops/course/L10/C04/T03-Composition.md`
- Then C04/T04, C05, C06, C07, C08, C09

**Option C — Start Docker Deep Dive**
Next file: `/Users/kgk/Desktop/projects/devops/course/L12/C01/T01-Container-Fundamentals.md`
- Read `/Users/kgk/Desktop/projects/devops/course/L12/README.md` first

## Notes for Tomorrow

- Keep topic files focused (~150-250 lines)
- Maintain consistent "Interview Prep" graded sections (Junior/Mid/Senior/Staff)
- Include "Next Topic" link at end pointing to actual next file
- Use existing READMEs to understand what each topic should cover
- After completing a chapter, move to next chapter README in lecture
- Update this PROGRESS.md at end of next session
