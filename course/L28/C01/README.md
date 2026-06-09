# L28/C01 — System Design Framework

## Topics

- **T01 Functional vs Non-Functional Requirements** — Two sides
- **T02 Capacity Estimation Math** — Numbers matter
- **T03 The 4 Boxes (Client, App, Data, Infra)** — Anchor model

## The 35-Minute Interview Framework

```
Min 0-5    Clarify requirements & scope
           - Functional (what)
           - Non-functional (scale, latency, availability)
           - Constraints

Min 5-10   Capacity estimation
           - DAU, QPS, data growth, storage

Min 10-15  High-level design (4 boxes)
           - Client → App → Data → Infra

Min 15-30  Deep dive on 2-3 components
           - Pick risky/interesting parts
           - Tradeoffs explicit

Min 30-35  Reliability, monitoring, scaling
           - SLOs, alerts
           - Failure modes
           - Multi-region
```

## Functional vs Non-Functional

### Functional
- What does the system do?
- Features, use cases
- API endpoints, data flows

### Non-Functional
- How well does it do it?
- Scale (users, requests/sec, data)
- Latency (p50, p99)
- Availability (nines)
- Consistency
- Cost
- Security
- Compliance

Most candidates jump to "what" before "how well". Slow down.

## Driving the Discussion

Interviewer is evaluating your engineering judgment. Ask:
- "Should I focus more on storage or compute?"
- "Are reads dominant or writes?"
- "Is consistency or availability more important here?"

Make calls; don't wait for instructions.

## Capacity Estimation

### From DAU
- 100M DAU
- Avg 10 actions/user/day
- = 1B actions/day
- = 11.5K actions/sec average
- Peak ~3× average = 34K/sec

### Storage
- Each action: 1 KB
- 1B/day × 1 KB = 1 TB/day = 365 TB/year

### Read:Write Ratio
- Typical 100:1 for social, 10:1 for transactional
- 34K writes/sec → 3.4M reads/sec (at 100:1)

### Bandwidth
- Reads × response size
- 3.4M × 10 KB = 34 GB/sec (uphill)

Numbers drive architecture choices.

## Numbers to Know

```
1 KB ≈ 10^3 bytes
1 MB ≈ 10^6 bytes
1 GB ≈ 10^9 bytes
1 TB ≈ 10^12 bytes
1 PB ≈ 10^15 bytes

86,400 seconds/day
2.6M seconds/month
31.5M seconds/year

L1 cache: 0.5 ns
L2 cache: 7 ns
Main memory: 100 ns
SSD read: 150 μs
HDD seek: 10 ms
Same DC RTT: 0.5 ms
Same region: 1-2 ms
Cross-region (US E-W): 70 ms
US-Europe: 100 ms
US-Asia: 150-200 ms
```

## The 4 Boxes

```
[Client]            [App Layer]              [Data Layer]            [Infra]
- Web/Mobile        - API servers            - SQL DBs               - DNS / CDN
- Cache             - Workers                - NoSQL DBs             - Load balancers
- State             - Queues / streams       - Cache (Redis)         - Networking
                    - Auth                   - Search (ES)           - Monitoring
                                             - Object storage        - Security
```

Start with this. Fill in as you go deep.

## Component Inventory

For a typical web service:
- Load balancer (CDN at edge; LB regional)
- App tier (stateless; multi-AZ)
- Cache (in-memory tier)
- DB primary + replicas
- Async tier (queue + workers)
- Search index
- Object storage
- Observability (metrics, logs, traces)

Each component you draw → ready to discuss tradeoffs if asked.

## Diagramming

Use boxes + arrows. Show data direction. Label everything.

```
[Browser] ──HTTPS──→ [CDN] ──→ [ALB] ──→ [API Cluster (3 AZs)] ──→ [Aurora MySQL]
                                                ↓
                                          [Redis Cluster]
                                                ↓
                                    [SQS] ──→ [Workers] ──→ [DB]
```

Don't over-detail at high level. Drill in when interviewer asks.

## Tradeoffs to Name Explicitly

For every choice, state the tradeoff:
- CP vs AP (CAP)
- Latency vs consistency (PACELC)
- Cost vs performance
- Complexity vs reliability
- Build vs buy
- Sync vs async
- SQL vs NoSQL

Showing you know the tradeoff = engineering judgment.

## Failure Modes (Always Discuss)

For each component:
- What happens if it fails?
- How is failure detected?
- What's the user impact?
- What's the recovery?

E.g., "If primary DB fails, multi-AZ standby promotes in ~60s; brief write unavailability."

## What Strong Candidates Do

- Drive the conversation
- Ask clarifying questions early
- Math on numbers
- Name explicit tradeoffs
- Identify risk areas + propose mitigations
- Discuss observability + operations
- Handle scope creep (defer to follow-ups)

## What Weak Candidates Do

- Wait for instructions
- Skip estimation
- Vague architecture (boxes without specifics)
- No tradeoff discussion
- Over-engineer (multi-region for an MVP)
- Forget operations / observability

## Common Prompts (Devops-Specific)

- Design a CI/CD platform
- Design a metrics pipeline at scale
- Design a logging pipeline
- Design a tracing system
- Design an internal developer platform
- Design Cloudflare's edge
- Design Vault's secret backend
- Design a global load balancer
- Design Netflix's deployment system
- Design a feature flag service
- Design a distributed rate limiter

## Interview Themes

- "Walk me through your system design framework"
- "Functional vs non-functional"
- "Capacity estimation — sample"
- "Numbers every engineer should know"
- "4 boxes model"
