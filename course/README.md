# The Complete DevOps Mastery Course

## From Beginner to Staff/Principal Engineer — FAANGM Interview Ready

This is a comprehensive, opinionated DevOps curriculum designed to take you from zero knowledge to a Staff/Principal-level engineer capable of cracking interviews at FAANGM companies (Facebook/Meta, Amazon, Apple, Netflix, Google, Microsoft) and other top-tier tech companies (Uber, Airbnb, Stripe, Datadog, Cloudflare, Databricks, etc.).

---

## Course Philosophy

> "You cannot operate what you don't understand. You cannot scale what you cannot measure. You cannot lead what you cannot teach."

Most DevOps courses teach tools. This course teaches:

1. **First principles** — Why systems behave the way they do (kernel, networking, distributed systems)
2. **Production realities** — How things actually break and how staff engineers respond
3. **Engineering judgment** — When to use what, what tradeoffs you're really making
4. **Interview-ready depth** — Every topic is taught to the depth a FAANGM bar-raiser will probe
5. **Leadership and influence** — How staff/principal engineers operate beyond code

---

## Target Audience

- **Software engineers** transitioning into DevOps/SRE/Platform Engineering
- **Junior/mid DevOps engineers** aiming for senior/staff roles at FAANGM
- **System administrators** modernizing to cloud-native skills
- **SREs** wanting deeper coverage of cloud, IaC, and platform engineering
- **Tech leads** building infrastructure-heavy products

---

## How This Course Is Structured

```
course/
├── L01-Introduction-to-DevOps/
│   ├── README.md                # Lecture overview, prerequisites, outcomes
│   ├── C01-Understanding-DevOps/
│   │   ├── README.md            # Chapter overview, topics list
│   │   ├── T01-What-is-DevOps.md
│   │   ├── T02-History-and-Evolution.md
│   │   └── ...
│   └── ...
├── L02-Linux-and-OS-Foundations/
└── ...
```

- **L = Lecture** (30 lectures total — large thematic units)
- **C = Chapter** (sub-areas within a lecture — typically 4–15 per lecture)
- **T = Topic** (granular learning units — typically 3–10 per chapter)

Every topic file contains:

1. Learning objectives
2. Prerequisites
3. Core concepts (deep)
4. How it works under the hood
5. Real-world examples
6. Production gotchas / failure modes
7. Hands-on labs
8. Interview questions (junior, mid, senior, staff)
9. Further reading

---

## The 30 Lectures

### Foundations (L01–L06)

| Lecture | Title | Why It Matters |
|---|---|---|
| L01 | Introduction to DevOps, SRE & Platform Engineering | Mental model for everything else |
| L02 | Linux & Operating System Internals | Foundation under every container, VM, and pod |
| L03 | Networking Deep Dive (OSI to BGP) | Networking is the #1 thing that breaks in production |
| L04 | Shell, Bash & Scripting for Automation | The lingua franca of operations |
| L05 | Version Control & Git Internals | Every change starts here |
| L06 | Programming for DevOps (Python & Go) | You will write tools, not just configure them |

### Cloud & Infrastructure (L07–L11)

| Lecture | Title | Why It Matters |
|---|---|---|
| L07 | Cloud Computing Fundamentals | Mental model that applies across all clouds |
| L08 | AWS Deep Dive (50+ services) | The dominant cloud — required for most FAANGM roles |
| L09 | Azure & GCP Comparative Mastery | Multi-cloud is the norm at scale |
| L10 | Infrastructure as Code (Terraform, Pulumi, CDK) | Infrastructure is software now |
| L11 | Configuration Management (Ansible, Chef, Puppet, Salt) | Day-2 ops and fleet management |

### Containers & Orchestration (L12–L14)

| Lecture | Title | Why It Matters |
|---|---|---|
| L12 | Docker & Container Internals | Namespaces, cgroups, OCI — first principles |
| L13 | Kubernetes — Beginner to Internals | The platform every FAANGM expects you to master |
| L14 | Service Mesh (Istio, Linkerd, Consul, Envoy) | The next layer above Kubernetes |

### Delivery & Reliability (L15–L19)

