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

**Mid**: "CAP."

**Senior**: "PACELC."

**Staff**: "Consistency trade-offs."

## Next Topic

→ Move to [L28/C03 — Reliability Patterns](../C03/README.md)
