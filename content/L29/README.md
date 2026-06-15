# L29 — FAANGM Interview Mastery

## Overview

The whole point of this course. This lecture covers the FAANGM interview loop end-to-end: coding, system design, behavioral, company-specific prep, negotiation, and resume.

**8 chapters, 38 topics.**

## Learning Outcomes

- Crack a FAANGM senior+ DevOps interview loop
- Negotiate compensation effectively
- Avoid common rejection causes

## Chapter Map

### [C01](C01/) — The FAANGM Interview Process
- T01 Recruiter Screen
- T02 Tech Phone Screen
- T03 Onsite Loop (Coding, System Design, Behavioral)
- T04 Bar Raiser / Hiring Committee
- T05 Levels at Each Company (L5/L6/L7, IC5/IC6, etc.)

### [C02](C02/) — Coding for DevOps Roles
- T01 Yes, You Still Need DSA
- T02 Focus Areas (Strings, Trees, Graphs, BFS/DFS, Heaps)
- T03 Concurrency Problems
- T04 Systems Coding (Reverse a Linked List vs Build a Rate Limiter)
- T05 Worked Example: Top-K from Logs
- T06 Worked Example: Topological Sort for Dependency Ordering
- T07 Worked Example: Sliding-Window Rate Counting

### [C03](C03/) — System Design for SRE/DevOps
- T01 The 35-Minute Framework
- T02 Drive the Discussion
- T03 Numbers You Must Know (Latency Numbers)
- T04 Common Patterns at Each Level

### [C04](C04/) — Behavioral / Leadership Interviews
- T01 STAR Format
- T02 Amazon Leadership Principles (Deep Dive)
- T03 Google's Googleyness & Leadership
- T04 Meta's Pillars
- T05 Common Themes (Ambiguity, Conflict, Influence)
- T06 Crafting a "Career Story Bank"

### [C05](C05/) — Company-Specific Prep
- T01 Amazon (LP-Heavy, Frugality, Ownership)
- T02 Google (Googleyness, GCA, Domain)
- T03 Meta (Move Fast, Impact)
- T04 Microsoft (Growth Mindset)
- T05 Apple (Secretive, Hardware-Software)
- T06 Netflix (Keeper Test, Freedom & Responsibility)

### [C06](C06/) — Negotiation
- T01 Compensation Components (Base, Bonus, RSU, Sign-On, Refresher)
- T02 Level Negotiation
- T03 Competing Offers
- T04 levels.fyi & TeamBlind Realism

### [C07](C07/) — Mock Interviews
- T01 Where to Find Them
- T02 How to Self-Score

### [C08](C08/) — Resume & LinkedIn
- T01 Impact-Driven Bullets
- T02 ATS Optimization
- T03 Recruiter Outreach

## The Standard FAANGM Loop

```
1. Recruiter screen (30 min)
   - Background, interest, role fit
2. Tech phone screen (60 min)
   - 1-2 coding problems OR system design lite
3. Onsite (4-6 hours)
   - 1-2 coding rounds
   - 1-2 system design rounds
   - 1-2 behavioral rounds
   - 1 deep technical (domain)
4. Hiring committee / bar raiser
5. Offer + negotiation
```

## Coding Reality Check for DevOps Roles

You will be asked DSA. Common topics:
- Strings (parsing, log processing)
- Arrays / two pointer
- Trees (BST, traversal)
- Graphs (BFS, DFS, topological sort)
- Heaps (top-K, scheduling)
- Sliding window
- Hash maps
- Sometimes: design problems (rate limiter, cache, scheduler)

You don't need to be at competitive-programmer level for senior DevOps; but you do need to solve mediums comfortably and discuss optimization.

## System Design at Each Level

| Level | Expectation |
|---|---|
| L4 / Mid | One component well-designed (e.g., "design a cache") |
| L5 / Senior | Full small system (e.g., "design URL shortener with monitoring") |
| L6 / Staff | Complex system with multiple subsystems, real tradeoffs (e.g., "design a CI/CD platform") |
| L7 / Principal | Org-level architecture, cross-cutting concerns, governance |

## Behavioral Story Bank (Build This)

Aim for ~12 stories covering:
- Leadership (led a project / team)
- Conflict (with peer / leader)
- Ambiguity (no clear path)
- Failure (and learning)
- Cross-functional partnership
- Mentoring / hiring
- Disagree-and-commit
- Customer obsession
- Frugality / scrappiness
- Hard decision with data
- Long-term tech bet
- Inclusion / DEI work

Each story should fit in 4-5 minutes; use STAR.

## Amazon Leadership Principles (Top Themes)

The 16 LPs, but expect questions on:
1. Customer Obsession
2. Ownership
3. Invent and Simplify
4. Are Right, A Lot
5. Hire and Develop the Best
6. Insist on the Highest Standards
7. Think Big
8. Bias for Action
9. Frugality
10. Earn Trust
11. Dive Deep
12. Have Backbone; Disagree and Commit
13. Deliver Results

Two stories per LP minimum.

## Compensation Components

```
Total Comp = Base + Bonus + RSUs/4 (avg) + Sign-on/N
```

| Company | Senior/L5 (est) | Staff/L6 (est) |
|---|---|---|
| Google | $450K–$550K | $650K–$900K |
| Meta | $480K–$580K | $700K–$1M |
| Amazon | $400K–$520K | $580K–$800K |
| Apple | $400K–$520K | $600K–$850K |
| Netflix | $700K–$900K (flat structure) | $1M+ |
| Microsoft | $350K–$450K | $500K–$700K |

> Numbers are approximate ranges from public sources (levels.fyi). Use for negotiation reference, not as guarantees.

## Negotiation Principles

1. Never accept the first offer
2. Get the offer in writing
3. Use competing offers (real or implied)
4. Negotiate level if scope warrants
5. Negotiate components separately (base, RSU, sign-on)
6. Stay friendly; this is a long-term relationship
7. The recruiter wants to close — use that

## Resume Format That Works

```
BULLET = ACTION + IMPACT + SCALE

Bad: "Worked on Kubernetes infrastructure."
Good: "Led migration from EC2 to EKS for 50+ services serving 10M req/min,
       reducing infrastructure cost 40% and deploy time from 2h to 8min."
```

## Recommended Resources

- *Cracking the Coding Interview* — Gayle Laakmann McDowell
- *System Design Interview* — Alex Xu
- *Decode and Conquer* — Lewis C. Lin (for behavioral)
- LeetCode (focus mediums)
- Pramp / interviewing.io for mock interviews
- levels.fyi for compensation data
- TeamBlind for company culture intel

## Interview Themes Per Lecture

- L01 (Culture) — STAR stories on culture change
- L02 (Linux) — debug a slow process
- L03 (Networking) — trace a packet, design VPC
- L04-L05 (Shell, Git) — usually basic
- L06 (Programming) — algorithms + system code
- L07-L09 (Cloud) — design on a specific cloud
- L10 (IaC) — Terraform deep dive
- L12 (Containers) — what IS a container
- L13 (K8s) — heaviest tested area
- L17-L18 (Observability) — design metrics/logs pipeline
- L19 (SRE) — SLI/SLO design, postmortem
- L20 (Security) — threat model, supply chain
- L28 (System Design) — the main event

## Next

→ [L30 — Capstone Projects & Portfolio](../L30/README.md)
