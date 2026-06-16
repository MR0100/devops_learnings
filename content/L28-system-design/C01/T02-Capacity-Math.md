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

L1 cache: 0.5 ns
SSD: 100 µs
Network: 1-100 ms

Web server: ~5k QPS
DB shard: ~10k QPS, 1 TB
```

## Interview Prep

**Junior**: "Estimate the QPS for 1M DAU doing 100 requests a day." — QPS = users × actions / seconds-in-day = 1M × 100 / 86,400 ≈ 1,160 average. Then multiply by ~3 for peak ≈ 3,500 QPS, because traffic isn't flat — you provision for peak, not average.

**Mid**: "How do you estimate storage growth?" — storage = items × size × time. For 100M new records/day at 1 KB each that's 100 GB/day; over 5 years (×1,825) that's ~180 TB. Always separate the daily growth rate from the cumulative total, and apply replication factor on top.

**Senior**: "How do you keep your numbers realistic?" — Anchor to known reference points — a web server does ~5–10k QPS, a DB shard ~10k QPS and ~1 TB, a 1 Gbps NIC moves 125 MB/s — and sanity-check the result against them. If my math says one box serves 10M QPS, the math is wrong. I show my work and commit to round numbers rather than hand-waving.

**Staff**: "Estimate capacity for a URL shortener and use it to drive the design." — 100M shortens/day ≈ 1,160 QPS write; with a 100:1 read:write ratio that's ~116k QPS redirect, so the read path dominates and needs a cache + CDN, the write path doesn't. At ~1 KB/URL, storage grows ~100 GB/day → ~180 TB over 5 years, which exceeds a single node so it's sharded. The estimation isn't a ritual — each number directly picks a component (cache for reads, sharding for storage), which is the point of doing it before designing.

## Next Topic

→ [T03 — The 4 Boxes (Client, App, Data, Infra)](T03-4-Boxes.md)
