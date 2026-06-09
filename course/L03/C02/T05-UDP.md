# L03/C02/T05 — UDP and When to Use It

## Learning Objectives

- Understand UDP semantics
- Identify use cases where UDP wins
- Build reliability on top of UDP when needed

## UDP Basics

User Datagram Protocol. Connectionless, unreliable, unordered.

```
Send a datagram. It arrives, or it doesn't. No retries.
```

UDP header: 8 bytes (source port, dest port, length, checksum). Compare to TCP's 20+.

## TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Connection | Yes (handshake) | No |
| Reliability | Yes (retries) | No |
| Ordering | Yes | No |
| Flow control | Yes | No |
| Congestion control | Yes | No |
| Header size | 20+ bytes | 8 bytes |
| Overhead | Higher | Lower |
| Use | Web, SSH, most apps | DNS, NTP, video, gaming, VPN, QUIC |

## When UDP Wins

### Low Latency
TCP handshake = 1 RTT before data. UDP = 0 RTT. Critical for:
- DNS queries (sub-millisecond)
- Real-time gaming
- VoIP

### Many Small Packets
Tiny payloads with TCP have huge overhead ratio. UDP minimal.

### Many Recipients
Multicast / broadcast natural in UDP; TCP is point-to-point only.

### Application-Level Reliability
If you have custom retry/ordering logic, TCP's adds duplicate work.

### Tolerant of Loss
Video: losing a frame is better than waiting for retransmission (drops freshness).

## Use Cases

### DNS (port 53)
- Most queries fit in one UDP packet (< 512 bytes)
- DNS-over-TCP for larger
- DNS-over-HTTPS (DoH) for privacy
- DNS-over-QUIC (DoQ) emerging

### NTP (port 123)
- Time sync
- Single packet exchange
- Slight delay tolerable

### DHCP (ports 67, 68)
- Broadcast required (UDP supports)
- Negotiation phase

### Video / Audio Streaming
- Real-time: WebRTC, SIP, RTP
- Late packet is useless → drop, don't retransmit
- Live streaming sometimes UDP (especially low-latency)

### Gaming
- Player movement updates
- Old data is stale; new data more useful than retransmits
- Custom reliability for critical events (purchases, account changes)

### VPN / Tunnels
- WireGuard, OpenVPN UDP mode
- IPSec ESP

### QUIC (becoming HUGE)
- Built on UDP
- Reliable + ordered streams above UDP
- Foundation for HTTP/3
- Avoids TCP's HoL blocking

### Metric Push
- StatsD, Datadog agent (lossy is OK; metrics are statistical anyway)

## Building Reliability on UDP

When you need some reliability but not full TCP:
- Acknowledgements (custom ACK)
- Sequence numbers
- Selective retransmission
- Fragmentation reassembly

QUIC does this above UDP, giving best of both worlds.

## UDP Flood Attacks

UDP has no handshake → no validation. Easy to spoof.
- Amplification attacks: small spoofed query → large response to victim
- DNS amplification: 50× amplification
- NTP amplification: 500×
- Memcached UDP: 50,000× (largest DDoS attacks ever)

Mitigations:
- Disable UDP on services that don't need it
- Rate limit UDP responses
- Source IP validation (BCP 38)

## UDP Socket Programming

```python
import socket

# Server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 5000))
while True:
    data, addr = s.recvfrom(4096)
    print(f"from {addr}: {data}")
    s.sendto(b"reply", addr)
```

No `listen()`, no `accept()`, no `connect()`. Just send/receive.

## Reading UDP in tcpdump

```
12:00:00.001 src.54321 > dst.53: 12345+ A? google.com. (28)
12:00:00.005 dst.53 > src.54321: 12345 1/0/0 A 142.250.80.46 (44)
```

Simple: just src/dst port + payload.

## Common Issues

- **Firewall drops**: middleboxes block unknown UDP
- **MTU + fragmentation**: UDP doesn't help; large datagrams problematic
- **Reliability assumed**: app forgets packets can be lost
- **Out-of-order**: app forgets packets can arrive reordered

## UDP in K8s

UDP services work but:
- Health checks tricky (no connection state)
- LB session affinity is per 5-tuple, may not be stable
- Some K8s LBs prefer TCP

## Interview Prep

**Junior**: "When use UDP over TCP?"

**Mid**: "DNS uses UDP — why? When does it fall back to TCP?"

**Senior**: "QUIC is built on UDP — why?"

**Staff**: "Design a real-time multiplayer game protocol — TCP, UDP, or QUIC?"

## Next Topic

→ [T06 — QUIC (and HTTP/3)](T06-QUIC.md)
