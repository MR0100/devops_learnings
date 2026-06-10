# L28/C03/T01 — Idempotency

## Learning Objectives

- Design idempotent operations
- Safe retries

(Covered L22/C01/T02 and L25/C05/T05.)

## Definition

Same operation N times = same result.

## Why

- Retries safe
- Duplicates handled
- Network failures OK

## Patterns

### Idempotency Key
Client sends unique ID. Server dedupes.

### Idempotent by Nature
DELETE (gone is gone).
PUT (overwrite).

### State Check
```python
if user.is_active:
    return  # already
activate(user)
```

For: already-done check.

## Apply

### HTTP
- GET, HEAD, OPTIONS: idempotent
- PUT, DELETE: idempotent (per spec)
- POST: usually not

For POST: idempotency key.

### Background Jobs
Worker may run twice:
```python
def handle(msg):
    if processed(msg.id):
        return
    do_work(msg)
    mark_processed(msg.id)
```

### Distributed
Cross-service:
- Idempotency at boundaries

## Examples

### Stripe
Mandatory idempotency keys.

### Email
- "Send welcome email" can run twice
- Dedupe by user_id + event

## Best Practices

- Idempotent by default
- Key for non-idempotent
- Track processed
- Test retry scenarios

## Quick Refs

```
Idempotent: safe to retry
Key: client-generated UUID
Dedupe: persist seen
```

## Interview Prep

**Mid**: "Idempotency."

**Senior**: "Distributed."

## Next Topic

→ [T02 — Backpressure](T02-Backpressure.md)
