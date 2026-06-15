# L21/C05 — Database Migrations

## Topics

- **T01 Schema Migration Tools** — Flyway, Liquibase, Atlas
- **T02 Online Schema Changes** — gh-ost, pt-online-schema-change
- **T03 Zero-Downtime Migration Patterns** — Expand/contract

## Schema Migration Tools

### Flyway
- SQL files, named with version: `V1__create_users.sql`, `V2__add_email.sql`
- Java-based, but DB-agnostic SQL
- Migrates forward only (no rollback by default; rollback = new migration)

```sql
-- V1__create_users.sql
CREATE TABLE users (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL);

-- V2__add_email.sql
ALTER TABLE users ADD COLUMN email TEXT;
```

### Liquibase
- XML/YAML/JSON/SQL changesets
- More features (preconditions, rollback)
- DB-agnostic

### Atlas (Ariga)
- Declarative HCL or SQL schemas
- "Desired state"; tool computes diff
- Better for schema-first workflows
- Modern alternative

### Language-Specific
- Alembic (SQLAlchemy/Python)
- Django migrations (Python)
- ActiveRecord (Rails)
- TypeORM/Prisma (TS)
- golang-migrate

### Choosing
- DB-agnostic team: Flyway / Liquibase / Atlas
- Specific language stack: native tool (Alembic, ActiveRecord, etc.)
- Schema-first: Atlas

## Migrations in CI/CD

```yaml
- name: Migrate DB
  run: flyway migrate -url=jdbc:postgresql://... -user=migrator -password=...
  env:
    FLYWAY_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

Best practices:
- Run BEFORE app deploy (app must work with new schema)
- Or AFTER, if change is backward-compatible
- Decide per migration

### Locking
Many migration tools take a global lock. Be aware on multi-instance deploys (ArgoCD might trigger migrate twice).

Use `flyway migrate` with idempotent advisory lock, or run migrations only from one place.

## Online Schema Changes

For huge tables (millions of rows), `ALTER TABLE` can lock for minutes/hours. Alternatives:

### gh-ost (GitHub)
- Triggerless (uses MySQL binlog)
- Throttles on replica lag
- Cancellable

```bash
gh-ost --alter "ADD COLUMN email TEXT" --table=users --execute
```

### pt-online-schema-change (Percona)
- Trigger-based
- Mature
- Wide adoption

```bash
pt-online-schema-change --alter "ADD COLUMN email TEXT" D=mydb,t=users --execute
```

### Postgres
- `ALTER TABLE ... ADD COLUMN x INT;` is fast (metadata-only) — no rewrite
- `... ADD COLUMN x INT NOT NULL DEFAULT 0` would rewrite the entire table in older Postgres; PG 11+ stores the default in metadata
- `... ADD COLUMN x INT GENERATED ALWAYS AS IDENTITY` requires rewrite

For PG, learn what's "fast" vs "slow" by version. PG 11+ added many fast operations.

## Zero-Downtime Migration Patterns

### Expand / Contract
Adding a NOT NULL column:

1. **Expand**: add column NULL-able
   ```sql
   ALTER TABLE users ADD COLUMN email TEXT;
   ```
2. **App reads/writes both**: app version A handles missing email; app version B writes email
3. **Backfill**: batch UPDATE existing rows
   ```sql
   UPDATE users SET email = 'unknown@example.com' WHERE email IS NULL;
   ```
4. **Verify**: all rows have email
5. **Contract**: set NOT NULL
   ```sql
   ALTER TABLE users ALTER COLUMN email SET NOT NULL;
   ```

### Renaming Column
Direct rename = breaks deployed code. Instead:

1. Add new column
2. Write to BOTH old and new in app
3. Backfill old → new
4. Read from new (verify with old)
5. Stop writing old
6. Drop old column

Each step is a separate deploy; all backward-compatible.

### Splitting/Joining Tables
1. New schema in parallel
2. Dual write
3. Backfill historical
4. Switch reads
5. Stop writing old
6. Drop old

## Backward-Compatible Changes

| Change | Backward Compatible? |
|---|---|
| Add nullable column | Yes |
| Drop column | No (app references it) |
| Rename column | No |
| Change column type (e.g., VARCHAR → TEXT) | Usually yes |
| Make column NOT NULL | No (existing NULL rows fail) |
| Add index | Yes |
| Drop index | Yes (if no query depends critically) |
| Add table | Yes |
| Add foreign key | Risky (data validation) |
| Add unique constraint | Risky (duplicates fail) |

## Data Migrations (vs Schema)

Sometimes you need to migrate DATA, not schema:
- Anonymize PII
- Normalize/denormalize
- Move data between tables

Strategy:
- Run as background job (don't block deploy)
- Idempotent + resumable
- Throttled (don't overwhelm DB)
- Monitor + alert

### Tools
- Custom scripts
- Airflow / dbt for analytical migrations
- pgbouncer + pg_partman for partitioning

## Rollback Strategies

### Option 1: Forward-Only
- Never roll back schema
- If migration causes problem, write a new migration to fix
- Most modern teams

### Option 2: Reversible Migrations
- Each migration has down().
- Risky for data migrations (data may be unrecoverable)
- Useful for early-stage / dev environments

## Long-Lived Migrations (Online)

Some migrations take days (huge tables, billions of rows). Pattern:
- Background job updates in batches of 1000-10000
- Sleeps between batches
- Logs progress
- Survives restarts (resumable)
- Monitors replication lag, throttles if rising

```python
batch_size = 10000
last_id = 0
while True:
    rows = update_batch(last_id, batch_size)
    if not rows: break
    last_id = max(r['id'] for r in rows)
    save_progress(last_id)
    if replication_lag() > 30: time.sleep(60)
    else: time.sleep(0.1)
```

## Cross-DB Migrations

Moving from MySQL to Postgres, or 1 DB to another:
- Dump + restore (downtime; simplest)
- Logical replication (Debezium, AWS DMS) — minimal downtime
- Dual-write + verify + cutover

Most complex migrations: years of work.

## Interview Themes

- "Walk through zero-downtime add NOT NULL column"
- "Rename a column — strategy"
- "Online schema change for billion-row table"
- "Compare Flyway, Liquibase, Atlas"
- "MySQL → Postgres migration plan"
