# L21/C03/T02 — MySQL Replication

## Learning Objectives

- Set up replication
- Choose mode

## Modes

### Async
Primary doesn't wait.

### Semi-Sync
Wait for at least 1 replica ack.

### Sync / Group Replication
Multiple replicas; quorum.

## Setup Async

Primary:
```ini
server-id = 1
log_bin = ON
binlog_format = ROW
```

```sql
CREATE USER 'repl'@'%' IDENTIFIED BY '...';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
```

Replica:
```ini
server-id = 2
read_only = ON
```

```sql
CHANGE MASTER TO
  MASTER_HOST = 'primary',
  MASTER_USER = 'repl',
  MASTER_PASSWORD = '...',
  MASTER_LOG_FILE = 'bin.00001',
  MASTER_LOG_POS = 12345;
START SLAVE;
```

## GTID

Modern; better:
```ini
gtid_mode = ON
enforce_gtid_consistency = ON
```

Tracks transactions globally.

## Semi-Sync

```sql
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = 1;
```

Primary waits for ACK. Timeout fallback to async.

## Group Replication

MySQL 8 native:
- Multi-primary or single-primary
- Auto-failover
- Conflict detection

```ini
plugin_load_add = group_replication.so
group_replication_group_name = "..."
```

## InnoDB Cluster

Helm bundle:
- Group Replication
- MySQL Router
- MySQL Shell admin

For: easier HA.

## Monitor Lag

```sql
SHOW SLAVE STATUS\G

-- Seconds_Behind_Master
-- Slave_IO_Running
-- Slave_SQL_Running
```

## Failover

Old way: manual.
Group Replication: automatic.

Tools:
- Orchestrator (GitHub)
- ProxySQL

## Read Scaling

- Primary: writes
- Replicas: reads

App or proxy splits.

## ProxySQL

Routes by query:
```sql
INSERT ... → primary
SELECT ... → replica
```

(See T03.)

## Conflicts (Multi-Primary)

Group Replication multi-primary:
- Detect conflicts
- Roll back loser
- Avoid hotspot writes

For: complex.

## Best Practices

- GTID-based
- Semi-sync for important data
- Group Replication for HA
- Monitor lag
- Test failover

## Common Mistakes

- Async without lag awareness
- Manual binlog position
- No replication monitoring
- One primary only (SPOF)

## Quick Refs

```sql
-- Show
SHOW MASTER STATUS;
SHOW SLAVE STATUS;
SHOW REPLICA STATUS;  -- 8.x rename

-- Control
STOP SLAVE; START SLAVE;
```

## Interview Prep

**Mid**: "MySQL replication."

**Senior**: "GTID."

**Staff**: "Group Replication."

## Next Topic

→ [T03 — ProxySQL](T03-ProxySQL.md)
