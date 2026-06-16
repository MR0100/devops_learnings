# L08/C06/T01 — RDS (MySQL, PostgreSQL, Oracle, SQL Server)

## Learning Objectives

- Operate RDS in production
- Pick engine

## RDS

Managed RDBMS. AWS handles:
- Provisioning
- Patching (in window)
- Backups
- Multi-AZ failover
- Read replicas

You: schema, queries, encryption choice, tuning.

## Engines

- **PostgreSQL**: modern default; many features
- **MySQL**: mature, popular
- **MariaDB**: MySQL fork
- **Oracle**: legacy, licensing
- **SQL Server**: Windows shops
- **Aurora** (separate; covered T02): AWS proprietary

For new: Postgres or Aurora Postgres.

## Instance Classes

- db.t (burstable): dev / small
- db.m (general): balanced
- db.r (memory): most DBs
- db.x (massive memory): very large in-memory workloads

DBs are memory-bound; r family typical.

## Storage

- gp3 (default SSD)
- io1/io2 (provisioned IOPS for IO-heavy)
- magnetic (legacy)

Storage Autoscaling: auto-grow when full.

```bash
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --engine postgres \
  --engine-version 16.1 \
  --db-instance-class db.r6g.large \
  --allocated-storage 100 \
  --storage-type gp3 \
  --master-username admin \
  --master-user-password '...' \
  --multi-az
```

## Multi-AZ

Synchronous standby in another AZ. Auto-failover on primary failure (~60s).

Doubles cost; worth it for production.

Failover triggers:
- Primary instance failure
- AZ failure
- DB software patching
- Maintenance window changes
- Manual

## Read Replicas

Async replication; for read scaling. Up to 15 (MySQL / MariaDB / PostgreSQL; raised from 5 in 2023-24). Oracle/SQL Server have lower limits.

Cross-region replicas possible.

Promotion: turn replica into standalone (e.g., for DR).

Eventual consistency: replica lag.

## Backups

Automated:
- Daily snapshot
- Transaction logs every 5 min
- Retention 0-35 days
- PITR within retention

Manual snapshots: persist beyond retention.

Cross-region copy.

```bash
aws rds create-db-snapshot --db-instance-identifier mydb --db-snapshot-identifier daily-snap
```

## PITR

Point-in-time recovery:
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier mydb \
  --target-db-instance-identifier mydb-restored \
  --restore-time 2026-06-09T10:00:00Z
