# L03/C02/T06 — QUIC (and HTTP/3)

## Learning Objectives

- Understand QUIC's design goals
- Compare QUIC to TCP+TLS
- Know HTTP/3's relationship to QUIC

## What QUIC Is

QUIC = Quick UDP Internet Connections. Originally Google; standardized as RFC 9000 (2021).

A reliable, encrypted transport built on UDP. Replaces TCP+TLS for many use cases.

## Why Not TCP?

TCP has shortcomings:
- **HoL blocking**: one lost packet stalls ALL streams sharing the connection
- **Slow handshake**: TCP + TLS = 2-3 RTT before data
- **Connection identity tied to 4-tuple**: change network → connection broken
- **Implemented in kernel**: hard to evolve
- **Middlebox ossification**: every change risks breaking middleboxes

QUIC fixes all of these.

## Key Features

### 1-RTT Handshake (0-RTT for resumption)
QUIC bundles transport + crypto handshake:
```
ClientHello (with key share) + early data (optional)
   ───────────────────────→
ServerHello + transport params + encrypted Finished
   ←───────────────────────
[application data]
```

vs TCP+TLS 1.3 needing TCP handshake (1 RTT) + TLS handshake (1 RTT).

### No HoL Blocking Between Streams
QUIC has multiple streams in one connection. A packet loss only blocks affected stream(s), not all.

TCP: 1 connection = 1 byte stream. Loss anywhere blocks all data after it (even on other HTTP/2 streams which were multiplexed in user space).

### Connection Migration
Connection identified by Connection ID, not 4-tuple. Laptop switches Wi-Fi → connection survives.

Browsers + mobile clients see fewer broken connections.

### TLS Built In
No separate TLS handshake. TLS 1.3 always (no plaintext mode).

### Implemented in User Space
- Faster iteration
- Each app can have own implementation (less middlebox issues)
- Higher CPU cost (no kernel offload typically)

### Better Loss Recovery
- Distinguishes loss vs reordering better
- Improved ACK frequency
- Per-stream recovery

## HTTP/3

HTTP/3 = HTTP semantics, but over QUIC.

```
HTTP/1.1 → TCP
HTTP/2   → TCP (multiplexed; still suffers TCP HoL)
HTTP/3   → QUIC (over UDP)
```

### Why HTTP/3 Matters

For users on lossy networks (mobile, Wi-Fi):
- Less buffering
- Faster page loads
- Survives network changes

For servers:
- Better tail latency
- More efficient on poor connections

### Adoption (2025)
- ~30% of Internet HTTP traffic
- All major CDNs support
- All major browsers default to it
- Mobile carriers increasingly optimize for it

## Negotiating HTTP/3

Server signals via header `Alt-Svc`:
```
Alt-Svc: h3=":443"; ma=86400
```

Client remembers; uses HTTP/3 next time.

Or via DNS HTTPS record.

## QUIC Implementations

- **quiche** (Cloudflare) — Rust; widely deployed
- **mvfst** (Meta)
- **msquic** (Microsoft)
- **lsquic** (LiteSpeed)
- **google-quic** → standardized
- **Go**: `quic-go`
- **Python**: `aioquic`

## Downsides

### CPU Cost
TCP has hardware offload (TSO, GRO, ToE). QUIC mostly software. CPU cost can be 2-3× TCP.

Improving as kernel and hardware add QUIC support.

### Middlebox Issues
- Some networks block UDP / rate limit
- QUIC can be blocked at enterprise firewalls
- Connection establishment may fail; client falls back to HTTP/2

### Diagnostic Tools Lag
Wireshark + tools improving but TCP debugging is still richer.

## Servers Supporting QUIC

- Cloudflare (default)
- Cloud CDN (Google)
- Fastly
- Nginx (1.25+)
- Caddy (built-in)
- AWS CloudFront

## Reading QUIC in tcpdump

```
12:00:00.001 src.54321 > dst.443: UDP, length 1200 (QUIC initial)
12:00:00.005 dst.443 > src.54321: UDP, length 1200 (QUIC handshake)
12:00:00.010 src.54321 > dst.443: UDP, length 500 (HTTP request inside)
```

