# L28/C03/T01 — Idempotency

## Learning Objectives

- Define idempotency and why it underpins safe retries and at-least-once delivery
- Implement idempotency keys, natural idempotency, and dedupe stores correctly
- Reason about idempotency at HTTP, queue, and cross-service boundaries

(Builds on retry mechanics in L25/C05/T05 and the reliability recap in L22/C01/T02.)

## Definition

> An operation is idempotent if performing it N times has the same effect as
> performing it once.

The *effect* is what matters, not the response. Charging a card once and then
returning the cached "already charged" result on retry is idempotent. Charging
twice is not — even if the second call returns the same JSON.

## Why It Matters

Every layer below your code retries:

- **Networks** drop the *response*, not the request — the work happened, but the
  client never heard back and retries → duplicate
- **Message queues** (SQS, Kafka, Pub/Sub) are **at-least-once** by design
- **Load balancers / proxies** retry idempotent methods on connection failure
- **Clients and SDKs** retry 5xx and timeouts automatically

Without idempotency, every one of these turns a transient blip into a double
charge, a duplicate order, or a doubled inventory decrement.

```
client          server
  │ POST /charge ─────────▶ │  processes, debits card
  │   (response lost) ✗     │
  │ (timeout → retry)       │
  │ POST /charge ─────────▶ │  WITHOUT idempotency: charges AGAIN ✗
  │                         │  WITH key: "seen abc-123" → returns prior result ✓
```

## Patterns

### 1. Natural (Idempotent by Construction)
Some operations are idempotent by definition:

- `DELETE /users/42` — gone stays gone; second call still results in "absent"
- `PUT /users/42 {state}` — full overwrite; same body → same end state
- `SET key value` — absolute assignment, not `INCR` (which is *not* idempotent)

Prefer absolute over relative writes (`balance = 100`, not `balance += 10`).

### 2. Idempotency Key
Client generates a unique key per *logical* operation and sends it; server
dedupes on first-write-wins.

```http
POST /charges
Idempotency-Key: 7c1f-ord-42-attempt
Content-Type: application/json

{"amount": 1000, "customer": "c_42"}
```

Server logic:

```python
def charge(key, payload):
    existing = store.get(key)          # atomic read
    if existing:
        return existing.response       # replay — never re-execute
    result = do_charge(payload)
    store.put(key, result, ttl=86400)  # persist before responding
    return result
```

### 3. State Check (Conditional No-Op)
Check current state; short-circuit if already done.

```python
if user.is_active:
    return                # already activated — no-op
activate(user)
```

Cheap, but only safe when the check + write is atomic (see race conditions).

## Race Conditions: The Hard Part

The naive "read key → if missing, do work → write key" has a window where two
concurrent retries both read "missing" and both execute. Close it with an
**atomic insert**:

```sql
-- Unique constraint makes the DB the arbiter
INSERT INTO idempotency_keys (key, status)
VALUES ('abc-123', 'in_progress')
ON CONFLICT (key) DO NOTHING;        -- 2nd request gets 0 rows → wait/replay
```

Pattern: insert key as `in_progress` first, do the work, then update to
`completed` with the response. A concurrent retry that loses the insert race
polls for `completed` instead of re-executing.

## Applying It

### HTTP Methods

| Method  | Idempotent? | Notes                                    |
|---------|-------------|------------------------------------------|
| GET/HEAD| Yes         | Read-only, no side effects               |
| PUT     | Yes (spec)  | Full overwrite                           |
| DELETE  | Yes (spec)  | Absent-after is the same end state       |
| POST    | **No**      | Creates resources → needs an idempotency key |
| PATCH   | Depends     | Idempotent only if the patch is absolute |

Note "idempotent" ≠ "safe": PUT and DELETE *mutate*, but mutating twice equals
mutating once.

### Background Jobs / Queue Consumers
At-least-once delivery means every consumer must dedupe:

```python
def handle(msg):
    if seen.exists(msg.id):     # dedupe on a stable message/business id
        return                  # already processed
    do_work(msg)
    seen.add(msg.id, ttl=...)   # mark AFTER work, atomically
```

Order matters: mark *after* the work, or a crash between mark-and-work silently
drops the message.

### Cross-Service / Distributed
Enforce idempotency **at every boundary**, not just the edge. A retry from
service A to B, and B's own retry to C, each need their own dedupe — propagate
or derive stable keys so the whole chain is replay-safe.

## Storage for Keys

| Store         | Use when                                              |
|---------------|-------------------------------------------------------|
| Redis + TTL   | High throughput, short dedupe window (hours)          |
| DB table + UNIQUE | Need durability + atomic conflict handling        |
| Same row as the resource | Tie key to the object you're mutating       |

Always set a **TTL** sized to your max retry window (Stripe holds keys ~24h).
Keys held forever leak storage; keys expiring too soon re-open the dup window.

## Production Examples

- **Stripe** — `Idempotency-Key` header mandatory on writes; cached response
  replayed for 24h; the canonical reference implementation.
- **AWS SQS FIFO** — `MessageDeduplicationId` dedupes within a 5-minute window.
- **Welcome email** — "send welcome email" can fire twice from a retry; dedupe
  on `(user_id, event_type)` so the user gets exactly one.

## Common Mistakes

- Returning the same response but re-executing the side effect (not idempotent)
- Non-atomic check-then-act → concurrent retries both execute
- Marking a message processed *before* the work completes (crash → data loss)
- Reusing one idempotency key across different logical operations
- No TTL on the dedupe store → unbounded growth, or too-short → dup window reopens
- Relative writes (`INCR`, `+=`) where absolute would be naturally idempotent

## Best Practices

- Make operations idempotent by default; use keys for anything that creates
- Generate one key per logical operation (a stable UUID), never reuse
- Use an atomic insert / `ON CONFLICT` to close the concurrency window
- Persist the key+response *before* returning, mark jobs done *after* work
- Enforce idempotency at every service boundary, not only the public edge
- Test the retry path explicitly — fire the same request twice in CI

## Quick Refs

```
Idempotent      : safe to retry; N calls == 1 call (by effect)
Key             : client-generated UUID per logical op, with TTL
Dedupe          : persist "seen"; atomic insert closes the race
Natural         : DELETE / PUT / absolute SET — idempotent by construction
At-least-once   : every queue consumer MUST dedupe
```

## Interview Prep

**Junior**: "What does idempotent mean?" — Doing the operation N times has the same effect as doing it once, so retries are safe — e.g. DELETE or PUT.

**Mid**: "How do you make POST /charge safe to retry?" — Require an idempotency key; on first call do the work and store key→response, on replay return the stored response without re-charging.

**Senior**: "How do you handle two concurrent retries of the same key?" — Use an atomic `INSERT ... ON CONFLICT DO NOTHING` (or Redis `SET NX`) so exactly one request wins and executes while the loser polls for the completed result, never re-executing.

**Staff**: "Where does idempotency live in a distributed system?" — At every boundary: the public API edge, each queue consumer (at-least-once), and each inter-service hop; you propagate or derive stable keys and prefer absolute writes so the entire retry chain is replay-safe end to end.

## Next Topic

→ [T02 — Backpressure](T02-Backpressure.md)
