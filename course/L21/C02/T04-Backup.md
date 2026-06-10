# L21/C02/T04 — Postgres Backup

## Learning Objectives

- Backup Postgres
- Restore tested

## Backup Types

### pg_dump
Logical:
- SQL output
- Per-database
- Restorable to different version

### pg_basebackup
Physical:
- Full data dir copy
- Faster for huge
- Same version restore

### WAL archive
Continuous:
- Every WAL segment archived
- Restore to point-in-time

## pg_dump

```bash
pg_dump -h localhost -U postgres -d mydb -F c -f mydb.dump
```

Custom format: compressed, restorable subset.

## Restore

```bash
pg_restore -h localhost -U postgres -d mydb mydb.dump
```

## pg_basebackup

```bash
pg_basebackup -h primary -D /backup -U replicator -P
```

Whole data dir. Fast.

## Restore

```bash
# Stop PG
systemctl stop postgresql

# Replace data dir
rm -rf /var/lib/postgresql/data
cp -r /backup /var/lib/postgresql/data

# Start
systemctl start postgresql
```

## WAL-G

Modern; supports cloud storage:
```bash
# Backup
WALG_S3_PREFIX=s3://my-backups wal-g backup-push /var/lib/postgresql/data

# Restore
wal-g backup-fetch /var/lib/postgresql/data LATEST

# Continuous WAL archive
archive_command = 'wal-g wal-push %p'
```

For: cloud-native.

## pgBackRest

Mature:
- Incremental
- Parallel
- Compression

```bash
pgbackrest backup --stanza=mydb --type=full
pgbackrest restore --stanza=mydb
```

## Point-In-Time Recovery (PITR)

```bash
# Restore base
wal-g backup-fetch /var/lib/postgresql/data LATEST

# Configure for PITR
echo "restore_command = 'wal-g wal-fetch %f %p'" >> postgresql.conf
echo "recovery_target_time = '2026-01-01 12:00:00'" >> postgresql.conf

# Start; replays WAL until target
systemctl start postgresql
```

For: restore to before incident.

## RPO

How much data loss tolerable:
- Daily backup: 24 hr possible loss
- + WAL archive: minutes
- + Sync replica: seconds-zero

For: lower RPO = more infrastructure.

## RTO

Recovery time:
- pg_dump restore: hours for big DB
- pg_basebackup restore: similar
- + WAL replay: faster (depends on lag)
- Failover to standby: minutes

## Strategy

```
1. Daily pg_basebackup → S3
2. Continuous WAL archive
3. Test restore monthly
4. Geo-replicated backup
5. Sync replicas for failover
```

## Encryption

Backups encrypted:
```bash
wal-g backup-push --encryption-key=KMS_KEY
```

For: at-rest.

## Retention

```
Recent (7 days): hot in S3
Old (30 days): cold tier
Archive (1 year): glacier
Delete: > 1 year
```

For: cost + compliance.

## Test Restore

Critical. Monthly:
1. Restore to test instance
2. Verify
3. Document

For: "have backups" ≠ "can restore."

## Cross-Region

For: regional DR.

```bash
WALG_S3_PREFIX=s3://us-west-2-backups
```

## Logical vs Physical Comparison

| | pg_dump | pg_basebackup | WAL-G |
|---|---|---|---|
| Format | SQL | data dir | data + WAL |
| Speed (huge DB) | slow | fast | fast |
| Restore version | any newer | same | same |
| PITR | no | with WAL | yes |
| Incremental | no | no | yes |

## Best Practices

- pg_basebackup + WAL archive (WAL-G)
- S3 backed
- Encrypted
- Tested restore monthly
- Multi-region
- Retention policy

## Common Mistakes

- pg_dump only (no PITR)
- No restore test (untested = no backup)
- Same region (no DR)
- No encryption

## Quick Refs

```bash
# Backups
pg_dump -F c -f mydb.dump DB
pg_basebackup -D /backup
wal-g backup-push /data
pgbackrest backup --stanza=mydb

# Restore
pg_restore mydb.dump
wal-g backup-fetch /data LATEST
pgbackrest restore

# PITR
recovery_target_time = '...'
```

## Interview Prep

**Mid**: "Postgres backup."

**Senior**: "PITR."

**Staff**: "Backup strategy."

## Next Topic

→ [T05 — Performance Tuning](T05-Postgres-Tuning.md)
