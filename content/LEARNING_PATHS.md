# Learning Paths

Curated routes through the 30 lectures by **role** and **seniority**. The course is linear by design, but few people need all of it in order. Pick the path that matches where you are and where you're going.

> Notation: **L08** = lecture directory `L08/`. Open its `README.md` for the chapter map.

---

## How to Choose a Path

| You are… | Start with | Path |
|---|---|---|
| New to DevOps entirely | [Foundations](#path-1--complete-beginner) | Path 1 |
| A software engineer moving into infra | [SWE → DevOps](#path-2--software-engineer--devopssre) | Path 2 |
| A sysadmin modernizing to cloud-native | [Sysadmin → Cloud-Native](#path-3--sysadmin--cloud-native) | Path 3 |
| Targeting an SRE role | [SRE track](#path-4--sresite-reliability) | Path 4 |
| Targeting a Platform Engineer role | [Platform track](#path-5--platform-engineer) | Path 5 |
| Cloud/AWS specialist | [Cloud track](#path-6--cloud-specialist-aws-first) | Path 6 |
| Interviewing at FAANGM in <8 weeks | [Interview crunch](#path-7--faangm-interview-crunch) | Path 7 |

---

## Path 1 — Complete Beginner

**Goal**: zero to job-ready DevOps engineer. **Budget**: 6–12 months @ 10–15 hrs/week. Go in order; do every lab.

```
L01 → L02 → L03 → L04 → L05 → L06   (foundations: mindset, Linux, networking, bash, git, programming)
L07 → L08 → L10 → L12 → L13         (cloud, AWS, IaC, Docker, Kubernetes)
L15 → L16 → L17 → L19               (CI/CD, observability, SRE)
L20 → L21 → L23                     (security, databases, caching)
L30                                 (capstone — build the portfolio)
```

Skip on the first pass (return later): L09, L11, L14, L18, L22, L24, L25–L28.

---

## Path 2 — Software Engineer → DevOps/SRE

**Goal**: leverage existing coding skill; fill the systems gaps. **Budget**: 3–5 months.

You can move fast through programming and git; slow down on the OS/networking/operations layers you've never had to own.

| Phase | Lectures | Notes |
|---|---|---|
| Skim | L04, L05, L06 | You know git and a language; learn the ops idioms |
| **Deep** | **L02, L03** | The kernel/networking foundations most SWEs lack |
| Core | L07, L08, L10, L12, L13 | Cloud + containers + Kubernetes |
| **Deep** | **L17, L19, L28** | Observability, SRE discipline, system design |
| Round out | L20, L21, L22, L23 | Security and data systems |

---

## Path 3 — Sysadmin → Cloud-Native

**Goal**: translate strong Linux/ops instincts into cloud-native fluency. **Budget**: 3–5 months.

You already own L02 and much of L03/L04. Your gaps are cloud, IaC, containers, and the "everything as code" workflow.

```
Validate: L02, L03, L04, L11        (confirm depth; L11 maps your config-mgmt experience forward)
Learn:    L07 → L08 → L10           (cloud mental model, AWS, Terraform)
Learn:    L12 → L13 → L14           (containers → Kubernetes → mesh)
Learn:    L15 → L16 → L17 → L19     (modern delivery + reliability)
Modernize: L20, L26, L27           (DevSecOps, FinOps, DR/HA the cloud way)
```

---

## Path 4 — SRE/Site-Reliability

**Goal**: the discipline that defines senior+ reliability roles.

| Priority | Lectures |
|---|---|
| **Core identity** | L19 (SRE), L17 (Observability), L18 (Logging & Tracing) |
| **Failure & scale** | L25 (Chaos), L27 (DR/HA/Multi-Region), L24 (Production Networking) |
| **Substrate** | L02 (Linux internals), L03 (Networking), L13 (Kubernetes) |
| **Data risk** | L21 (Databases), L22 (Queues), L23 (Caching) |
| **Leveling** | L28 (System Design), L29 (Interviews) |

Read Google's *SRE Book* and *SRE Workbook* alongside L19.

---

## Path 5 — Platform Engineer

**Goal**: build the paved road other teams ship on.

```
L13 (Kubernetes)  →  L14 (Service Mesh)   →  L10 (IaC)
L15/L16 (CI/CD + GitOps)  →  L17 (Observability)  →  L20 (DevSecOps)
L28 (System Design — esp. the IDP / platform chapters)
L30 (Capstone: build an internal developer platform)
```

Pay special attention to L28's platform/IDP and tradeoff chapters (build-vs-buy, centralized-vs-federated, tool sprawl) — that's the daily judgment of the role.

---

## Path 6 — Cloud Specialist (AWS-first)

**Goal**: deep, interview-grade cloud mastery.

| Phase | Lectures |
|---|---|
| Mental model | L07 (cloud fundamentals) |
| **Deep AWS** | **L08** (the largest lecture — 73 topics) |
| Multi-cloud | L09 (Azure & GCP comparative) |
| Automate it | L10 (Terraform/IaC), L11 (config mgmt) |
| Operate it | L17, L19, L24, L27 |
| Optimize it | L26 (FinOps) |

---

## Path 7 — FAANGM Interview Crunch

**Goal**: maximum signal in minimum time. **Budget**: 4–8 weeks. See [INTERVIEW_PREP.md](INTERVIEW_PREP.md) for the full strategy.

```
Week 1: L13 (K8s internals) + L17 (Observability) + L19 (SRE)
Week 2: L28 (System Design — one problem per day)
Week 3: L29 (Coding + Behavioral + company-specific) 
Week 4: Mock interviews + L30 capstone walkthrough
```

If you have 8 weeks, prepend a week on L02/L03 (Linux + networking fundamentals get probed in phone screens) and a week on L20/L21 (security + databases).

---

## Seniority Lens

The same lectures read differently by level. Use the graded **Interview Prep** section at the bottom of every topic file:

| Level | What to optimize for |
|---|---|
| **Junior** | Breadth + correct vocabulary. Can you name and explain the thing? |
| **Mid** | Hands-on fluency. Can you operate it and debug the common failures? |
| **Senior** | Trade-offs + failure modes. Why this over the alternative, and how does it break? |
| **Staff** | Org-level judgment. Build-vs-buy, blast radius, influence without authority, multi-year bets. |

---

## See Also

- [README.md](README.md) — Course overview and the 30-lecture map
- [COURSE_OUTLINE.md](COURSE_OUTLINE.md) — Master index of every chapter and topic
- [INTERVIEW_PREP.md](INTERVIEW_PREP.md) — FAANGM-specific interview guidance
