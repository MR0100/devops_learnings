# L27/C05 — Backups That Actually Work

## Topics

- **T01 3-2-1 Backup Rule** — Time-tested
- **T02 Testing Restores** — Mandatory
- **T03 Immutable Backups** — Ransomware defense

## 3-2-1 Backup Rule

> **3** copies of data, **2** different media, **1** off-site.

Cloud version:
- 3 copies (primary, in-region backup, cross-region backup)
- 2 distinct services (e.g., RDS snapshot + S3 with WAL)
- 1 off-site (different region, or cold storage with separate creds)

## Backup Types

### Logical
- Schema + data as SQL/JSON
- Portable across versions
- Slow restore for big datasets

### Physical / Snapshot
- File-level
- Fast restore
- Tied to specific version/platform

### Continuous (WAL Archiving)
- Stream changes
- Point-in-time recovery
- Minimal RPO

## Backup Frequency vs Retention

```
Daily snapshots: keep 30 days
Weekly: keep 12 weeks
Monthly: keep 12 months
Yearly: keep N years (compliance)
```

GFS (Grandfather/Father/Son) rotation. Old strategy that still works.

## Backup Storage

### Tier the Storage
- Hot: recent backups in fast accessible storage
- Cool: older backups in IA
- Cold: archive (Glacier Deep Archive)

### Cross-Region
- S3 cross-region replication of backup bucket
- Snapshot copy to another region
- Cross-cloud for paranoid

### Cost
For 1 TB DB with continuous backup + 1-year retention:
- ~$300/month all in (cheap insurance)

## Immutable Backups

### Why
Ransomware encrypts everything it can reach (including backups). Immutable backups survive.

### Implementation

#### S3 Object Lock
```bash
aws s3api put-object \
  --bucket backups \
  --key db-2026-06-09.dump \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date 2027-06-09T00:00:00Z
```

`COMPLIANCE` mode: nobody (including root) can delete during retention. `GOVERNANCE` mode: privileged users can override.

#### Air Gap
- Physically separate storage
- Tape backups in vault
- Different cloud provider

#### Different Credentials
- Backup destination uses separate IAM role / account
- Primary credentials compromise doesn't reach backups

## Test Restores

> A backup you haven't restored is just a thing on disk.

### Cadence
- Quarterly minimum
- Major DB: monthly
- After backup procedure change: immediate

### Process
1. Pick a recent backup
2. Restore to sandbox environment
3. Verify data integrity (count rows, checksum samples)
4. Verify app can connect
5. Measure time (compare to RTO)
6. Document any gaps

### Automation
Build restore drill into CI:
- Spin up sandbox
- Restore from backup
- Run sanity checks
- Report results

Discovered issues get fixed before disaster.

## Sample Backup Strategy (Postgres)

```
Layer 1: WAL-G continuous archiving to S3
  → PITR to any second up to 35 days

Layer 2: pg_basebackup nightly
  → Fast restore for full-instance recovery

Layer 3: Logical dump weekly
  → Schema portability; emergency export

Layer 4: Cross-region replication of S3 bucket
  → Regional disaster

Layer 5: Glacier Deep Archive monthly
  → Compliance retention

Immutability: Object Lock on S3 bucket (COMPLIANCE mode, 30 days)
```

Layered. Each addresses different failure mode.

## Backup Validation

### Integrity Check
- After backup: hash the file
- Periodically: download + verify
- Detects: silent corruption, bit rot

### Restore Check
- Periodically: restore to sandbox
- Run application smoke tests
- Verify data matches expectations

### Both
Don't trust either alone. Integrity = "bits intact". Restore = "actually usable".

## Common Backup Failures

- **Encrypted; key lost** → unrecoverable
- **Stored only in same region** → regional disaster destroys both
- **Same credentials as primary** → ransomware reaches both
- **No retention policy** → backup pile grows; cost spirals; can't find right one
- **Never tested** → discovers it doesn't work during actual disaster
- **Manual process** → not run consistently
- **No alerting on failed backups** → finds out after the fact

## Cloud Service Backup Coverage

### RDS
- Daily automated backups (1-35 days retention)
- Manual snapshots
- Point-in-time recovery within window
- Snapshot share / copy to another region

### DynamoDB
- Point-in-time recovery (continuous; 35 days)
- On-demand backups (manual)
- AWS Backup integration

### S3
- Versioning (recover deleted)
- Lifecycle policies (move to Glacier)
- Cross-region replication
- Object Lock for immutability

### Cloud Native Postgres / Aurora
- Continuous backup to S3
- 1-35 days PITR

### Kubernetes Volumes
- Velero (VolumeSnapshot CSI)
- Cloud provider-native snapshot tools
- Application-aware (e.g., quiesce DB before snapshot)

## Velero (K8s Backup)

```bash
velero install \
  --provider aws \
  --bucket velero-backups \
  --backup-location-config region=us-east-1

velero backup create daily --include-namespaces='*' --ttl 720h
velero schedule create daily-backup --schedule="0 2 * * *" --include-namespaces='*'

velero restore create --from-backup daily-20260609
```

Backs up: K8s objects + PVs + namespace state.

## Audit & Documentation

- List of what's backed up (services, frequency, retention)
- Where backups live
- How to restore
- Who has access
- Test results history
- Last successful test date per service

Auditors and incident responders need this.

## Interview Themes

- "3-2-1 backup — apply to cloud"
- "Immutable backups — why and how"
- "Test restores — strategy"
- "Common backup failures"
- "Postgres backup strategy"
- "Velero — what does it back up?"
