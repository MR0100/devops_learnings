# L27/C05/T02 — Testing Restores (Mandatory)

## Learning Objectives

- Test restores
- Avoid GitLab-style disasters

(Covered L21/C06/T04 — referencing.)

## Untested Backup ≠ Backup

Famous: GitLab 2017.
- 5 backup methods
- All failed
- 6 hours data lost

For: test or it's hope.

## Frequency

- Monthly: small restore
- Quarterly: full restore
- Annually: DR drill

## Process

```
1. Pick backup
2. Provision target
3. Restore
4. Verify
5. Document time + issues
```

## Verify

- Row count
- Specific records
- App connects
- Functions work

For: confirmed.

## Document

```markdown
## Restore Test 2026-01-15

Backup: 2026-01-14 daily snapshot
Target: test instance
Start: 14:00
Complete: 14:35
Verify pass: yes

Issues found:
- Permissions not restored (action: fix script)

Action: Re-test after fix
```

## Failure Modes

- Backup corrupt
- Wrong region (slow)
- Missing key
- Wrong version
- Slow restore

Find before crisis.

## Real Examples

### GitLab 2017
Public postmortem; influential.

### Code Spaces 2014
Backup deleted by hacker; out of business.

For: lessons.

## Best Practices

- Monthly tests
- Document
- Action items
- Drill (full DR)
- Various backup vintages

## Common Mistakes

- "Backups are running" without test
- One-time test
- No documentation
- Same backup tested (variety needed)

## Quick Refs

```
Test:
- Monthly small
- Quarterly full
- Annually DR drill

Untested = no backup
```

## Interview Prep

**Mid**: "Test restores."

**Senior**: "Verify."

**Staff**: "Backup confidence."

## Next Topic

→ [T03 — Immutable Backups (Ransomware Defense)](T03-Immutable-Backups.md)
