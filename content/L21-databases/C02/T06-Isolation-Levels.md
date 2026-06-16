# L21/C02/T06 — Transaction Isolation Levels

## Learning Objectives

- Define the four SQL isolation levels and the read anomalies each one prevents
- Explain dirty read, non-repeatable read, phantom read, and lost update concretely
- Know the real-world defaults: PostgreSQL READ COMMITTED vs InnoDB REPEATABLE READ, and how they actually behave
- Understand how MVCC, gap/next-key locks, and Serializable Snapshot Isolation (SSI) implement these guarantees

## Why Isolation Levels Exist

ACID's "I" is **Isolation**: concurrent transactions should behave *as if* they ran one at a time (serially). True serial execution is slow, so databases offer weaker levels that allow more concurrency in exchange for permitting specific anomalies. Picking a level is choosing **which anomalies you can tolerate** for more throughput.

The SQL standard defines four levels by the anomalies they *forbid*:

| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| READ UNCOMMITTED | possible | possible | possible |
| READ COMMITTED | prevented | possible | possible |
| REPEATABLE READ | prevented | prevented | possible* |
| SERIALIZABLE | prevented | prevented | prevented |

\* The standard *allows* phantoms at REPEATABLE READ, but real engines differ — see below.

## The Anomalies

### Dirty Read
You read a row another transaction wrote but **has not committed**. If that transaction rolls back, you acted on data that never existed.

```
T1: UPDATE accounts SET balance = 0 WHERE id = 1;   -- not committed
T2: SELECT balance FROM accounts WHERE id = 1;       -- sees 0 (dirty)
T1: ROLLBACK;                                         -- the 0 never happened
```

### Non-Repeatable Read
You read the **same row twice** in one transaction and get **different values**, because another transaction committed an update in between.

```
T1: SELECT balance FROM accounts WHERE id = 1;   -- 100
T2: UPDATE accounts SET balance = 50 WHERE id = 1; COMMIT;
T1: SELECT balance FROM accounts WHERE id = 1;   -- 50  (changed under you)
```

### Phantom Read
You run the **same range query twice** and a different *set of rows* comes back, because another transaction inserted/deleted rows matching your predicate.

```
T1: SELECT count(*) FROM orders WHERE total > 100;   -- 10 rows
T2: INSERT INTO orders (total) VALUES (200); COMMIT;
T1: SELECT count(*) FROM orders WHERE total > 100;   -- 11 rows  (a phantom)
```

Phantoms differ from non-repeatable reads: non-repeatable is about an *existing row changing*; a phantom is about the *set of matching rows changing*.

### Lost Update
Two transactions read the same value, both compute a new value from it, and both write — the second overwrites the first silently.

```
T1: read counter = 10
T2: read counter = 10
T1: write 11; COMMIT
T2: write 11; COMMIT     -- should be 12; one increment is lost
```

Lost updates are not in the original SQL table but matter a lot in practice. Fixes: `SELECT ... FOR UPDATE` (pessimistic lock), an atomic `UPDATE counter = counter + 1`, or optimistic concurrency with a version column.

## Real-World Defaults

The standard describes behavior; engines implement it differently — mostly via **MVCC** (snapshots), not locking reads.

### PostgreSQL — default READ COMMITTED
- Each **statement** sees a fresh snapshot of committed data. So within one transaction, two queries can see different data (non-repeatable reads and phantoms are allowed).
- `REPEATABLE READ` in Postgres uses a **single transaction-level snapshot** taken at the first query — and because of MVCC it *also* prevents phantoms (stronger than the standard requires). Conflicting writes raise a serialization error you must retry.
- `SERIALIZABLE` adds **SSI** on top (see below).

### MySQL/InnoDB — default REPEATABLE READ
- A consistent snapshot is taken at the transaction's first read; plain `SELECT`s are repeatable for the whole transaction.
- InnoDB prevents phantoms under REPEATABLE READ using **next-key locks** (record lock + gap lock) on index ranges touched by locking reads — so it is stronger than the standard here too.
- **Gap locks** lock the gaps between index records so no one can insert into a scanned range. They are a common source of deadlocks; switching to READ COMMITTED disables most gap locking (and requires `binlog_format=ROW`).

Key interview point: **Postgres defaults to READ COMMITTED, InnoDB defaults to REPEATABLE READ** — and both are stricter about phantoms than the SQL standard mandates.

## Serializable: Two Implementations

SERIALIZABLE guarantees the result equals *some* serial order. Two ways to get there:

