# L21/C02/T03 — PgBouncer

## Learning Objectives

- Use PgBouncer
- Tune pooling

## Why

Postgres connections:
- ~10 MB each
- Process per connection
- Limit ~100-500 typical

Many app servers:
- 100 × 50 conns = 5000
- DB collapses

PgBouncer: pool.

## PgBouncer

Connection pooler:
- App connects to PgBouncer
- PgBouncer reuses few DB conns
- Drastically reduces DB load

## Install

```bash
apt install pgbouncer
```

## Config

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

## Pool Modes

### Session
1 client conn = 1 server conn for whole session.
Allows: features, prepared statements.

### Transaction
Conn returned after each tx.
Allows: more pooling.

### Statement
Conn returned after each statement.
Limited features.

For most: transaction.

## Client → PgBouncer → DB

```
App (1000 conns) → PgBouncer (handles 1000) → DB (25 conns)
```

40× reduction.

## Settings

```ini
max_client_conn = 10000       # max from apps
default_pool_size = 25          # DB conns per (db, user)
reserve_pool_size = 5           # extras for surge
reserve_pool_timeout = 5        # wait before using reserve
```

## Transaction Mode Caveats

Features broken:
- Prepared statements (PG14+ work)
- Session variables
- LISTEN/NOTIFY
- Holds via SET commands

For: app aware.

## Multi-Pool

For multiple DBs:
```ini
[databases]
db1 = host=primary dbname=db1
db2 = host=primary dbname=db2
analytics = host=replica dbname=db1
```

Route by name.

## Read/Write Split

App connects to "primary" or "replica":
- PgBouncer routes
- Read replicas for SELECT

For: app explicit.

## High Availability

PgBouncer HA:
- Multiple PgBouncer instances
- LB in front
- Patroni manages PG primary; PgBouncer config updates

For: no SPOF.

## Monitor

```bash
psql -h pgbouncer -p 6432 -U admin pgbouncer

SHOW POOLS;
SHOW CLIENTS;
SHOW SERVERS;
SHOW STATS;
```

For: status.

## Stats

- Conn count per pool
- Wait time
- Queries/sec

Export to Prometheus.

## Performance

- Latency: ~1ms added
- Throughput: massive boost
- Memory: very low

For: critical infra.

## Alternative: Odyssey

Yandex:
- More features
- Multi-process

## Built-in Pooler (PG14+)

```
listen_addresses = '*'
max_connections = 100
```

PG built-in is just per-process; not pool.

For: PgBouncer still needed.

## RDS Proxy

AWS RDS Proxy:
- Managed PgBouncer-like
- Cloud-native
- IAM integration

For: AWS managed.

## Best Practices

- Transaction mode
- Pool size: connections × CPU / 4
- Monitor pool usage
- Reserve pool for surges
- HA setup

## Common Mistakes

- Session mode without need
- Pool too small (queueing)
- Pool too large (DB overwhelmed)
- Single PgBouncer (SPOF)

## App Side

App pool + PgBouncer:
- App pool small (10-25)
- PgBouncer handles aggregation

For: layered.

## Specifically

```python
# App pool
pool = ConnectionPool(min=5, max=25, ...)
# Connects to PgBouncer
```

PgBouncer presents many app conns to small DB pool.

## Quick Refs

```ini
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

```sql
SHOW POOLS;
SHOW STATS;
```

```bash
pgbouncer -d /etc/pgbouncer/pgbouncer.ini
```

## Interview Prep

**Mid**: "What's PgBouncer."

**Senior**: "Pool modes."

**Staff**: "Connection pooling at scale."

## Next Topic

→ [T04 — Backup (pg_dump, pg_basebackup, WAL-G)](T04-Backup.md)
