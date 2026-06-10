# L18/C01/T02 — Log Levels

## Learning Objectives

- Use levels correctly
- Avoid common mistakes

## Levels

Standard:
- TRACE
- DEBUG
- INFO
- WARN
- ERROR
- FATAL / CRITICAL

## Definitions

### TRACE
Very fine-grained:
- Function entry/exit
- Loop iterations
- Almost never enabled

### DEBUG
Detailed debugging:
- Variable values
- Branching
- Disabled in prod

### INFO
Normal operation:
- Service started
- Request handled
- Always enabled

### WARN
Recoverable issue:
- Retry succeeded
- Deprecated API used
- Should be investigated

### ERROR
Operation failed:
- Request returned 5xx
- DB query failed (after retries)
- Action required

### FATAL
App crashing:
- Out of memory
- Required config missing
- App terminates

## Common Mistakes

### Wrong Severity
- WARN for normal events (alert fatigue)
- ERROR for expected (404 not an error from server perspective)
- INFO for everything (no signal)

### No Level
Default INFO. Loses signal.

### TRACE / DEBUG in Prod
Too verbose; cost.

## What to Log at Each

### INFO Examples
```
"Service started"
"Request received: GET /users"
"Background job completed"
```

### WARN Examples
```
"Retry needed; succeeded on attempt 2"
"Deprecated endpoint used"
"Cache miss exceeded threshold"
```

### ERROR Examples
```
"DB connection failed after 3 retries"
"Failed to process payment"
"External API timeout"
```

## 4xx Errors

User errors:
- 400: bad request
- 401: unauthorized
- 404: not found

INFO or DEBUG. NOT ERROR from server perspective (client mistake).

## Filter for Real Issues

```promql
{level="error"}
```

Should be rare and actionable.

If always firing: signal-to-noise bad.

## Dynamic Levels

Some frameworks:
- Sample DEBUG (1%)
- Always INFO+

For cost.

## Per-Module Level

```python
logging.getLogger("aws").setLevel(logging.WARN)
logging.getLogger("my_module").setLevel(logging.DEBUG)
```

Noisy libs: WARN.

## Production Default

INFO baseline; bump to DEBUG for incidents:
```bash
LOG_LEVEL=debug ./my-app
```

Live reload preferred.

## Anti-Patterns

### "Logging All The Things"
At INFO; everything. Noise.

### Log + Throw
```python
try:
    ...
except:
    log.error(e)
    raise
```

Caller may log too. Double-log.

Solution: log OR raise.

### Inconsistent Levels
Same event in different code → different levels.

### log.exception() vs log.error()
exception: includes stacktrace.
error: doesn't.

For real exceptions: log.exception or log.error(exc_info=True).

## Volume

Reasonable:
- 1-10 log lines per request
- More for batch jobs
- Less for high-RPS

## Cost

Log storage:
- Standard ~$0.10/GB/month indexed
- Cheap unindexed (Loki)
- High volume: $$$

For: budget by service.

## Sampling

For high-volume DEBUG:
```python
if random.random() < 0.01:
    log.debug("verbose", ...)
```

(See T03.)

## Alternative: Events

Some prefer:
```python
event("user_login", user=...)
```

No level. Filter by event_type.

## When ERROR

- User-impacting
- Requires action
- Unexpected

NOT:
- "Slow query" (use metric)
- "User mistake" (use INFO)
- Periodic warnings

## When WARN

- Should be addressed
- Non-blocking
- Quality issue

## When FATAL

- Process dies
- Service can't recover
- App exit

Rarely. Use ERROR + exit if needed.

## Log Aggregation

Filter by level:
```
{level=~"error|warn"}
```

Or alerts on ERROR rate.

## Best Practices

- INFO default
- ERROR rare + actionable
- WARN for "could be issue"
- DEBUG only on demand
- Sample DEBUG / TRACE
- Per-module override

## Common Mistakes

- Log every variable at INFO
- 4xx as ERROR
- Same event different levels
- TRACE in prod
- No dynamic reload

## Quick Refs

```
TRACE - very fine; never on
DEBUG - debugging; on demand
INFO  - normal ops; always on
WARN  - investigation needed
ERROR - action needed
FATAL - app death
```

## Interview Prep

**Junior**: "Log levels."

**Mid**: "ERROR criteria."

**Senior**: "Level discipline."

## Next Topic

→ [T03 — Sampling Strategies](T03-Sampling-Strategies.md)
