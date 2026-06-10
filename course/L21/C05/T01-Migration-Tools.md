# L21/C05/T01 — Schema Migration Tools (Flyway, Liquibase, Atlas)

## Learning Objectives

- Manage DB schema
- Choose tool

## Why

Schema changes:
- Versioned
- Repeatable
- Rolled back if possible

For: track + automate.

## Flyway

Java-based:
```
db/migration/
  V1__create_users.sql
  V2__add_email_index.sql
  V3__create_orders.sql
```

```bash
flyway migrate -url=jdbc:postgresql://... -user=X -password=Y
```

Tracks in `flyway_schema_history` table.

## Liquibase

XML/YAML/SQL/JSON:
```yaml
databaseChangeLog:
  - changeSet:
      id: 1
      author: alice
      changes:
        - createTable:
            tableName: users
            columns:
              - column: {name: id, type: bigint}
              - column: {name: email, type: varchar(255)}
```

```bash
liquibase update
```

## Atlas (HashiCorp/Ariga)

Modern; declarative:
```hcl
table "users" {
  schema = schema.public
  column "id" {
    type = bigint
  }
}
```

```bash
atlas migrate apply
```

Diff-based:
- Detects desired vs actual
- Generates migration

## sqitch

Plan-based:
- Dependencies
- Verify scripts
- Revert scripts

## Per-Language Tools

- Rails: Active Record Migrations
- Django: makemigrations
- Alembic (Python / SQLAlchemy)
- Knex (Node)
- Goose (Go)

## CI Integration

```yaml
- name: Apply migrations
  run: flyway migrate
  env:
    FLYWAY_URL: jdbc:postgresql://...
```

Run before app deploy.

## Down Migrations

Some tools support reverting:
```sql
-- V1__create_users.sql
CREATE TABLE users (...);

-- V1__create_users.sql.undo (Flyway pro)
DROP TABLE users;
```

Caution: data loss.

## Reversibility

Some changes:
- Reversible (rename column → rename back)
- Irreversible (drop column → lost data)

For: prefer additive.

## Expand-Contract

Avoid breaking changes:
1. Add new column
2. Migrate data
3. Switch app
4. Drop old column

Multi-deploy.

For: zero-downtime.

## Version Control

Migrations in Git:
- Reviewed
- History
- Audit

## Testing

- Apply to test DB
- Run app tests
- Verify data integrity

## Drift Detection

```bash
atlas migrate diff
```

Compare DB vs migrations.

## Rolling Out

```
Dev DB: apply
Staging: apply (after dev)
Prod: apply (after staging)
```

Phased.

## Online Schema Change

For huge tables:
- pt-online-schema-change
- gh-ost

(See T02.)

## Best Practices

- Versioned
- Reviewed
- Tested
- Backward compatible (expand-contract)
- Idempotent

## Common Mistakes

- Manual SQL in prod (drift)
- Destructive changes (data loss)
- Long migrations (lock)
- Forget rollback plan

## Quick Refs

```bash
# Flyway
flyway migrate / info / validate / repair

# Liquibase
liquibase update / status / rollback

# Atlas
atlas migrate apply / diff / status

# Alembic
alembic upgrade head / downgrade -1
```

## Interview Prep

**Mid**: "Schema migrations."

**Senior**: "Zero-downtime."

**Staff**: "Migration strategy."

## Next Topic

→ [T02 — Online Schema Changes (gh-ost, pt-online-schema-change)](T02-Online-Schema.md)
