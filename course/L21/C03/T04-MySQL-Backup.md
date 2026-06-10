# L21/C03/T04 — MySQL Backup

## Learning Objectives

- Backup MySQL
- Choose tool

## Tools

### mysqldump
Logical:
```bash
mysqldump -u root -p --all-databases > backup.sql
mysqldump -u root -p --single-transaction --routines mydb > mydb.sql
```

Pros: simple, portable.
Cons: slow for huge.

## Restore mysqldump

```bash
mysql -u root -p mydb < mydb.sql
```

## mydumper

Parallel mysqldump:
```bash
mydumper -h primary -u root --threads=8 -o /backup
myloader -h target -u root --threads=8 -d /backup
```

For: faster.

## Percona XtraBackup

Physical, hot:
```bash
xtrabackup --backup --target-dir=/backup
xtrabackup --prepare --target-dir=/backup

# Restore (stop MySQL first)
xtrabackup --copy-back --target-dir=/backup
chown -R mysql:mysql /var/lib/mysql
systemctl start mysql
```

For: huge DB, no locking.

## Binlog Backup

For PITR:
```bash
mysqlbinlog binlog.000001 > binlog-2026-01-01.sql
```

Continuous archive.

## PITR

```bash
# Restore base
xtrabackup --copy-back ...

# Apply binlogs up to time
mysqlbinlog --start-position=... --stop-datetime='2026-01-01 12:00:00' binlog.000002 | mysql -u root
```

For: restore before incident.

## RDS / Aurora Backup

Managed:
- Auto snapshots daily
- PITR up to 35 days
- Cross-region copy

For: AWS native; less ops.

## Encryption

```bash
xtrabackup --encrypt=AES256 --encrypt-key=KEY ...
```

For: at-rest.

## Test Restore

Monthly:
1. Restore to test instance
2. Verify
3. Document time

For: confidence.

## Best Practices

- XtraBackup for prod (hot, fast)
- mysqldump for small / portability
- Binlog continuous archive
- Cross-region S3
- Encrypted
- Test monthly

## Common Mistakes

- mysqldump only (slow for huge)
- No binlog archive (no PITR)
- Same region (no DR)
- Never test

## Quick Refs

```bash
# Dump
mysqldump --single-transaction --routines mydb > mydb.sql

# Parallel
mydumper -h X -u U -o /backup

# Physical
xtrabackup --backup --target-dir=/backup
xtrabackup --prepare --target-dir=/backup

# Binlog
mysqlbinlog binlog.000001 > backup.sql

# AWS
aws rds create-db-snapshot ...
```

## Interview Prep

**Mid**: "MySQL backup."

**Senior**: "XtraBackup."

**Staff**: "PITR strategy."

## Next Topic

→ Move to [L21/C04 — NoSQL Operations](../C04/README.md)