- **Strict two-phase locking (S2PL)** — take read+write locks and hold them to commit (classic; InnoDB SERIALIZABLE turns plain `SELECT` into `SELECT ... LOCK IN SHARE MODE`). Correct but lock-heavy; deadlocks and contention.
- **Serializable Snapshot Isolation (SSI)** — PostgreSQL's approach. Run optimistically on snapshots (like REPEATABLE READ), but track read/write dependencies between concurrent transactions; if a *dangerous structure* that could break serializability forms, the database aborts one transaction with a serialization failure. No read locks, high concurrency — but the app **must retry** aborted transactions.

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- ... work ...
COMMIT;   -- may raise: ERROR 40001 could not serialize access; retry the whole tx
```

## Setting the Level

```sql
-- PostgreSQL / standard SQL
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- or per session:
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- MySQL / InnoDB
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT @@transaction_isolation;
```

## Choosing a Level

- **READ COMMITTED** — the right default for most OLTP. Cheap, good concurrency; handle lost updates explicitly with `FOR UPDATE` or atomic updates.
- **REPEATABLE READ** — when a transaction must see a stable snapshot across multiple reads (reports, multi-step reads). On Postgres, be ready to retry serialization errors.
- **SERIALIZABLE** — when correctness under concurrency is non-negotiable and you can't reason about every race (financial invariants, "no double booking"). Always pair with **retry-on-40001** logic.

## Common Mistakes

- Assuming "REPEATABLE READ" means the same thing everywhere — Postgres and InnoDB both go beyond the standard, and differently.
- Forgetting lost updates: READ COMMITTED does **not** stop two read-modify-write transactions from clobbering each other. Use `FOR UPDATE` or atomic SQL.
- Using SERIALIZABLE/SSI without retry logic — serialization failures are normal at that level, not bugs.
- Reaching for SERIALIZABLE to "be safe" and then drowning in deadlocks/aborts when an atomic UPDATE or a unique constraint would have done.
- Mixing `binlog_format=STATEMENT` with READ COMMITTED on InnoDB (unsafe; needs ROW).

## Best Practices

- Default to READ COMMITTED; escalate per-transaction only where you need a stable snapshot or true serializability.
- Make every transaction at SERIALIZABLE/REPEATABLE READ **idempotent and retryable**; wrap in a retry loop on error 40001.
- Prevent lost updates with `SELECT ... FOR UPDATE`, atomic `col = col + 1`, or a version column — don't rely on isolation alone.
- Keep transactions short to reduce lock/gap-lock contention and snapshot bloat (long transactions also block Postgres autovacuum).
- Enforce invariants with constraints (unique, check, exclusion) where possible — cheaper and clearer than isolation gymnastics.

## Quick Refs

```sql
-- Inspect
SELECT @@transaction_isolation;                       -- MySQL
SHOW default_transaction_isolation;                   -- PostgreSQL

-- Set
SET TRANSACTION ISOLATION LEVEL { READ UNCOMMITTED | READ COMMITTED
                                | REPEATABLE READ | SERIALIZABLE };

-- Prevent lost update
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- pessimistic
UPDATE counters SET n = n + 1 WHERE id = 1;            -- atomic
```

| | Postgres default | InnoDB default |
|---|---|---|
| Level | READ COMMITTED | REPEATABLE READ |
| Phantoms at RR | prevented (MVCC snapshot) | prevented (next-key locks) |
| SERIALIZABLE via | SSI (optimistic, retry) | S2PL (locking) |

## Interview Prep

**Junior**: "What are the four isolation levels?" — READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE — ordered weakest to strongest. Each forbids more anomalies: dirty reads, then non-repeatable reads, then phantoms.

**Mid**: "Difference between a non-repeatable read and a phantom?" — A non-repeatable read is the *same row* returning a different value on a second read (another tx updated it). A phantom is the *set of rows* matching a predicate changing (another tx inserted/deleted), so a range query returns a different count. REPEATABLE READ stops the first; SERIALIZABLE stops both.

**Senior**: "What does Postgres default to vs InnoDB, and why does it matter?" — Postgres defaults to READ COMMITTED (fresh snapshot per statement); InnoDB defaults to REPEATABLE READ (one snapshot per transaction). Both exceed the standard on phantoms — Postgres via MVCC snapshots, InnoDB via next-key/gap locks. So code ported between them can behave differently around repeated reads and range locking.

**Staff**: "How does SERIALIZABLE work without crushing throughput?" — Postgres uses SSI: transactions run optimistically on snapshots, the engine tracks read/write dependency edges, and aborts one transaction (error 40001) only when a dangerous cycle could violate serializability. No read locks, so high concurrency — at the cost of mandatory retry logic. The lock-based alternative (S2PL) is correct but serializes contended access and deadlocks more. You also still defend invariants with constraints and atomic updates rather than relying solely on the level.

## Next Topic

→ [T07 — Indexing Strategies](T07-Indexing.md)
