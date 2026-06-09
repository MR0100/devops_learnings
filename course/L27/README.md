# L27 — Disaster Recovery, HA & Multi-Region

## Overview

RTO and RPO are board-level metrics. Multi-region design is what separates senior+ engineers. This lecture covers the spectrum from backup-restore to active-active globally.

**6 chapters, 18 topics.**

## Chapter Map

### [C01](C01/) — DR Fundamentals
- T01 RTO, RPO, MTD
- T02 DR Strategies (Backup/Restore, Pilot Light, Warm Standby, Active/Active)

### [C02](C02/) — High Availability Patterns
- T01 Single AZ vs Multi-AZ
- T02 Multi-Region Architecture
- T03 Active/Active vs Active/Passive
- T04 Cells & Bulkheads (Amazon's Approach)

### [C03](C03/) — Data Replication
- T01 Synchronous vs Asynchronous
- T02 Cross-Region Replication
- T03 Conflict Resolution

### [C04](C04/) — Failover Mechanics
- T01 DNS-Based Failover
- T02 Health Checks
- T03 Failover Automation

### [C05](C05/) — Backups That Actually Work
- T01 3-2-1 Backup Rule
- T02 Testing Restores (Mandatory)
- T03 Immutable Backups (Ransomware Defense)

### [C06](C06/) — Region Evacuation
- T01 Pre-Drained Regions
- T02 Traffic Steering

## The Four DR Strategies

| Strategy | RTO | RPO | Cost |
|---|---|---|---|
| Backup & Restore | Hours–Days | Hours | Low |
| Pilot Light | Tens of min | Min | Low-Med |
| Warm Standby | Min | Sec | Med-High |
| Active/Active | ~Zero | ~Zero | High |

## Multi-Region Patterns

### Active/Passive
- Primary serves all traffic
- Standby region kept warm
- Failover via DNS (Route53 with health checks)
- RTO: minutes; RPO: seconds (async replication)

### Active/Active
- Both regions serve traffic (geographic routing)
- Data: bi-directional replication with conflict resolution
- Requires apps to be conflict-tolerant or use CRDTs / Spanner-like global ACID
- More complex but lowest RTO/RPO

### Cells (Amazon-style)
- Workload split into independent cells (e.g., per customer)
- Failure of one cell affects only its slice
- Used at AWS for blast radius reduction

## Backup 3-2-1 Rule

- **3** copies of data
- **2** different media
- **1** off-site

Modern cloud version: 3 copies in 2 distinct cloud regions, 1 in immutable / cold storage with separate credentials.

## Restore Testing

> A backup you haven't restored is just a thing on disk. Test restores.

- Quarterly restore drill minimum
- Document RTO actual vs target
- Restore to a separate environment (so you don't risk the production)
- Verify data integrity

## DNS Failover Caveats

- TTLs lie — many resolvers honor minimum 60s+
- Browsers cache DNS for the page session
- Client SDKs may cache forever
- DNS failover is NOT instant; budget for 1–5 min real-world

For faster: anycast IPs (Global Accelerator), BGP failover.

## Recommended Reading

- *Designing Data-Intensive Applications* — Ch 5, 9
- *Building Secure & Reliable Systems* — Google
- AWS Well-Architected Reliability pillar
- *Sustainable Software Engineering* — Microsoft GreenSWE

## Interview Themes

- "Define RTO and RPO"
- "Compare DR strategies"
- "Walk me through a multi-region failover"
- "Cells — what problem do they solve?"
- "Active/active with conflicts — how?"

## Next

→ [L28 — System Design for DevOps & Platform Engineers](../L28/README.md)
