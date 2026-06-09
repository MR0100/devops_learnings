# L03/C02/T04 — TCP Flow Control, Congestion Control, Slow Start

## Learning Objectives

- Distinguish flow control from congestion control
- Understand slow start, AIMD, fast recovery
- Compare CUBIC, BBR, Reno

## Flow Control vs Congestion Control

- **Flow control**: prevent sender from overwhelming RECEIVER
- **Congestion control**: prevent sender from overwhelming NETWORK

Both regulate sending rate; for different reasons.

## Flow Control: Receive Window (rwnd)

Receiver advertises buffer space in TCP header.
- Sender can't send more than `rwnd` unacked bytes
- Receiver shrinks `rwnd` when buffer fills
- Sender pauses; reads catch up; window opens

If receiver app reads slowly, sender naturally slows. Backpressure.

## Window Scaling

Standard TCP window is 16-bit (max 65535). For high-BDP paths, need bigger. Window scaling option multiplies window by 2^N.

Modern TCPs negotiate this in handshake.

## Bandwidth-Delay Product (BDP)

```
BDP = bandwidth × RTT
```

For 1 Gbps × 100ms RTT:
```
1,000,000,000 bps / 8 = 125,000,000 B/s
125,000,000 × 0.1 = 12,500,000 bytes = 12.5 MB
```

To saturate the link, sender needs 12.5 MB unacked. If TCP buffers (rmem/wmem) smaller, you can't saturate.

Tune:
```bash
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_rmem='4096 87380 16777216'
sysctl -w net.ipv4.tcp_wmem='4096 65536 16777216'
```

## Congestion Control: cwnd

Sender maintains a "congestion window" (`cwnd`). Effective send window = min(rwnd, cwnd).

cwnd grows on success, shrinks on loss.

## Slow Start

Start `cwnd = 1` (or 10 in modern TCP).
Each ACK doubles cwnd: 1, 2, 4, 8, ... (exponential).

Continues until:
- `cwnd` reaches `ssthresh` (slow start threshold)
- Loss detected

## Congestion Avoidance (AIMD)

After slow start: linear growth.

**Additive Increase**: cwnd += 1 per RTT
**Multiplicative Decrease**: on loss, cwnd /= 2

This is the classic AIMD pattern. Fair across competing flows.

## Fast Retransmit / Recovery

If sender gets 3 duplicate ACKs (receiver got out-of-order data):
- Retransmit the missing segment without waiting for timeout
- Cut cwnd in half, but continue from there (don't slow-start)

This is "fast recovery."

## Modern Algorithms

### NewReno (default historically)
- AIMD with fast recovery
- Conservative; older

### CUBIC (Linux default since 2006)
- cwnd grows cubically (faster on high-BDP paths)
- Recovers from loss faster than Reno
- Standard for most workloads

### BBR (Google, 2016+)
- **Bandwidth × RTT** model
- Estimates available bandwidth and minimum RTT directly
- Avoids loss-based signaling
- Dramatically better on lossy paths (Wi-Fi, transcontinental)
- Used by YouTube and many CDNs

```bash
# Check current
sysctl net.ipv4.tcp_congestion_control

# Available
sysctl net.ipv4.tcp_available_congestion_control

# Switch to BBR
sysctl -w net.ipv4.tcp_congestion_control=bbr
```

### Other
- **Vegas** — delay-based
- **CDG** — delay + loss
- **DCTCP** — for data center (uses ECN)
- **BBRv2 / BBRv3** — refined BBR

## Loss Detection

- **Timeout (RTO)**: no ACK for a while → assume lost, retransmit, cwnd → 1 (slow start)
- **3 duplicate ACKs**: fast retransmit
- **Selective ACK (SACK)**: receiver indicates exactly what's missing

## ECN (Explicit Congestion Notification)

Routers mark packets when nearing congestion (instead of dropping).
- Sender slows down
- Avoids actual loss
- Requires both ends + path support

DCTCP relies heavily on ECN in data centers.

## Why CUBIC vs BBR Matters

| | CUBIC | BBR |
|---|---|---|
| Trigger to slow | Loss | Bandwidth/RTT estimation |
| High-loss paths | Slow | Fast |
| Bufferbloat | Causes | Doesn't (bounds queue) |
| Fairness with other CUBIC flows | Yes | Aggressive (BBR may "win" against CUBIC) |
| Default | Linux | Optional (sysctl change) |

For modern long-distance / mobile / lossy networks: BBR is often dramatically better.

## Buffer Bloat

Large buffers in network = high latency under load.
- Buffer fills, packets queue, RTT grows
- Loss-based CC keeps sending until loss → bloated queue
- BBR avoids by detecting bandwidth, not loss

## Tuning Checklist

For high-throughput cross-region (e.g., S3 transfers):
- Window scaling enabled
- TCP buffers sized for BDP
- BBR congestion control
- MTU 9000 if path supports
- Multi-stream transfers (parallel TCP)

## Interview Prep

**Mid**: "Flow control vs congestion control?"

**Senior**: "Slow start — how does it work?"

**Staff**: "Why is BBR better than CUBIC on lossy paths?"

## Next Topic

→ [T05 — UDP and When to Use It](T05-UDP.md)