Wireshark dissects QUIC and HTTP/3 (with keys).

## 0-RTT Resumption

For known servers, client sends data in the first packet:
```
ClientHello (with session ticket) + application data
   ───────────────────────────────→
```

Risk: replay attacks possible. Only safe for idempotent requests.

## When to Adopt HTTP/3

| Need | Adopt HTTP/3? |
|---|---|
| Public website | Yes (CDN handles it) |
| Mobile users | Yes |
| Enterprise internal | Wait — some firewalls block |
| Real-time API | Likely yes |
| Streaming media | Strongly yes |

For most: CDN flips a switch; you don't change anything.

## Common Mistakes

- **Thinking QUIC removed head-of-line blocking entirely**: it removes *cross-stream* HoL (loss on stream A no longer stalls stream B). Within a single stream, ordering is still enforced.
- **Confusing QUIC with HTTP/3**: QUIC is the transport (reliable, encrypted, over UDP); HTTP/3 is HTTP semantics mapped onto QUIC. Other protocols (DNS-over-QUIC, WebTransport) also run on QUIC.
- **Blocking or rate-limiting UDP/443 and expecting HTTP/3**: many enterprise firewalls drop UDP, forcing silent fallback to HTTP/2 over TCP. "HTTP/3 enabled but never used" is usually a UDP-blocking middlebox.
- **Using 0-RTT for non-idempotent requests**: 0-RTT early data is replayable. Restrict it to safe/idempotent operations (GET); never to writes, payments, or anything with side effects.
- **Ignoring the CPU cost**: QUIC runs largely in user space without TCP's hardware offload (TSO/GRO), often 2-3× the CPU. Capacity-plan accordingly for high-throughput origins.
- **Assuming connection migration "just works"**: NAT rebinding and some middleboxes can still break it; it's a best-effort improvement, not a guarantee.

## Best Practices

- **Let your CDN terminate HTTP/3 at the edge** and speak HTTP/2 or HTTP/1.1 to the origin — users get QUIC's benefits without re-architecting backends.
- **Advertise HTTP/3 via `Alt-Svc` and/or DNS HTTPS records**, and keep HTTP/2 as a working fallback for UDP-blocked clients.
- **Gate 0-RTT to idempotent requests only**, and disable it where replay risk isn't acceptable.
- **Watch UDP/443 reachability** from real networks; track the HTTP/3-vs-HTTP/2 negotiation ratio so you notice middlebox fallback.
- **Capture with `SSLKEYLOGFILE` + Wireshark** to decrypt and inspect QUIC/HTTP-3 — its tooling is improving but still thinner than TCP's.

## Quick Refs

Stack: `HTTP/1.1 → TCP` · `HTTP/2 → TCP (multiplexed, TCP HoL)` · `HTTP/3 → QUIC → UDP (no cross-stream HoL)`.

Handshake RTTs: TCP+TLS1.3 = 2 · TCP+TLS1.2 = 3 · QUIC = 1 · QUIC 0-RTT = 0. Connection identity: QUIC Connection ID (survives IP changes), not the 4-tuple. TLS 1.3 is mandatory (no plaintext mode).

Advertise: `Alt-Svc: h3=":443"; ma=86400` or DNS `HTTPS 1 . alpn="h3,h2"`.

```bash
# Force HTTP/3 (curl must be built with HTTP/3 support)
curl --http3 -v https://example.com

# See QUIC packets on the wire
sudo tcpdump -ni any 'udp port 443'

# Decrypt QUIC/HTTP-3 in Wireshark
SSLKEYLOGFILE=/tmp/keys.log chromium https://example.com
```

Implementations: quiche (Cloudflare/Rust), msquic (Microsoft), mvfst (Meta), quic-go (Go), aioquic (Python).

## Interview Prep

**Mid**: "What does QUIC solve that TCP+TLS doesn't?"

**Senior**: "Connection migration — how does QUIC handle network changes?"

**Staff**: "Why does HTTP/2 still have HoL blocking despite multiplexing?"

## Next Chapter

→ [C03 — DNS Deep Dive](../C03/README.md)
