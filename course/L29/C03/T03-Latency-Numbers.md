# L29/C03/T03 — Latency Numbers You Must Know

## Learning Objectives

- Memorize numbers
- Cite in design

## Latency

```
L1 cache:           0.5 ns
Branch mispredict:  5 ns
L2 cache:           7 ns
Mutex lock/unlock:  25 ns
Main memory:        100 ns
Compress 1KB Zippy: 3 µs
1 GB/s network:     10 µs/KB
SSD random read:    150 µs
Round trip same DC: 500 µs
HDD seek:           10 ms
Same continent NW:  50 ms
Cross-continent NW: 150 ms
```

(Jeff Dean's numbers; updated)

## Throughput

- 1 Gbps NIC: 125 MB/s
- 10 Gbps NIC: 1.25 GB/s
- SSD: 1-3 GB/s
- HDD: 100-200 MB/s
- DDR4 RAM: 25 GB/s

## QPS

- Modern web server: 10k-100k QPS
- Modern DB (KV): 100k-1M QPS
- Single Redis: 100k-1M QPS

## Sizes

- 1 KB: small
- 1 MB: image
- 1 GB: video
- 1 TB: backup

- 1 char: 1 byte (ASCII) or 4 (UTF-8 max)
- UUID: 16 bytes
- Timestamp: 8 bytes

## Capacity

- DAU: how many active per day
- MAU: monthly
- QPS = DAU × actions / 86400

## Storage

- Per record: bytes per field × fields
- Per day: records × size
- Per year: × 365

## Cost (Rough)

- EC2: $30-300/mo per instance
- S3: $20/TB/month
- RDS: $50-500/mo
- Bandwidth: $0.05-0.10/GB

## Cite

In design:
- "Network call ~50 ms cross-region"
- "Memory access ~100 ns"
- "SSD random ~150 µs"

For: credibility.

## Best Practices

- Memorize key numbers
- Order-of-magnitude
- Update for modern hardware

## Common Mistakes

- Wrong numbers (sounds amateur)
- Skip math
- Hand-wave

## Quick Refs

```
RAM: 100 ns
SSD: 150 µs
Same DC: 500 µs
Cross-cont: 150 ms

Web server: 10k QPS
DB: 100k-1M QPS
Single host: 100 MB/s NW
```

## Interview Prep

**Mid**: "Latency numbers."

**Senior**: "Cite in design."

**Staff**: "Realistic estimates."

## Next Topic

→ [T04 — Common Patterns at Each Level](T04-Common-Patterns.md)
