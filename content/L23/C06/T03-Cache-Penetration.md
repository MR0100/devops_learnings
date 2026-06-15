# L23/C06/T03 — Cache Penetration

## Learning Objectives

- Prevent penetration
- Bloom filters

## Cache Penetration

Lookups for non-existent keys:
- Cache miss (correctly)
- DB miss
- Every lookup hits DB
- No cache benefit

## Attack Vector

Attacker queries:
- /api/user/random-string
- /api/user/another-random
- Each: DB miss
- DB overwhelmed

## Mitigations

### Negative Cache

```python
val = cache.get(key)
if val == NOT_FOUND:
    return None
if val is None:
    val = db.fetch(key)
    cache.set(key, val or NOT_FOUND, ttl=60)
return val
```

Even missing: cache for short.

## Bloom Filter

Probabilistic membership:
- "Is key X possibly in DB?"
- False positives OK (just check DB)
- No false negatives

```python
if not bloom.contains(key):
    return None  # definitely not in DB
val = cache.get(key) or db.fetch(key)
```

## Update Bloom

When item added:
```python
db.insert(...)
bloom.add(key)
```

When deleted:
- Bloom can't remove
- Periodic rebuild
- Or use Cuckoo filter (removable)

## RedisBloom

```
BF.ADD users alice
BF.EXISTS users alice    # true
BF.EXISTS users random   # false (probably)
```

Built-in. Use for penetration prevention.

## Cuckoo Filter

Like Bloom but supports delete:
```
CF.ADD seen alice
CF.DEL seen alice
```

## Rate Limit

Per-IP:
```python
key = f"req:{ip}"
count = redis.incr(key)
redis.expire(key, 60)
if count > 100:
    return "Rate limited"
```

For: throttle attackers.

## Captcha

For repeated misses:
- Suspicious
- Challenge

For: confirm human.

## Validation

```python
if not is_valid_user_id(user_id):
    return error
```

Don't query DB for impossible IDs.

For: cheap rejection.

## Real Attack

Malicious script:
```bash
for i in 1..1000000:
    curl /api/user/random-$i
```

Without protection: DB hammered.

## Cost

- Bloom filter: KB-MB memory
- Cheap; massive benefit

## Best Practices

- Bloom filter for existence check
- Negative caching for short TTL
- Rate limiting per IP
- Input validation
- Monitor miss rate

## Common Mistakes

- No negative cache
- Wide-open API
- No rate limit
- Skip Bloom for small dataset (still valuable)

## Quick Refs

```python
# Negative
cache.set(key, NOT_FOUND, ttl=60)

# Bloom (Redis)
BF.RESERVE / ADD / EXISTS

# Rate limit
redis.incr / expire
```

## Interview Prep

**Mid**: "Cache penetration."

**Senior**: "Bloom filter."

**Staff**: "DB protection."

## Next Topic

→ Move to [L24 — Production Networking](../../L24/README.md)
