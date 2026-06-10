# L28/C02/T03 — Replication Patterns

## Learning Objectives

- Apply replication patterns
- Architecture

## Single-Leader

```
Writer → Leader → Replicas (read-only)
```

Simple; lag possible.

For: most DBs.

## Multi-Leader

```
Writer → Any leader → Other leaders
```

Active-active.

For: multi-region.

## Leaderless

```
Writer → Any node (multiple)
Reader → Any node (multiple)
```

Cassandra, DynamoDB.

For: high availability.

## Patterns

### Read Replicas
Offload reads.

### Hot Standby
Ready to promote.

### Cold Standby
Periodic backup; slow promote.

### Cross-Region
Async typically.

## Consistency

- Strong: read sees latest
- Read-your-writes: own writes
- Eventual: catches up

## CAP

(See T04.)

CP or AP per replication.

## Read Patterns

### Read from Leader
Strong consistency.

### Read from Replica
Faster; possible lag.

### Read from Local
Geo-distributed.

## Examples

### Postgres
Single-leader streaming.

### MySQL
Single or Group Replication.

### MongoDB
Single-leader (primary) + secondaries.

### Cassandra
Leaderless.

### DynamoDB
Auto.

### Spanner
Multi-leader sync (Paxos).

## Best Practices

- Default single-leader
- Multi-leader for HA cross-region
- Read replicas for scale
- Monitor lag

## Common Mistakes

- Read replica for critical (stale)
- Multi-leader without conflict plan
- No lag monitoring

## Quick Refs

```
Single-leader: most common
Multi-leader: HA cross-region
Leaderless: massive HA

Tools:
- Postgres / MySQL: single
- Mongo: single
- Cassandra: leaderless
- Spanner: multi
```

## Interview Prep

**Mid**: "Replication patterns."

**Senior**: "Pick pattern."

**Staff**: "Replication strategy."

## Next Topic

→ [T04 — CAP & PACELC](T04-CAP-PACELC.md)