| Lecture | Title | Why It Matters |
|---|---|---|
| L15 | CI/CD Fundamentals & Pipeline Design | Where code becomes product |
| L16 | CI/CD Tools (Jenkins, GitHub Actions, GitLab, ArgoCD, Spinnaker, Tekton) | Pick the right tool, run it well |
| L17 | Monitoring & Observability (Prometheus, Grafana, OTel) | Cannot operate what you cannot see |
| L18 | Logging & Distributed Tracing (ELK, Loki, Jaeger, Tempo) | Debugging at scale |
| L19 | Site Reliability Engineering (SRE) | The discipline that defines senior+ roles |

### Security, Data & Networking (L20–L24)

| Lecture | Title | Why It Matters |
|---|---|---|
| L20 | Security & DevSecOps (Zero Trust, SLSA, Supply Chain) | Security is everyone's job now |
| L21 | Databases & Data Management for DevOps | DBs are the highest-risk part of any system |
| L22 | Message Queues & Event Streaming (Kafka, RabbitMQ, Pulsar) | Async is how scale works |
| L23 | Caching & CDN (Redis, Memcached, CloudFront, Fastly) | Latency is a feature |
| L24 | Production Networking (Load Balancers, API Gateway, Anycast, BGP) | Edge and ingress matter |

### Advanced Engineering (L25–L28)

| Lecture | Title | Why It Matters |
|---|---|---|
| L25 | Chaos Engineering & Resilience Testing | Break it on purpose before it breaks you |
| L26 | FinOps & Cloud Cost Optimization | Senior engineers are accountable for spend |
| L27 | Disaster Recovery, HA & Multi-Region Architecture | RTO/RPO are board-level metrics |
| L28 | System Design for DevOps & Platform Engineers | The interview question that decides level |

### Interview & Career (L29–L30)

| Lecture | Title | Why It Matters |
|---|---|---|
| L29 | FAANGM Interview Mastery (Coding, System Design, Behavioral) | The whole point of this course |
| L30 | Capstone Projects & Portfolio | Proof of skill that survives any interview |

---

## How to Use This Course

### If you're a beginner

Go in order. Each lecture builds on the last. Budget **6–12 months** at 10–15 hrs/week.

### If you're mid-level

Skim L01–L06, then do L07 onwards in order. Spend extra time on L13 (Kubernetes), L19 (SRE), L28 (System Design). **3–6 months** at 10 hrs/week.

### If you're senior preparing for FAANGM

Pick weak areas from L01–L24. Then spend **2–3 months** intensively on L25–L30 with mock interviews.

### If you only have 4 weeks before an interview

- Week 1: L13 (Kubernetes internals), L17 (Observability), L19 (SRE)
- Week 2: L28 (System Design — daily problems)
- Week 3: L29 (Behavioral + company-specific prep)
- Week 4: Mock interviews + L30 capstone walkthrough

---

## Hands-On Requirements

You will need:

- A laptop with at least 16 GB RAM (32 GB recommended for K8s labs)
- An AWS account (free tier + ~$30/month budget for labs)
- An Azure or GCP account (free tier)
- A GitHub account (for CI/CD and IaC labs)
- A Linux VM, WSL2, or macOS for local development
- Docker Desktop or Rancher Desktop
- A kubectl / kind / minikube setup
- A Terraform CLI installation

---

## Books & Resources Referenced Throughout

The course aligns with these canonical texts (read them in parallel):

1. **The Phoenix Project** — Gene Kim
2. **The DevOps Handbook** — Gene Kim, Jez Humble, Patrick Debois, John Willis
3. **Site Reliability Engineering** — Google (free online)
4. **The SRE Workbook** — Google (free online)
5. **Designing Data-Intensive Applications** — Martin Kleppmann
6. **Kubernetes in Action** — Marko Lukša
7. **Kubernetes: Up & Running** — Brendan Burns, Kelsey Hightower, et al.
8. **Terraform: Up & Running** — Yevgeniy Brikman
9. **Cloud Native Patterns** — Cornelia Davis
10. **Accelerate** — Nicole Forsgren, Jez Humble, Gene Kim

---

## See Also

- [COURSE_OUTLINE.md](COURSE_OUTLINE.md) — Master index with every chapter and topic
- [LEARNING_PATHS.md](LEARNING_PATHS.md) — Curated paths by role and seniority (coming soon)
- [INTERVIEW_PREP.md](INTERVIEW_PREP.md) — FAANGM-specific interview guidance (coming soon)