```

Creates new instance. Original untouched.

## Maintenance Windows

Weekly window when:
- Minor version updates (if AutoMinorVersionUpgrade)
- OS patches
- Hardware fixes

Multi-AZ: standby patched first; failover; primary patched. ~minute downtime.

Single-AZ: full outage during patch.

## Parameter Groups

DB config (postgres.conf equivalents):
```bash
aws rds create-db-parameter-group --db-parameter-group-name pg16-custom --db-parameter-group-family postgres16 --description "Custom"
aws rds modify-db-parameter-group --db-parameter-group-name pg16-custom --parameters "ParameterName=max_connections,ParameterValue=1000,ApplyMethod=pending-reboot"
```

Some params static (need restart), others dynamic.

## Option Groups

Engine-specific features (e.g., SQL Server agent, Oracle TDE).

## Encryption

At rest: KMS-encrypted (recommended, often default).
In transit: TLS optional but recommended.

Force TLS via parameter group:
```
rds.force_ssl = 1
```

Encrypted snapshot for encrypted DB.

## Performance Insights

Built-in query analytics; identifies slow queries. Free for 7-day retention.

```
Top SQL:
1. SELECT ... 2300ms avg, called 1200/min
```

Find bottlenecks.

## Enhanced Monitoring

OS-level metrics (CloudWatch is hypervisor-level). Per-second metrics.

Cost: small. Enable for production.

## CloudWatch Metrics

- CPUUtilization
- DatabaseConnections
- FreeableMemory
- ReadIOPS / WriteIOPS
- ReadLatency / WriteLatency
- ReplicaLag

Alert on:
- High CPU sustained
- Connections near max (running out)
- Lag on replica
- Free memory low
- IOPS at limit

## Storage Performance

- gp3: 3000 IOPS / 125 MB/s baseline; provision more
- io1/io2: high IOPS

For DB at saturation: provision more IOPS / throughput.

## RDS Proxy

Connection pooler managed by AWS:
- Connection multiplexing
- Failover handling
- IAM auth

Use when app has many connections.

```bash
aws rds create-db-proxy --db-proxy-name myproxy --engine-family POSTGRESQL --auth ... --role-arn ... --vpc-subnet-ids ...
```

App connects to proxy endpoint; proxy manages DB connections.

Especially useful for Lambda (each invocation can open connection; quickly exhausts DB max).

## IAM Auth

Connect with IAM creds instead of DB password:
```bash
TOKEN=$(aws rds generate-db-auth-token --hostname myhost --port 5432 --username myuser)
psql "host=myhost port=5432 user=myuser password=$TOKEN sslmode=require"
```

Token valid 15 min.

For: avoiding password rotation; using IAM roles.

## Secrets Manager Integration

Store DB password in Secrets Manager; rotate automatically:
```bash
aws secretsmanager rotate-secret --secret-id myDbSecret
```

RDS native rotation (rotates user password without app awareness).

## Upgrade Process

Minor version: auto (in maintenance window) or manual.

Major version: more careful:
1. Test in non-prod
2. Take snapshot
3. Upgrade (downtime)
4. Or: Blue/green deployment (newer)

Blue/green:
```bash
aws rds create-blue-green-deployment --source arn:... --target-engine-version 16.2 --target-db-parameter-group-name new-pg
```

Creates parallel "green" environment; switch traffic when ready.

## Cross-Region DR

Read replica in another region; promote on disaster.

Aurora Global Database: <1s RPO; faster than RDS cross-region replica (covered T02).

For RDS: ~minute RPO.

## RDS Sizing

Right-size:
- Memory: enough for working set
- CPU: 50-70% avg target
- Storage: 50% used or less typical
- IOPS: <80% sustained

Compute Optimizer recommends.

## Connection Limit

Default depends on instance class:
- db.t3.micro: 87
- db.m5.large: 819
- db.r5.4xlarge: 5000+

Track `DatabaseConnections`. Approach limit → upsize OR pool.

## Backups Best Practices

- Retention 14-30 days minimum
- Cross-region copy
- Test restore quarterly
- Manual snapshots for major events

## Disaster Recovery

| RPO/RTO | Method |
|---|---|
| Hours | Cross-region snapshot copy |
| 30 min | Cross-region read replica + promote |
| < 1 sec | Aurora Global Database |

Cost / complexity scale with tightness.

## Common Mistakes

- Single-AZ in production
- Backups disabled or 1-day retention
- No connection pooling
- Public DB endpoint
- No encryption
- Same VPC; no isolation
- Maintenance window during peak

## Best Practices

- Multi-AZ for production
- 30-day backup retention
- Encryption (at rest + in transit)
- Private subnets only
- Connection pooling (proxy or app)
- IAM auth + Secrets Manager
- Performance Insights enabled
- Monitor + alert
- Test failover quarterly

## Cost Optimization

- Reserved Instances (1 or 3 year): 30-60% off
- Right-size
- Stop dev/test outside hours
- Aurora Serverless for variable workloads
- Aurora I/O Optimized (no per-IO charges)
- Storage tier matching

## RDS Performance Tuning

When DB slow:
1. Performance Insights: top queries
2. EXPLAIN ANALYZE problem queries
3. Index review
4. Vacuum (Postgres)
5. Statistics
6. Cache hit ratio
7. Right-size if hitting limits

## Quick Refs

```bash
# Create
aws rds create-db-instance --db-instance-identifier mydb --engine postgres ...

# Snapshot
aws rds create-db-snapshot --db-instance-identifier mydb --db-snapshot-identifier mysnap

# Restore PITR
aws rds restore-db-instance-to-point-in-time --source-db-instance-identifier mydb --target-db-instance-identifier mydb-new --restore-time 2026-06-09T10:00:00Z

# Modify (resize)
aws rds modify-db-instance --db-instance-identifier mydb --db-instance-class db.r6g.xlarge --apply-immediately
```

## Interview Prep

**Mid**: "Multi-AZ vs Read Replica."

**Senior**: "RDS upgrade with zero downtime."

**Staff**: "DB scaling at 100k QPS."

## Next Topic

→ [T02 — Aurora Architecture](T02-Aurora.md)
