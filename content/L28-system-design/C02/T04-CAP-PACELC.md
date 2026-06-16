# L28/C02/T04 — CAP & PACELC

## Learning Objectives

- Understand CAP
- Apply PACELC

## CAP

Brewer's theorem:
- **C**onsistency
- **A**vailability
- **P**artition tolerance

Pick 2.

In distributed: P required.

So: CP or AP.

## CP

Strong consistency:
- May refuse writes during partition
- Spanner, Postgres (single leader during partition)

## AP

High availability:
- Accept writes; resolve later
- Cassandra, DynamoDB

## PACELC

Extension (Daniel Abadi):
- If Partition: A or C
- Else (no partition): Latency or Consistency

For: most time, no partition; trade L vs C.

## Examples

### Spanner
PC/EC: strong always.

### DynamoDB
PA/EL: AP during partition; low latency otherwise.

### Cassandra
PA/EL.

### Postgres
PC/EC (sync) or PA/EL (async replicas).

## In Practice

Real systems:
- Tunable
- Cassandra QUORUM: more consistent
- ONE: more available

For: pick per query.

## Network Reality

Partitions:
- Rare in well-engineered
- But happen
- Plan for both modes

## Latency vs Consistency

Strong consistency cross-region:
- Sync (slow)
- Or fail

Eventual:
- Local writes fast
- Eventual sync

## Latency Numbers

- Same DC: < 1 ms
- Cross-AZ: 1-5 ms
- Cross-region: 50-200 ms
- Cross-cont: 100-300 ms

## When CP

- Banking
- Inventory
- Critical state

## When AP

- Social feeds
- Likes
- Eventual updates OK

## Hybrid

Some queries strong (transactional):
- Use CP system

Some eventual (analytics):
- AP fine

## Examples

### E-commerce
- Cart: AP (don't lose items)
- Order: CP (don't double charge)

### Social
- Feed: AP
- DM: CP (delivery)

## Best Practices

- Know your system's CAP
- Pick per use case
- Tunable when possible
- Document trade-off

## Common Mistakes

- "We have CA" (impossible distributed)
- Strong cross-region (slow)
- Eventual when not OK

## Quick Refs

```
CAP: C, A, P (pick 2 in distributed)
PACELC: PC/EC, PA/EL, etc.

Default:
- CP: Spanner, Postgres
- AP: Cassandra, DynamoDB
```

## Interview Prep

**Junior**: "What does CAP say?" — Under a network partition you can't have both consistency and availability — you pick one. Since partition tolerance isn't optional in a distributed system, the real choice is CP (refuse writes to stay consistent) or AP (stay available, reconcile later). "CA" only describes a single node.

**Mid**: "Why is PACELC a better lens than CAP?" — Because partitions are rare, and CAP says nothing about the normal case. PACELC adds: *else* (no partition), you still trade Latency vs Consistency. DynamoDB is PA/EL (available under partition, low-latency-but-eventual otherwise); Spanner is PC/EC (consistent always, paying latency). That 'else' clause describes how the system behaves 99.9% of the time, which is what actually matters.

**Senior**: "Give a concrete CP-vs-AP decision and defend it." — In e-commerce, the cart is AP — never reject an add-to-cart over a partition; a transient duplicate item is cheaper than a lost sale, and you reconcile later. The order/payment is CP — refuse to proceed rather than risk a double charge or overselling inventory; correctness beats availability there. Same product, opposite choices, because the cost of being wrong differs per operation.

**Staff**: "How do you reason about consistency across a whole system, not one database?" — Per-operation, not per-system. I classify each path by the cost of staleness and the cost of unavailability, then place it: strong/CP systems for money and inventory, AP/eventual for feeds, likes, and analytics. Many stores are tunable (Cassandra QUORUM vs ONE), so I set the level per query rather than globally. The mistake is a blanket 'we're strongly consistent' — it's slow and unnecessary for most paths — or a blanket 'eventual' that silently corrupts the paths that needed strong. I document the choice and its partition behavior so on-call knows what 'degraded' means.

## Next Topic

→ Move to [L28/C03 — Reliability Patterns](../C03/README.md)
