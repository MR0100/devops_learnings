# L27/C05/T03 — Immutable Backups (Ransomware Defense)

## Learning Objectives

- Protect against ransomware
- Implement immutability

## Threat

Ransomware:
- Encrypts data
- Demands payment
- If backups encrypted too: dead

## Defense

Immutable backups:
- Cannot be modified
- Cannot be deleted
- WORM (Write Once Read Many)

For: ransomware can't touch.

## S3 Object Lock

```bash
aws s3api put-object-lock-configuration \
  --bucket my-backups \
  --object-lock-configuration ...
```

Modes:
- Governance: admin can override
- Compliance: cannot override

For: stronger.

## Retention

```json
{
  "Mode": "COMPLIANCE",
  "RetainUntilDate": "2027-01-01T00:00:00Z"
}
```

Locked until date.

## Glacier Vault Lock

Stronger:
- Write policy
- Lock policy
- Cannot change

For: max defense.

## Air-Gapped

Physical separation:
- Off-line backups
- Tape
- Different cloud account

For: ultimate.

## Account Isolation

Backups in separate AWS account:
- Different IAM
- Hard to compromise both
- Cross-account replication

## Hourly Backups

Frequent:
- Incremental
- Many points to restore
- Less data loss

## Encryption + Keys

Backups encrypted:
- Keys separate
- KMS strict access

If keys compromised: bad.

For: key rotation, MFA.

## Detection

Backup integrity:
- Hashes
- Compare regularly
- Alert if mismatch

## Test

Restore from immutable:
- Verify works
- Document
- Periodic drill

## Real Attacks

### Many ransomware victims
Backups encrypted; paid ransom.

### Heroes
Immutable backups saved them.

For: real risk.

## Best Practices

- Object Lock for backups
- Separate account
- Air-gap critical
- Test restore
- Detect tampering

## Common Mistakes

- Backups in primary account (compromised together)
- No immutability
- Long-running creds (compromise)
- No detection

## Quick Refs

```
S3 Object Lock: Compliance mode
Glacier Vault Lock: write + lock policies
Account separation
Air-gap for critical
```

## Interview Prep

**Mid**: "Immutable backup."

**Senior**: "Ransomware defense."

**Staff**: "Backup security."

## Next Topic

→ Move to [L27/C06 — Region Evacuation](../C06/README.md)
