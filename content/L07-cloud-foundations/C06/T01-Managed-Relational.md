# L07/C06/T01 — Managed Relational (RDS, Cloud SQL, Azure SQL)

## Learning Objectives

- Use managed relational DBs
- HA, backup, scaling

## Why Managed

Run a DB yourself:
- Install
- Patch (security, perf, bug)
- Configure HA / failover
- Backup automation
- Restore testing
- Performance tuning
- Replicate for read scale
- Monitor
- Scale up (downtime)

Managed: provider does most. You focus on schema + queries.

## RDS (AWS)

Engines: Postgres, MySQL, MariaDB, Oracle, SQL Server, Aurora.

Per-instance:
- Compute class (db.t3, db.r5, db.m5)
- Storage (gp3, io1)
- Engine version

Pricing: instance-hour + storage + I/O + backup.

## Aurora

AWS's cloud-native RDBMS. MySQL- or Postgres-compatible.

Architecture:
- Storage decoupled (6-way replicated across 3 AZs)
- Compute scales independently
- Up to 15 read replicas
- Auto-failover (~30s)
- Backtrack (rewind point-in-time)
- Aurora Serverless v2: auto-scale ACU (compute units)

Costs more per instance-hour; better availability and perf.

## Multi-AZ

Standby in another AZ; sync replication; automatic failover.
- RDS Multi-AZ: ~60-120s failover
- Aurora: ~30s

Doubles cost. Worth it for production.

## Read Replicas

Async replicas for read scale. Eventual consistency.
- Postgres: streaming replication
- MySQL: binary log replication
- Aurora: shared storage; fast

Replica lag matters: monitor.

## Backups

Automated:
- Daily snapshot
- Transaction logs every 5 min
- Retention 1-35 days
- Point-in-time restore within retention

Manual snapshots: persist beyond retention (until manually deleted).

Restore: creates new instance. Original untouched.

## Patching

Maintenance window (you pick): RDS applies minor versions; you can defer.
Major version: you trigger.

For HA Multi-AZ: standby patched first; then failover; then primary. ~minute downtime.

## Performance Insights

Per-query analytics; identifies slow queries. Built into RDS.

## Storage Auto Scale

Configure: when storage > 90%, grow N GB. Limits prevent runaway.

## Encryption

At-rest: KMS keys (master key). Required: SSL/TLS for in-transit.

## Cloud SQL (GCP)

Engines: Postgres, MySQL, SQL Server.
- HA option: synchronous standby
- Read replicas
- Backups + PITR
- Automatic version updates

Simpler than RDS in some ways; fewer features.

## Azure SQL Database

Microsoft SQL Server-based:
- Single database (DTU or vCore)
- Elastic pool (shared resources)
- Managed Instance (full SQL Server compatibility)

Auto-tuning, threat detection, geo-replication.

## DB Sizing

Start small; scale:
- Vertical: bigger instance (downtime to switch)
- Horizontal reads: replicas
- Horizontal writes: sharding (app-level; harder)

For most apps: vertical until very large; then consider sharding or NoSQL.

## Connection Management

Apps spawning many connections kill DB. Use connection pool:
- pgBouncer (Postgres)
- ProxySQL (MySQL)
- RDS Proxy (AWS managed)

Pool: maintain limited connections; multiplex requests.

## Failover Testing

Test failover regularly. Most teams don't; first real failure surprises.

```bash
aws rds reboot-db-instance --db-instance-identifier mydb --force-failover
```

## DR (Cross-Region)

Read replica in another region (async). Promote on disaster. RPO: seconds-minutes. RTO: minutes.

Aurora Global Database: cross-region replica with <1s RPO.

## Cost Tips

- Reserved Instances: 30-60% off for 1-3 yr
- Stop dev/test outside hours
- Right-size storage (don't over-provision)
- Aurora Serverless if bursty
- Read replicas only when actually read-heavy

## Maintenance / Upgrades

Upgrade major version:
1. Take snapshot
2. Restore to new instance with new version
3. Test
4. Cut over

Or in-place upgrade (downtime).

## Monitoring

CloudWatch:
- CPUUtilization
- FreeableMemory
- ReadIOPS, WriteIOPS
- ReadLatency, WriteLatency
- DatabaseConnections
- ReplicaLag

Alert on:
- High CPU
- High connections (running out)
- High lag
- Low free memory

## Performance Tuning

- Slow query log
- EXPLAIN ANALYZE
- Index review
- Vacuum (Postgres)
- Connection pooling
- Caching layer (Redis)

Managed doesn't tune your queries; that's still on you.

## Choose Engine

| | Postgres | MySQL | Aurora |
|---|---|---|---|
| Features | Most | Mature | Postgres/MySQL + cloud features |
| Performance | Very good | Very good | Better at scale |
| Compatibility | High | High | High (with original) |
| Cost | Cheaper | Cheaper | Premium |
| Manageability | RDS managed | RDS managed | Most managed |

Default: Aurora or RDS Postgres for new AWS workloads.

## Common Mistakes

- Single-AZ in prod
- Backups not tested
- No monitoring
- DB on tiny instance (saturated)
- No connection pooling
- Read-from-replica without considering lag
- Putting everything in DB (use S3, queues for not-relational)

## Best Practices

- Run production Multi-AZ (or Aurora) for automatic failover; accept the doubled cost as the price of HA.
- Enable automated backups with adequate retention and periodically test point-in-time restore — an untested backup is not a backup.
- Use connection pooling (RDS Proxy / PgBouncer) so spiky/serverless clients don't exhaust DB connections.
- Add read replicas only when genuinely read-heavy, and account for replica lag before reading from them.
- Right-size and use Performance Insights / slow-query logs to fix queries and indexes — managed services don't tune your SQL.
- Encrypt at rest with KMS, keep the DB in private subnets, and copy snapshots cross-region for DR.

## Quick Refs

HA/scaling primitives — don't confuse them:

| Feature | Purpose | Consistency |
|---|---|---|
| Multi-AZ | HA / automatic failover | Synchronous standby |
| Read Replica | Read scale-out | Async (lag) |
| Cross-region replica | DR / geo-reads | Async |
| Aurora | Decoupled storage, fast failover, up to 15 replicas | 6-way across 3 AZs |

Failover times: RDS Multi-AZ ~60–120s · Aurora ~30s.

Engine pick: RDS Postgres/MySQL for standard managed workloads; Aurora when you want better scale/availability and can pay the premium; Aurora Serverless v2 for bursty/unpredictable load.

Metrics to alarm on: `CPUUtilization`, `FreeableMemory`, `DatabaseConnections`, `ReadLatency`/`WriteLatency`, `ReplicaLag`.

## Interview Prep

**Mid**: "RDS Multi-AZ vs Read Replica."

**Senior**: "Cross-region DR for RDS."

**Staff**: "DB scaling at 100k QPS — strategy."

## Next Topic

→ [T02 — Managed NoSQL](T02-Managed-NoSQL.md)
