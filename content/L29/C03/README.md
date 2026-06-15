# L29/C03 — System Design for SRE/DevOps

## Topics

- **T01 The 35-Minute Framework** — Clarify (5) → Estimate (5) → High-level (5) → Deep dive (15) → Reliability/scale (5)
- **T02 Drive the Discussion** — Interviewer evaluates *signal*. Silence = uncertainty. Always be communicating.
- **T03 Numbers You Must Know** — Latency table, throughput ranges, storage costs.
- **T04 Common Patterns at Each Level** — L5: one service end-to-end. L6: multi-system platform. L7: org-level architecture.

## The 35-Minute Framework (Detailed)

### Min 0-5: Clarify
- "What's the scope? Who are the users? What's the scale?"
- "Are these requirements? (functional)"
- "What about (non-functional): latency, availability, durability, cost?"
- "Any constraints: regions, compliance, team size?"
- "What are NOT requirements?" — explicitly exclude scope

### Min 5-10: Estimate
- DAU → QPS (peak ~ 2-3× average)
- Data growth per day, per year
- Read:write ratio
- Bandwidth implications

### Min 10-15: High-Level Sketch
Four boxes:
```
[Clients] → [App/API] → [Data] → [Infra/Pipeline]
              │
              ▼ (observability)
         [Metrics/Logs/Traces]
```

### Min 15-30: Deep Dive (Pick 2-3)
- Pick the riskiest components
- Discuss alternatives, name the chosen approach
- Be explicit about tradeoffs
- Sketch APIs, data models, sharding strategy

### Min 30-35: Reliability + Scale
- Failure scenarios
- Monitoring + alerting
- Capacity expansion plan
- Multi-region if needed

## Driving the Discussion

> "Should I dive deeper into the storage layer or the messaging layer?"

This kind of question demonstrates engineering judgment. The interviewer wants to see you make calls, not wait for instructions.

## Capacity Estimation Cheat Sheet

```
1 GB ≈ 10^9 bytes
1 TB ≈ 10^12 bytes
1 PB ≈ 10^15 bytes

86,400 seconds/day
2.6M seconds/month
31.5M seconds/year

Daily 10M events × 1KB = 10 GB/day = 3.65 TB/year
Peak QPS for 10M DAU @ 5 actions/user: 580 avg, 1740 peak
```

## Common System Design Prompts for SRE/DevOps

- Design a CI/CD platform for 1000 engineers
- Design a metrics pipeline (Prometheus-scale)
- Design a logging pipeline (Splunk-scale)
- Design a tracing system (Jaeger-scale)
- Design an internal developer platform
- Design Cloudflare's edge
- Design Vault's secret backend
- Design a service mesh
- Design Netflix's deployment system
- Design a global load balancer
- Design a chaos engineering platform
- Design a feature flag service (LaunchDarkly)
- Design a rate limiter (distributed)
- Design a config management system (etcd-like)

## Patterns by Level

| Level | Pattern |
|---|---|
| L5 | Microservice with cache + DB; multi-AZ; basic observability |
| L6 | Multi-component platform; multi-region; clear ownership boundaries |
| L7 | Org-level; multi-tenant; governance; cost & policy at scale |

## Recommended Reading

- *Designing Data-Intensive Applications* (mandatory)
- *System Design Interview* — Alex Xu Vol 1 & 2
- "System Design Primer" GitHub
- *Software Engineering at Google*

## Interview Tips

- Ask before assuming
- Write capacity numbers on the board
- Name the components explicitly
- Recognize when an answer is "good enough" and move on
- Explicitly name tradeoffs (CAP, latency vs cost, etc.)
- End by summarizing the design
