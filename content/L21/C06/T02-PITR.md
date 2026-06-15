# L21/C06/T02 — Point-in-Time Recovery

## Learning Objectives

- Set up PITR
- Restore to time

## PITR

Restore DB to specific time:
- Before bad change
- Before delete
- Before corruption

## Postgres PITR

Requires:
- Base backup
- WAL archive

### Setup

```ini
# postgresql.conf
archive_mode = on
archive_command = 'wal-g wal-push %p'
```

WAL segments → S3.

### Restore

```bash
# Restore base
wal-g backup-fetch /data LATEST

# Configure target
cat > /data/postgresql.auto.conf <<EOF
restore_command = 'wal-g wal-fetch %f %p'
recovery_target_time = '2026-01-15 14:30:00'
EOF

# Mark recovery
touch /data/recovery.signal

# Start
systemctl start postgresql
```

PG replays WAL until target.

## Verify

After:
```sql
SELECT pg_is_in_recovery();
SELECT now(), pg_last_wal_receive_lsn();
```

Promote to writable:
```sql
SELECT pg_promote();
```

## MySQL PITR

Binlogs:
```bash
# Restore base
xtrabackup --copy-back ...

# Apply binlogs up to time
mysqlbinlog --stop-datetime='2026-01-15 14:30:00' binlog.000010 binlog.000011 | mysql -u root
```

## AWS RDS

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier original \
  --target-db-instance-identifier restored \
  --restore-time 2026-01-15T14:30:00Z
```

Automatic up to 35 days back.

## Granularity

Postgres: WAL position (1 sec ish).
MySQL: 1 statement.
RDS: 5 minutes for older; finer recent.

## Use Cases

### Bad DELETE
```sql
DELETE FROM users;  -- oops; no WHERE
```

PITR to before.

### Corrupt Migration
Schema migration broke. Restore.

### Logical Corruption
Bug wrote bad data.

## Test PITR

Quarterly:
- Pick random time
- Restore to test instance
- Verify

For: known works.

## Multiple PITR

For DR:
- Local PITR (5-min RPO)
- Cross-region PITR (hour RPO)

## Storage

WAL volume:
- Active DB: GB per day
- Archive: months / years

Cost: significant. Cold tier OK for old.

## Compression

```bash
wal-g wal-push %p   # auto-compressed
```

## Encryption

```bash
wal-g backup-push --encryption-key=KMS
```

## Atlas PITR (MongoDB)

```bash
mongorestore --oplogReplay --oplogLimit ts:ord
```

Up to oplog window.

## DynamoDB PITR

```bash
aws dynamodb update-continuous-backups --table-name X \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

aws dynamodb restore-table-to-point-in-time \
  --source-table-name X \
  --target-table-name X-restored \
  --restore-date-time 2026-01-15T14:30:00Z
```

35 day window.

## Best Practices

- PITR enabled
- Tested
- Cross-region archive
- Encrypted
- Retention policy

## Common Mistakes

- No WAL archive (no PITR)
- Not tested (won't work when needed)
- No DR test
- Wrong target time

## Quick Refs

```
Postgres:
  archive_command = 'wal-g wal-push %p'
  restore_command = 'wal-g wal-fetch %f %p'
  recovery_target_time = '...'

MySQL:
  mysqlbinlog --stop-datetime=...

AWS:
  restore-db-instance-to-point-in-time
```

## Interview Prep

**Mid**: "PITR."

**Senior**: "Setup + test."

**Staff**: "DR with PITR."

## Next Topic

→ [T03 — Cross-Region Replication](T03-Cross-Region-Replication.md)
