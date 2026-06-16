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

**Junior**: "What are the main replication patterns?" — Single-leader (one node takes writes, replicas serve reads — most databases), multi-leader (multiple write nodes, used for multi-region active-active), and leaderless (any node accepts reads/writes with quorums — Cassandra/Dynamo). They trade write simplicity against availability.

**Mid**: "When would you use a read replica versus reading from the leader?" — Read replicas offload read traffic and scale reads cheaply, but they lag the leader, so they're fine for analytics, feeds, and anything tolerant of slightly-stale data. For read-your-writes or anything where stale data is wrong (checking your own just-placed order), read from the leader or use a consistency token — replica lag is the trap here.

**Senior**: "How do you pick a replication pattern for a given system?" — Map it to the consistency and geography needs. Single-leader is the default — simple, consistent, lag-monitored. Go multi-leader only when you genuinely need local writes in multiple regions, and only with a conflict-resolution plan (LWW/CRDTs), because conflicts are the cost. Leaderless when availability under partition trumps consistency. The decision is really a CAP/PACELC decision (T04) about what you do during a partition and what latency you'll pay otherwise.

**Staff**: "Design replication for a system that needs low-latency global reads and strong writes." — Single write region with synchronous replication to a local standby (so an acked write survives a node loss, RPO≈0) plus asynchronous read replicas in each region for fast local reads — accepting bounded staleness on those reads. If the business truly needs local writes everywhere, that's multi-leader or a system like Spanner (synchronous consensus, paying cross-region latency on writes) — and I'd push back on whether the latency cost is justified, because most "global write" requirements are actually "global read, regional write." Lag monitoring and a tested leader-promotion path are non-negotiable operationally.

## Next Topic

→ [T04 — CAP & PACELC](T04-CAP-PACELC.md)
