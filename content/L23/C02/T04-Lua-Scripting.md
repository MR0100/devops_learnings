# L23/C02/T04 — Redis Lua Scripting

## Learning Objectives

- Write Lua scripts
- Atomic multi-key ops

## Why Lua

Atomic:
- Multiple commands as one
- No race conditions

```
EVAL "return redis.call('GET', KEYS[1])" 1 mykey
```

## Example: Atomic Increment + Check

```lua
local val = redis.call('INCR', KEYS[1])
if val > tonumber(ARGV[1]) then
    redis.call('SET', KEYS[1], 0)
    return 1
end
return 0
```

```
EVAL "..." 1 counter 100
```

For: atomic rate limiting.

## EVALSHA

Cache script:
```
SCRIPT LOAD "script"
# Returns SHA

EVALSHA SHA NUMKEYS KEY... ARG...
```

Faster.

## Rate Limiting

```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('GET', key) or 0
if current + 1 > limit then
    return 0   -- denied
end

redis.call('INCR', key)
redis.call('EXPIRE', key, window)
return 1   -- allowed
```

Atomic; no race.

## Lock Acquire

```lua
if redis.call('SETNX', KEYS[1], ARGV[1]) == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[2])
    return 1
end
return 0
```

For: distributed lock.

## Multi-Key

```lua
local user = redis.call('HGETALL', KEYS[1])
local profile = redis.call('GET', KEYS[2])
return {user, profile}
```

Atomic read across keys.

## Limitations

- Single-threaded (blocks other ops)
- Should be fast
- No network calls

For: < 1 ms ideal.

## Long-Running

```lua
-- Bad: long loop
for i = 1, 1000000 do
    redis.call(...)
end
```

Blocks Redis. Avoid.

## Library

`redis.call` (errors throw).
`redis.pcall` (errors returned).

## Cluster

In cluster:
- All keys must be in same slot
- Use hash tags

```
EVAL "..." 2 {user:1}:profile {user:1}:settings
```

## Redis Functions (7.0+)

Like Lua but:
- Loaded once
- Reusable
- Better libraries

```
FUNCTION LOAD ...
FCALL name NUMKEYS KEY... ARG...
```

For: modern.

## Use Cases

- Atomic operations
- Rate limiting
- Distributed locks
- Conditional sets
- Bulk operations

## Best Practices

- Short scripts (< 1 ms)
- Cache (EVALSHA)
- Same slot for cluster
- Idempotent
- Test thoroughly

## Common Mistakes

- Long-running (blocks)
- Network calls in Lua (no)
- Cross-slot in cluster
- Side effects (not idempotent)

## Quick Refs

```
EVAL script numkeys key... arg...
EVALSHA SHA numkeys key... arg...
SCRIPT LOAD script
SCRIPT FLUSH
SCRIPT EXISTS sha

# 7.0+
FUNCTION LOAD
FCALL name numkeys key... arg...
```

## Interview Prep

**Mid**: "Lua in Redis."

**Senior**: "Atomic ops."

**Staff**: "Distributed locks."

## Next Topic

→ [T05 — Redis Modules](T05-Redis-Modules.md)
