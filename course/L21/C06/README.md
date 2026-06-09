# L21/C06 — Backups & DR

## Topics

- **T01 RPO & RTO for Databases** — Quantifying recovery
- **T02 Point-in-Time Recovery** — WAL/binlog archiving
- **T03 Cross-Region Replication** — Multi-region survival
- **T04 Restoring Without Crying** — Test, test, test

## RPO and RTO

- **RPO (Recovery Point Objective)**: max data loss tolerable
- **RTO (Recovery Time Objective)**: max time to restore service

### Typical Targets
| Tier | RPO | RTO |
|---|---|---|
| Tier 1 (revenue critical) | < 1 min | < 15 min |
| Tier 2 (important) | < 1 hour | < 4 hours |
| Tier 3 (other) | < 1 day | < 1 day |

Define per service. Drives backup strategy.

## Backup Types

### Logical
- pg_dump, mysqldump
- Schema + data as SQL
- Portable across versions
- Slow to restore at TBs

### Physical
- File-system snapshot of data dir
- pg_basebackup, XtraBackup
- Fast restore
- Tied to specific version + platform

### Continuous Archive
- WAL (Postgres), binlog (MySQL) shipped continuously
- Combined with base backup → point-in-time recovery
- Minimal RPO

### Snapshot (Cloud)
- EBS snapshot, GCP PD snapshot
- File-system level
- Fast (copy-on-write)
- Restore: launch new instance from snapshot

## Point-in-Time Recovery (PITR)

```
Base backup (Monday 0:00)
   + WAL Mon 0:00 → Mon 12:34:56
   = state at Mon 12:34:56
```

You can restore to any moment between base backup and now.

### Postgres + WAL-G
```bash
# Backup nightly
wal-g backup-push /var/lib/postgresql/data

# WAL continuous (archive_command in config)
archive_command = 'wal-g wal-push %p'

# Restore to point-in-time
wal-g backup-fetch /restore LATEST
echo "restore_command = 'wal-g wal-fetch %f %p'" >> recovery.conf
echo "recovery_target_time = '2026-06-09 12:00:00'" >> recovery.conf
```

### MySQL + binlog
- XtraBackup base
- Continuous binlog
- Restore: apply binlogs to base up to target time

### Cloud Managed
- RDS Automated Backups: 1-35 day retention with PITR (set during creation; pricey beyond default)
- Aurora: continuous backup to S3
- Cloud SQL: similar

## Cross-Region Replication

### For Read Replicas
- Postgres: streaming replication cross-region (async; ~100ms+ lag)
- Aurora Global Database: <1s lag, automated cross-region
- DynamoDB Global Tables: multi-region multi-active

### For Backup Storage
- S3 cross-region replication (CRR) of backup bucket
- Snapshot copy to another region

### Disaster scenarios
- Single AZ failure → Multi-AZ standby
- Regional outage → cross-region promote (manual or automated)
- Logical corruption → PITR

## Backup Strategy

```
Primary (RDS Multi-AZ in us-east-1)
   ↓ continuous replication
Cross-region Replica (us-west-2)
   ↓ snapshots
S3 (cross-region replicated)
   ↓
Glacier (long-term, immutable)
```

Layered: each layer different failure mode protected.

## Backup Hygiene

### Frequency
- Continuous (WAL/binlog) — best
- Hourly snapshots
- Daily full
- Weekly off-site

### Retention
- Daily: 7-30 days
- Weekly: 6-12 months
- Monthly: years
- Yearly: regulatory

### 3-2-1 Rule
- **3** copies of data
- **2** different media types
- **1** off-site

Cloud version: 2 regions + 1 cold storage.

### Immutability
Object Lock / WORM:
- Ransomware defense
- Compliance retention
- Backup can't be deleted even by admin

```
S3 Object Lock COMPLIANCE mode: no one (even root) can delete during retention
```

## Restoring

### Test Quarterly
Backup not restored = backup that doesn't exist. Test:
1. Pick a recent backup
2. Restore to a sandbox
3. Validate data integrity
4. Measure time taken (compare to RTO)
5. Document gaps + fix

### Common Surprises
- Encrypted backup; key lost → unrecoverable
- Backup of secondary; secondary was lagging → data loss
- Restore needs specific Postgres version → not available anymore
- Restore needs IAM permissions you don't have anymore
- DNS not updated → app talks to old DB
- Replicas don't auto-reattach → stuck primary-only

### Restore Runbook
```markdown
# Restore Production Postgres

## Prerequisites
- AWS account access (prod-recovery role)
- KMS key XYZ access
- DNS update permission

## Steps
1. Identify latest good backup: `aws rds describe-db-snapshots --db-instance-identifier prod-db`
2. Restore to new instance:
   `aws rds restore-db-instance-from-db-snapshot --db-snapshot-identifier <id> ...`
3. Wait for available (10-20 min)
4. Verify data: `psql -c "SELECT count(*) FROM critical_table"`
5. Update DNS: `dnsupdate prod-db.internal new-host.rds.amazonaws.com`
6. Restart apps
7. Monitor + verify
8. Document timeline

## Rollback
- If verify fails: stay on snapshot, investigate
- Repeat with older snapshot if needed

## Time Estimate
- 15-30 min total
```

## Backup Failure Modes

Track:
- Backup job success rate
- Time since last successful backup (alarm if > 24h)
- Backup size growing too fast (corruption? infinite loop?)
- Restore time measurements

## DR Drills

Quarterly:
- Full restore to recovery region
- Failover test
- Application reconnection test
- Time measurements

Document outcomes; address gaps.

## Backup Cost

For large DBs:
- Storage: ~$0.023/GB/mo (S3 Standard)
- Snapshot: ~$0.05/GB/mo (EBS-style)
- Cross-region transfer: ~$0.02/GB

A 1 TB DB with continuous backup + 1-yr retention: ~$300/month. Cheap insurance.

## Interview Themes

- "Design backup strategy for X"
- "RPO/RTO for tier 1 service"
- "Point-in-time recovery — how works"
- "Ransomware defense for backups"
- "Test restores — why and how"
