# L03/C04/T04 — HTTP/3 Over QUIC

## Learning Objectives

- Understand HTTP/3's relationship to QUIC
- Recognize benefits over HTTP/2
- Know adoption status

## HTTP/3 = HTTP semantics over QUIC

- Methods, status codes, headers: same as HTTP/1.1 and HTTP/2
- Transport: QUIC (over UDP) instead of TCP
- TLS: built into QUIC (TLS 1.3)

## Key Benefits

1. **No TCP HoL blocking** — packet loss only affects one stream
2. **Faster connection setup** — 1 RTT (or 0-RTT for resumption)
3. **Connection migration** — IP change doesn't kill connection
4. **Independent streams** — true parallelism
5. **Always encrypted** — no fallback to plaintext

## Why It Matters

For mobile users:
- Network changes (Wi-Fi → cellular) survive
- Lossy connections perform better
- Lower latency on first request

For servers:
- Better p99 latency
- More efficient on poor connections
- Future-proof

## QPACK

HTTP/3's equivalent of HPACK (header compression).
Differences:
- Adapted for QUIC's stream model (no HoL between streams)
- Doesn't block streams during dynamic table updates

## Frame Types

Like HTTP/2, framed:
- DATA
- HEADERS
- SETTINGS
- PUSH_PROMISE (still in spec but not widely implemented)
- GOAWAY
- MAX_PUSH_ID
- CANCEL_PUSH

## Connection Establishment

```
TCP + TLS 1.3: 2 RTT
TCP + TLS 1.2: 3 RTT (or more)
QUIC (HTTP/3): 1 RTT
QUIC 0-RTT:    0 RTT (with resumption)
```

For 100ms RTT path, that's a noticeable difference.

## Alt-Svc Header

How browsers learn about HTTP/3:
```
HTTP/2 response:
Alt-Svc: h3=":443"; ma=86400
```

Translation: "I also support HTTP/3 on port 443; remember for 24h."

Next visit: browser tries HTTP/3 first.

Also: DNS HTTPS records can advertise HTTP/3.

## DNS HTTPS Records

```
example.com. HTTPS 1 . alpn="h3,h2"
```

Tells client: this site supports HTTP/3 and HTTP/2.

## Adoption (2025)

- Cloudflare: enabled by default for all sites
- Google: serves HTTP/3 from major services
- Meta: serves HTTP/3
- AWS CloudFront: supports
- Most major browsers: enabled by default

~30% of HTTP traffic globally is HTTP/3.

## Implementation Landscape

- **Servers**: Nginx 1.25+, Caddy, LiteSpeed, Cloudflare's quiche
- **Clients**: Chrome, Firefox, Safari, Edge
- **Libraries**: quic-go (Go), aioquic (Python), msquic (Microsoft), quiche (Rust)

## Performance Reality

Benchmarks vary. Generally:
- Excellent on lossy paths (mobile, congested Wi-Fi)
- Roughly equal on clean wired networks
- Slightly higher CPU on server (no kernel offload yet)

## Operating

```bash
curl --http3 https://example.com -v
# Requires curl built with HTTP/3 support (often nghttp3 / quiche)

nghttp3 https://example.com   # specialized debug
```

Wireshark dissects HTTP/3 with keys.

## Common Mistakes

### Firewalls
Some enterprises block UDP/443 — HTTP/3 fails; browser falls back to HTTP/2.

### CPU
QUIC is in user-space; ~2-3× CPU vs TCP. Improving.

### Tooling
Diagnostic tools less mature than for TCP-based HTTP.

## When to Adopt

For public web: yes (CDN handles transparently).
For internal APIs: depends on use case (mobile users? geographic? Y/N).

Most teams: enable on CDN; benefit immediately.

## Common Issues

- **CDN supports but origin doesn't**: HTTP/3 at edge; HTTP/1.1 to origin (still wins for users)
- **Some users on networks blocking UDP/443**: fall back to HTTP/2
- **Connection migration disabled by some middleboxes**: less benefit

## Performance Wins (Cloudflare data)

For Cloudflare users:
- 11% reduction in TTFB on average
- Bigger wins on mobile (often 20-30%)
- Best wins on lossy connections

## Future

- HTTP/3 likely default for next 10 years
- Possibly HTTP/4 someday (no concrete proposals)
- Multipath QUIC (multi-network paths simultaneously)
- WebTransport (raw datagrams over QUIC for games/AR)

## Best Practices

- **Enable HTTP/3 at the CDN/edge** and let it speak HTTP/2 or HTTP/1.1 to the origin — users get QUIC's loss/latency benefits without re-architecting backends.
- **Advertise it correctly**: send `Alt-Svc: h3=":443"` and/or a DNS `HTTPS` record (`alpn="h3,h2"`), and always keep HTTP/2 as a working fallback for UDP-blocked clients.
- **Verify UDP/443 reachability from real networks** and monitor the h3-vs-h2 negotiation ratio; a low h3 share usually means a middlebox is dropping UDP.
- **Capacity-plan for higher CPU**: QUIC runs largely in user space (~2-3× TCP CPU). Budget for it on high-throughput origins, or terminate at the CDN.
- **Gate 0-RTT to idempotent requests only** — early data is replayable.
- **Prioritize HTTP/3 for mobile and lossy-network audiences**, where independent streams + connection migration deliver the biggest wins (Cloudflare reports ~11% TTFB improvement, more on mobile).

## Quick Refs

HTTP/3 = HTTP semantics over **QUIC** (over UDP), TLS 1.3 built in. Fixes TCP's cross-stream HoL blocking; survives IP changes via Connection ID; header compression is **QPACK** (HoL-safe variant of HPACK).

Handshake RTTs: TCP+TLS1.3 = 2 · QUIC = 1 · QUIC 0-RTT = 0. Discovery: `Alt-Svc: h3=":443"; ma=86400` or DNS `example.com. HTTPS 1 . alpn="h3,h2"`. Adoption (2025): ~30% of HTTP traffic; default on major CDNs/browsers.

```bash
# Requires curl built with HTTP/3 (nghttp3/quiche)
curl --http3 -v https://example.com 2>&1 | grep -i 'HTTP/3\|h3'

# Confirm the Alt-Svc advertisement (served over h2)
curl -sI https://example.com | grep -i alt-svc

# Check DNS HTTPS record
dig HTTPS example.com +short

# See QUIC/UDP packets
sudo tcpdump -ni any 'udp port 443'
```

## Interview Prep

**Mid**: "What's HTTP/3?"

**Senior**: "Why does HTTP/3 work better than HTTP/2 on lossy networks?"

**Staff**: "Should we enable HTTP/3 on our service? Tradeoffs?"

## Next Topic

→ [T05 — Cookies, CORS, Same-Origin Policy](T05-Cookies-CORS.md)
