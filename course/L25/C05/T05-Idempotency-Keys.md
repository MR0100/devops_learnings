# L25/C05/T05 — Idempotency Keys

## Learning Objectives

- Use idempotency keys
- Safe retries for writes

## Idempotency

Same operation N times = same result.

## Why

Network may retry:
- Request times out
- Was it processed?
- Retry: duplicate?

For: dedupe.

## Idempotency Key

Client generates unique ID:
```
Idempotency-Key: <UUID>
```

Server:
- Has key been seen? Return cached result.
- New: process; cache result.

## Stripe API

```python
stripe.PaymentIntent.create(
    amount=2000,
    currency='usd',
    idempotency_key='unique-key-123'
)
```

If retry with same key: same result; no double charge.

## Server Implementation

```python
def create_payment(req):
    key = req.headers['Idempotency-Key']
    cached = redis.get(f'idempotency:{key}')
    if cached:
        return cached
    
    result = actually_create_payment(req)
    redis.set(f'idempotency:{key}', result, ttl=86400)
    return result
```

## Considerations

- Storage: key + result
- TTL: 24-48 hr typical
- Atomic check + set

## SQL Approach

```sql
INSERT INTO idempotency_keys (key, result)
VALUES (?, ?)
ON CONFLICT (key) DO NOTHING
RETURNING result;
```

If conflict: return cached.

## Generate Keys

Client:
```python
import uuid
key = str(uuid.uuid4())
```

For: unique per logical request.

## Reuse on Retry

Same key for retries:
```python
def call_api(key):
    return requests.post(url, headers={'Idempotency-Key': key})

key = uuid()
for attempt in retries:
    result = call_api(key)   # same key
```

Server dedupes.

## Idempotent by Nature

Some operations idempotent inherently:
- SET (overwrite)
- DELETE (already gone)
- PUT (replace)

POST: usually not.

For POST: idempotency key.

## Distributed Locks

Alternative:
```python
with redis_lock(key):
    if processed(key):
        return cached
    process(key)
    cache(key)
```

Similar idea.

## Idempotent Workers

For background workers:
```python
def handle_message(msg):
    if processed(msg.id):
        return
    process(msg)
    mark_processed(msg.id)
```

For: at-least-once delivery.

## Best Practices

- Idempotency keys for writes
- TTL ≥ retry window
- Persistent storage (Redis with persist; DB)
- Document API contract

## Common Mistakes

- No idempotency (duplicates)
- TTL too short (real retries miss)
- Race conditions (non-atomic check+set)
- Reuse key for different operation

## Real Examples

### Stripe
Mandatory idempotency keys.

### AWS DynamoDB
ConditionExpression for atomic check.

### Many APIs
Standard pattern.

## Quick Refs

```
Header: Idempotency-Key: <UUID>

Server:
  if seen(key): return cached
  result = process()
  cache(key, result)
  return result

Client:
  key = uuid()
  for retry: use same key
```

## Interview Prep

**Mid**: "Idempotency."

**Senior**: "Implement keys."

**Staff**: "Distributed dedup."

## Next Topic

→ Move to [L26 — FinOps & Cloud Cost Optimization](../../L26/README.md)
