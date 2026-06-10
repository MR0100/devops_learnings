# L21/C06/T04 — Restoring Without Crying

## Learning Objectives

- Restore reliably
- Avoid disasters

## The Problem

"We have backups."
3 AM incident.
Backup restore: fails.
Then you cry.

For: untested = no backup.

## Test Restores

Frequency:
- Monthly: full restore to test env
- Quarterly: cross-region restore
- Annually: full DR drill

For: known works.

## Restore Process

Document:
```markdown
1. Identify backup to restore
2. Provision target instance
3. Restore base backup
4. Apply WAL / binlog (if PITR)
5. Verify data
6. Verify app connects
7. Promote / cutover
8. Verify SLO
9. Post-restore review
```

For: clarity at 3 AM.

## Verify Backup

Don't just take. Verify:
```bash
# Postgres
pg_basebackup --checksums
WAL replay test

# MySQL
mysqlbinlog --verify-binlog-checksum
```

For: not corrupt.

## Practice

Drill:
- Pick random recent backup
- Restore
- Time it
- Document issues

For: muscle memory.

## Failure Modes

### Backup Corrupt
Bit rot. Storage failure.

Mitigation: checksums; multiple copies.

### Restore Slow
Hours when promised minutes.

Mitigation: test; profile.

### Missing WAL
WAL archive incomplete.

Mitigation: monitor archive; alarm gaps.

### Wrong Version
Backup from PG 14; trying restore to PG 13.

Mitigation: keep target version handy.

### Encryption Key Lost
Encrypted backup; key gone.

Mitigation: key escrow.

## Multi-Copy

```
Primary backup: S3 (encrypted)
Copy 1: S3 different region
Copy 2: Glacier (long-term)
```

For: redundancy.

## Tested = Backup

If untested:
- Schrodinger's backup
- Could be fine; could be empty

Test.

## On-Call Run Book

```
"Database corrupt; need PITR to 14:00"

Steps:
1. Stop app
2. Snapshot current (for analysis)
3. Provision new instance
4. Restore: wal-g backup-fetch /data LATEST
5. Configure: restore_command + target_time
6. Start; wait for recovery_target reached
7. Promote: pg_promote()
8. Verify: SELECT COUNT(*) FROM critical_table;
9. Switch app
10. Postmortem
```

For: speed under pressure.

## Compliance

Some require:
- Annual restore test
- Documented
- Reviewed by audit

## Restore Time Estimation

```
TB to restore = X
Bandwidth from S3 = Y MB/s
WAL to apply = Z hours

Total = X / Y + Z + start up + verify
```

Plan accordingly.

## What Could Go Wrong

- Backup not found
- Backup not readable
- Wrong region
- Key not available
- Target capacity insufficient
- App can't reconnect (DNS, IP)
- Different schema
- Encryption mismatch
- Network issue

Mitigate each.

## Real Incidents

### GitLab 2017
Restored from backup; backup empty.
6 hours of data loss.

Lesson: VERIFY backups.

### Many others
- Backup process broke months ago
- Nobody noticed

For: monitor backup job.

## Backup Monitoring

```promql
time() - postgres_backup_last_success_seconds > 86400
```

Alert if no backup in 24 hr.

## Practice Drills

Game day:
- Pretend disaster
- Restore to staging
- Document gaps

For: skill maintenance.

## Best Practices

- Monthly test restore
- Multi-copy
- Checksums
- Documented runbook
- Monitored backups
- Practice failover

## Common Mistakes

- "Backups are running" without verify
- Restore not tested
- Single copy
- No runbook
- 3 AM = no idea what to do

## Post-Restore

Verify:
- Row counts match
- Specific records present
- App functions
- SLO maintained

For: confidence.

## Quick Refs

```
Test:
  Monthly: restore + verify
  Quarterly: cross-region
  Annually: full DR

Document:
  Runbook (step-by-step)
  Estimated time
  Verification checklist

Monitor:
  Backup success
  Age of last backup
  Size trends
```

## Interview Prep

**Mid**: "Restore process."

**Senior**: "Test backups."

**Staff**: "DR strategy."

## Next Topic

→ Move to [L21/C07 — Database Observability](../C07/README.md)
