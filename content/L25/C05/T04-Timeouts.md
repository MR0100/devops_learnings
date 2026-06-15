# L25/C05/T04 — Timeouts (Done Right)

## Learning Objectives

- Set proper timeouts
- Avoid hangs

## Why

Without timeout:
- Slow dependency hangs
- Threads stuck
- Cascading failure

## Levels

- Connect timeout
- Read timeout
- Total timeout

## Connect Timeout

Time to establish:
- TCP handshake
- Few seconds (1-5)

## Read Timeout

Time waiting for data:
- After connected
- Depends on operation

## Total Timeout

Overall budget:
- Including retries
- < user expectation

## HTTP Client

```python
import requests

response = requests.get(
    url,
    timeout=(5, 30)   # (connect, read)
)
```

## Connection Pool

```python
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=100,
)
session.mount('http://', adapter)
```

## gRPC

```python
stub.MyMethod(req, timeout=5.0)
```

## DB

```python
psycopg2.connect(connect_timeout=5)
```

```
options=-c statement_timeout=30000   # 30 sec
```

## Layered

User waits 10s max:
- Frontend: 10s total
- Backend call: 5s
- DB: 2s

Each layer: less than parent.

## Distributed Timeouts

Propagate deadline:
```python
deadline = time.time() + 5
headers['X-Deadline'] = str(deadline)
```

Backend:
```python
remaining = float(headers['X-Deadline']) - time.time()
db.query(timeout=remaining)
```

For: don't waste.

## gRPC Deadlines

Built-in:
```python
stub.MyMethod(req, timeout=5)
# Propagated automatically
```

## Hedging

```python
# Send 2 parallel; use first
```

For: tail latency.

## Service Mesh

```yaml
http:
- route: ...
  timeout: 5s
```

Per-route timeout.

## Common Timeouts

- HTTP API: 5-30s
- DB query: 5-30s
- Cache: 100ms-1s
- External API: 10s
- Background job: minutes-hours

## Best Practices

- Always set (don't default infinite)
- Connect + read separate
- Layered (less inner)
- Propagate deadline
- Tuned per operation

## Common Mistakes

- No timeout (hangs forever)
- Same timeout everywhere
- Connect timeout too generous
- Don't propagate

## Examples

### requests Default
No timeout. Set explicitly!

### Java
URLConnection default infinite.

### Always Set
```python
timeout=(5, 30)
```

## Quick Refs

```python
requests.get(url, timeout=(connect, read))
grpc.call(req, timeout=5)
db_conn.query(timeout=30)
ctx, cancel = context.WithTimeout(parent, 5*time.Second)  # Go
```

## Interview Prep

**Mid**: "Timeouts."

**Senior**: "Layered timeouts."

**Staff**: "Distributed deadlines."

## Next Topic

→ [T05 — Idempotency Keys](T05-Idempotency-Keys.md)
