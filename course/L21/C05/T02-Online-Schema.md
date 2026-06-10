# L21/C05/T02 — Online Schema Changes (gh-ost, pt-online-schema-change)

## Learning Objectives

- Migrate without locking
- Use online tools

## Problem

ALTER TABLE on huge:
- Locks table
- Hours for big tables
- App down

## pt-online-schema-change (Percona)

```bash
pt-online-schema-change \
  --alter "ADD COLUMN email VARCHAR(255)" \
  D=mydb,t=users \
  --execute
```

How:
1. Create new table with desired schema
2. Trigger captures changes
3. Copy data
4. Swap tables

## gh-ost (GitHub)

Triggerless:
- Uses binlog
- Less impact

```bash
gh-ost \
  --user=X --password=Y \
  --host=primary \
  --database=mydb \
  --table=users \
  --alter="ADD COLUMN email VARCHAR(255)" \
  --execute
```

For: lower impact than pt-osc.

## Why Triggerless

- pt-osc triggers: write amplification
- gh-ost: replicates from binlog

Performance better.

## When

For tables:
- > 1 GB
- High write rate
- Can't afford lock

For small: regular ALTER.

## Postgres

```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```

PG: AddColumn fast (just metadata).

```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL DEFAULT '';
```

PG: ADD with DEFAULT now: also fast (PG11+).

## Postgres Index

```sql
CREATE INDEX CONCURRENTLY idx ON users(email);
```

Online; no lock.

## pg_repack

Online VACUUM FULL + reindex:
```sql
pg_repack -t users
```

## Tools per DB

- MySQL: gh-ost, pt-osc
- Postgres: pg_repack, native CONCURRENTLY
- Mongo: no need (schema flexible)

## Workflow

1. Test on staging
2. Run during off-peak
3. Monitor
4. Pause if load spikes

## gh-ost Throttle

```bash
gh-ost --throttle-control-replicas=replica1,replica2 \
  --throttle-flag-file=/tmp/gh-ost.throttle
```

Pauses if replicas lag.

## Reversible

If migration goes bad:
- gh-ost: cut-over → cancel before
- pt-osc: similar

For: cancel before swap.

## Expand-Contract

```
1. Add column (online)
2. Backfill (batched)
3. App reads/writes
4. Drop old (later)
```

Multiple deploys.

## Best Practices

- Test on prod-size dataset
- Off-peak run
- Throttle on replica lag
- Monitor binlog growth
- Expand-contract pattern

## Common Mistakes

- ALTER on huge prod table (locks)
- No test on staging
- Forget triggers (pt-osc)
- Stuck migration (no monitoring)

## Quick Refs

```bash
# gh-ost
gh-ost --execute / --test / --dry-run

# pt-online-schema-change
pt-online-schema-change --execute / --dry-run

# Postgres
ALTER TABLE ... (PG11+ many ops fast)
CREATE INDEX CONCURRENTLY
pg_repack
```

## Interview Prep

**Mid**: "Online schema change."

**Senior**: "gh-ost vs pt-osc."

**Staff**: "Migration strategy."

## Next Topic

→ [T03 — Zero-Downtime Migration Patterns](T03-Zero-Downtime.md)
