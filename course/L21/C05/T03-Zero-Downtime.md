# L21/C05/T03 — Zero-Downtime Migration Patterns

## Learning Objectives

- Migrate without downtime
- Coordinate app + DB

## Goal

DB changes:
- App keeps running
- Both old + new app work during migration
- No data loss

## Expand-Contract

```
Phase 1 (Expand): Add new column
Phase 2: Backfill data
Phase 3: App reads new (or both)
Phase 4: App writes only new
Phase 5 (Contract): Drop old column
```

Multiple deploys; each safe.

## Backward Compatible

App + DB:
- Old app must work with new schema
- New app must work with old schema (temporarily)

For: gradual.

## Example: Rename Column

Bad:
```sql
ALTER TABLE users RENAME COLUMN name TO full_name;
-- Old app breaks
```

Good (expand-contract):
```
1. ADD COLUMN full_name VARCHAR(255)
2. App writes both name + full_name
3. Backfill full_name from name
4. App reads full_name; writes both
5. App reads + writes only full_name
6. DROP COLUMN name
```

5 deploys.

## Example: Add Required Column

Bad:
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL;
-- Existing rows: NULL → fail
```

Good:
```
1. ADD COLUMN email VARCHAR(255)  -- nullable
2. App fills email for new rows
3. Backfill existing
4. ALTER COLUMN email SET NOT NULL
```

## Example: Drop Column

```
1. App stops reading column
2. App stops writing column
3. DROP COLUMN
```

Verify steps before dropping.

## Backfill

For huge:
```python
batch = 1000
while True:
    rows = db.fetch(f"SELECT id FROM users WHERE email IS NULL LIMIT {batch}")
    if not rows: break
    for r in rows:
        db.execute(f"UPDATE users SET email = ... WHERE id = {r.id}")
    time.sleep(0.1)
```

Batched. Throttled.

## Data Type Change

Bad:
```sql
ALTER COLUMN price TYPE BIGINT;
-- Rewrite table; lock
```

Good (Postgres):
```sql
ALTER TABLE x ADD COLUMN price_new BIGINT;
UPDATE x SET price_new = price;
ALTER TABLE x DROP COLUMN price;
ALTER TABLE x RENAME COLUMN price_new TO price;
```

But: DROP / RENAME both quick metadata changes (PG).

## Foreign Keys

Adding:
```sql
ALTER TABLE orders ADD CONSTRAINT fk_user 
  FOREIGN KEY (user_id) REFERENCES users(id) 
  NOT VALID;

ALTER TABLE orders VALIDATE CONSTRAINT fk_user;
```

NOT VALID: quick; no lock.
VALIDATE: scans; no lock (PG).

## Indexes

```sql
CREATE INDEX CONCURRENTLY idx ON users(email);
```

No lock. Slower but online.

Drop:
```sql
DROP INDEX CONCURRENTLY idx;
```

## App + DB Coordinate

Deploy order:
- Some changes: DB first
- Some: app first
- Some: simultaneous

Example: drop column. App stops using first.

## Migrations in CI/CD

```yaml
- name: Apply migration
  run: flyway migrate

- name: Deploy app
  run: kubectl set image deploy/app ...
```

Migration before deploy.

## Rolling Deploys

K8s rolling:
- Old + new pods run
- Both need to work with schema during

For: backward compat critical.

## Tools

- gh-ost / pt-osc (MySQL)
- pg_repack (Postgres reorg)
- Atlas migrate

## Pre-Deploy Tests

- App tests on new schema
- App tests on old + new together
- Verify backward compat

## Postgres Online Operations

Many fast in PG11+:
- ADD COLUMN with DEFAULT
- DROP COLUMN
- ALTER COLUMN TYPE (most)

For: easier than MySQL.

## MySQL Limitations

- Many ALTERs lock
- Online tools needed (gh-ost)

## Cutover

For major (DB switch):
- Setup new DB
- Replicate
- Switch app
- Decommission old

Tools: AWS DMS, manual replication.

## Best Practices

- Backward compat always
- Multi-step migrations
- Test on staging
- Backfill batched
- Monitor during

## Common Mistakes

- One-step destructive change
- Forget backward compat
- Migration not tested
- Backfill not throttled

## Quick Refs

```
Pattern: expand-contract
Step 1: Add new (compatible)
Step 2: Backfill
Step 3: Switch app
Step 4: Drop old

Tools:
- Postgres: CREATE INDEX CONCURRENTLY, ADD COLUMN
- MySQL: gh-ost, pt-osc
```

## Interview Prep

**Mid**: "Zero-downtime migration."

**Senior**: "Expand-contract."

**Staff**: "Migration patterns."

## Next Topic

→ Move to [L21/C06 — Backups & DR](../C06/README.md)
