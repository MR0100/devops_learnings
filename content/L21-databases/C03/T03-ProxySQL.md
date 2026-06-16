# L21/C03/T03 — ProxySQL

## Learning Objectives

- Use ProxySQL
- Query routing

## ProxySQL

MySQL proxy:
- Read/write split
- Connection pool
- Query rewrite
- High perf

## Install

```bash
apt install proxysql
```

## Config

```sql
INSERT INTO mysql_servers (hostgroup_id, hostname, port) VALUES
(0, 'primary', 3306),
(1, 'replica-1', 3306),
(1, 'replica-2', 3306);

LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
```

Hostgroups:
- 0: writes
- 1: reads

## Rules

```sql
INSERT INTO mysql_query_rules (rule_id, match_pattern, destination_hostgroup, apply) VALUES
(1, '^SELECT.*FOR UPDATE', 0, 1),     -- writes
(2, '^SELECT', 1, 1),                   -- reads to replicas
(3, '^(INSERT|UPDATE|DELETE)', 0, 1);   -- writes

LOAD MYSQL QUERY RULES TO RUNTIME;
```

App connects to ProxySQL:6033; ProxySQL routes.

## Connection Pool

ProxySQL pools to backend. App connects without worry.

## Monitor Replication

ProxySQL polls replicas:
- Lag
- Status

Auto-remove if lagging.

## Failover

If primary down:
- ProxySQL detects (via monitoring)
- Promote replica
- ProxySQL config updates

For: rapid recovery.

## Query Rewrite

```sql
INSERT INTO mysql_query_rules
(match_pattern, replace_pattern, ...) VALUES
('SELECT.*old_name', 'SELECT id FROM new_name', ...);
```

For: schema migrations.

## High Availability

Multiple ProxySQL:
- LB in front
- Cluster mode (sync config)

## Performance

- Adds ~1 ms
- Massive throughput
- Memory low

## Vs Native

| | ProxySQL | App routing |
|---|---|---|
| Routing | proxy | app code |
| Pool | yes | app pool |
| Rewrite | yes | no |
| Complexity | infra | code |

For: ProxySQL: ops-friendly.

## Best Practices

- Per-cluster ProxySQL
- HA pair
- Monitor stats
- Rule tested

## Common Mistakes

- Single ProxySQL (SPOF)
- Stale config (don't run LOAD)
- Wrong rule order
- Slow replica still active

## Quick Refs

```sql
-- Admin port: 6032
-- Data port: 6033

LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL QUERY RULES TO RUNTIME;
LOAD MYSQL USERS TO RUNTIME;

SHOW MYSQL SERVERS;
SHOW MYSQL QUERY RULES;
```

## Interview Prep

**Mid**: "ProxySQL."

**Senior**: "Read/write split."

**Staff**: "MySQL proxy at scale."

## Next Topic

→ [T04 — Backup (mysqldump, Percona XtraBackup)](T04-MySQL-Backup.md)
