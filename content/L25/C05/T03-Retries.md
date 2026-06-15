# L25/C05/T03 — Retries with Backoff & Jitter

## Learning Objectives

- Smart retry
- Avoid retry storms

## Why Retry

Transient failures:
- Network blip
- Server restart
- Throttled

For: succeed eventually.

## Why Smart

Naive retry:
- All clients retry immediately
- Server overwhelmed
- Thundering herd

## Exponential Backoff

```
Retry 1: 1 sec
Retry 2: 2 sec
Retry 3: 4 sec
Retry 4: 8 sec
```

For: spread retries.

## Jitter

Random:
```python
delay = base * (2 ** attempt) + random.uniform(0, jitter)
```

For: avoid lockstep retries.

## Full Jitter

```python
delay = random.uniform(0, min(cap, base * 2 ** attempt))
```

For: maximum spread.

## Equal Jitter

```python
temp = min(cap, base * 2 ** attempt)
delay = temp / 2 + random.uniform(0, temp / 2)
```

## Decorrelated Jitter

```python
prev = base
def next():
    nonlocal prev
    prev = random.uniform(base, prev * 3)
    return min(prev, cap)
```

For: AWS pattern.

## Max Retries

```python
max_retries = 3
```

After: fail.

For: bound total time.

## Total Timeout

```python
total_timeout = 30   # seconds
```

Stop retrying after.

For: bounded user wait.

## Only Idempotent

Retry only safe operations:
- GET: retry
- PUT (idempotent): retry
- POST: caution (might create duplicates)

For: avoid double-action.

## Idempotency Keys

(See T05.)

```python
headers['Idempotency-Key'] = uuid()
```

Server dedupes.

For: retry-safe writes.

## Retry-After Header

Server tells:
```
Retry-After: 30
```

Client waits.

For: respect server.

## Examples

### AWS SDK
Built-in retry with decorrelated jitter.

### Stripe API
Idempotency keys + retry.

### Most clients
Configurable retry.

## Code

```python
import time
import random

def retry_with_backoff(fn, max_retries=3, base=1, cap=60):
    for attempt in range(max_retries):
        try:
            return fn()
        except RetryableError:
            if attempt == max_retries - 1:
                raise
            delay = random.uniform(0, min(cap, base * 2 ** attempt))
            time.sleep(delay)
```

## What to Retry

- 5xx (server errors)
- 429 (throttled)
- Network errors
- Timeouts

NOT:
- 4xx (client errors)
- 401 / 403 (auth)
- 404 (not found)

## Library

- Tenacity (Python)
- backoff (Python)
- Polly (.NET)
- Resilience4j (Java)
- AWS SDK retry

## Best Practices

- Exponential backoff
- Jitter
- Max retries (3-5)
- Total timeout
- Idempotency for writes
- Retry only retryable

## Common Mistakes

- Retry forever (eventually success not viable)
- No jitter (sync retries)
- Retry 4xx (waste)
- No idempotency (duplicates)
- Naive exponential without cap

## Quick Refs

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter())
def call():
    ...

# AWS SDK
client = boto3.client('s3', config=Config(retries={'mode': 'adaptive', 'max_attempts': 5}))
```

## Interview Prep

**Mid**: "Retry with backoff."

**Senior**: "Jitter."

**Staff**: "Avoid retry storms."

## Next Topic

→ [T04 — Timeouts](T04-Timeouts.md)
