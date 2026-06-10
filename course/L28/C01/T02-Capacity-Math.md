# L28/C01/T02 — Capacity Estimation Math

## Learning Objectives

- Estimate capacity
- Back-of-envelope

## Common Numbers

Latency:
- L1 cache: 0.5 ns
- L2 cache: 7 ns
- RAM: 100 ns
- SSD: 100 µs
- HDD: 10 ms
- Network: 0.5 ms (same DC) - 100 ms (cross-cont)

Throughput:
- 1 Gbps NIC: 125 MB/s
- SSD: 1 GB/s
- HTTP server: 10k-100k QPS

## Formulas

### Requests
```
QPS = users × requests/user/day / seconds/day
```

For 1M DAU, 100 req/user/day:
```
QPS = 1M × 100 / 86400 = ~1158 QPS
```

Peak: 2-3x average:
```
Peak QPS = ~3000
```

### Storage
```
storage = items × size × time
```

For 1B records × 1 KB × 5 years:
```
1B × 1 KB × 5 = 5 TB
```

### Bandwidth
```
bandwidth = QPS × bytes/req
```

For 1000 QPS × 10 KB/req:
```
bandwidth = 10 MB/s
```

## Scale Factors

- 86400 sec/day
- 1k = 10^3
- 1M = 10^6
- 1B = 10^9
- 1T = 10^12

## Interview Example

URL Shortener:
- 100M URLs/day → 1158 QPS shorten
- Read:Write 100:1 → 116k QPS redirect
- Each URL ~1 KB → 100 GB/day storage growth
- 5 yr retention → 180 TB total

## Cache Sizing

- 20% of items get 80% of traffic
- Cache hot 20%
- Memory needed: 20% × total

## Compute

- 1 web server: 5k QPS typical
- For 100k QPS: 20+ servers
- Add buffer for HA: 30 servers

## DB Sharding

- 1 shard: 10k QPS, 1 TB
- For 100k QPS: 10 shards

## Sanity Check

Don't say:
- 10B QPS (impossible)
- 1 KB DB (silly)

Verify with experience.

## Best Practices

- Practice common formulas
- Sanity-check
- Show work
- Commit to numbers

## Common Mistakes

- Math errors (units)
- Unrealistic numbers
- Hand-wave (no math)

## Quick Refs

```
QPS = users × actions / 86400
Peak = avg × 3
Storage = items × size × time

L1 cache: 1ns
SSD: 100 µs
Network: 1-100 ms

Web server: ~5k QPS
DB shard: ~10k QPS, 1 TB
```

## Interview Prep

**Junior**: "Estimate QPS."

**Mid**: "Storage growth."

**Senior**: "Realistic numbers."

**Staff**: "Scale math."

## Next Topic

→ [T03 — The 4 Boxes (Client, App, Data, Infra)](T03-4-Boxes.md)
