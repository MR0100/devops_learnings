# L03/C04/T03 — HTTP/2 Multiplexing & Server Push

## Learning Objectives

- Understand HTTP/2's binary framing
- See why multiplexing helps over HTTP/1.1
- Know why server push is deprecated

## What Changed in HTTP/2

HTTP/2 = same semantics as HTTP/1.1 (methods, headers, status codes) but binary wire format with multiplexing.

Key wins:
- **Binary framing**: faster to parse, more compact
- **Multiplexing**: many requests/responses share one TCP connection
- **Header compression** (HPACK): reduces redundant headers
- **Server push**: server preemptively sends resources (now deprecated)
- **Stream priority**: client hints what to prioritize

## HTTP/1.1's Problems

- One connection = one request at a time
- Browsers open 6 parallel connections per origin
- TLS handshake per connection (expensive)
- Headers repeated verbatim (no compression)
- Pipelining never worked in practice (HoL blocking)

## HTTP/2 Solves Some

Single TCP connection multiplexes streams:
```
TCP connection
  ├── Stream 1: GET /page.html (request → response, interleaved)
  ├── Stream 2: GET /style.css
  ├── Stream 3: GET /script.js
  └── Stream 4: GET /image.png
```

Each stream is bidirectional; frames from different streams interleave.

## Binary Framing

```
+-----------------------------------------------+
|                 Length (24)                   |
+---------------+---------------+---------------+
|   Type (8)    |   Flags (8)   |
+---------------+---------------+-------------------------------+
|R|                 Stream Identifier (31)                      |
+-+-------------------------------------------------------------+
|                   Frame Payload (0...)                      ...
+---------------------------------------------------------------+
```

Frame types: DATA, HEADERS, PRIORITY, RST_STREAM, SETTINGS, PUSH_PROMISE, PING, GOAWAY, WINDOW_UPDATE, CONTINUATION.

## HPACK Header Compression

Tracks header table on both sides. Common headers encoded as small indices.

A second request: only NEW headers transmitted; common ones referenced from table.

Massive savings on chatty REST APIs with many headers (auth, accept, user-agent).

## TCP HoL Blocking Remains

HTTP/2 multiplexes streams. But TCP underneath is a single byte stream:
- Packet loss anywhere = ALL streams blocked until retransmit
- Better than HTTP/1.1 (which has its own HoL plus no multiplexing)
- Worse than HTTP/3 (QUIC fixes this)

On reliable networks: HTTP/2 great. On lossy: still has issues.

## Stream Priority

Client can hint:
```
Browser: "HTML and CSS first; images after"
```

Server's scheduler tries to respect.

Reality: implementations vary; not always honored.

## Server Push (Deprecated)

Original idea: server proactively sends resources client will likely need.

```
Client: GET /index.html
Server: HEADERS for /index.html
Server: PUSH_PROMISE for /style.css
Server: DATA for /index.html
Server: DATA for /style.css   (without being asked)
```

Sounds great. In practice:
- Hard to know what client has cached
- Often pushed wasted bandwidth
- Browsers removed implementations
- Server push is dead (HTTP/3 doesn't have it)

Use `Early Hints (103)` or HTTP `Link` header instead.

## Settings Frame

Each side declares preferences:
- `SETTINGS_MAX_CONCURRENT_STREAMS` (default 100)
- `SETTINGS_INITIAL_WINDOW_SIZE` (default 65535)
- `SETTINGS_HEADER_TABLE_SIZE`

## Flow Control

Per-stream and per-connection windows.
- Receiver advertises window
- Sender can't exceed
- WINDOW_UPDATE frames extend window

## ALPN Negotiation

During TLS handshake, client + server agree on HTTP version:
```
ALPN protocols: h2, http/1.1
```

Server picks `h2` if supported.

## Operating

```bash
curl --http2 -v https://example.com
# Look for: "HTTP/2 200"
```

```bash
nghttp -nv https://example.com   # better HTTP/2 debug
```

Wireshark: dissects HTTP/2 with keys.

## Should You Enable HTTP/2?

For public sites: yes (CDN handles). Major performance win for browser users.

For internal APIs: depends. Some gRPC uses HTTP/2 already. REST microservices: HTTP/1.1 keepalive often fine.

## Common Mistakes

### Many Servers Multiplex Poorly
- One stream's slow processing blocks others
- Backend may handle per-request

### HTTPS Required (in practice)
Spec allows plaintext HTTP/2 (h2c) but no browser supports.

### Operator Confusion
Some load balancers terminate HTTP/2 and forward as HTTP/1.1 (with one request per backend connection). Lose multiplexing benefit at backend.

## Best Practices

- **Enable HTTP/2 for public, browser-facing traffic** (usually a CDN/LB toggle) — multiplexing + HPACK is a clear win over HTTP/1.1's 6-connections-per-origin model.
- **Stop sharding domains and inlining assets** under HTTP/2: those HTTP/1.1 workarounds now hurt by fragmenting the single multiplexed connection and busting cache granularity.
- **Drop server push; use `103 Early Hints` or `Link: rel=preload`** instead — push is removed from browsers and absent in HTTP/3.
- **Watch for HoL-prone paths**: on lossy networks a single TCP loss stalls every stream. If that's your user base, prefer HTTP/3 (QUIC).
- **Check the backend leg**: if the LB terminates h2 and re-opens HTTP/1.1 per request to origins, you lose multiplexing there — use HTTP/2 (or h2c) to the backend or keep-alive pools.
- **Right-size `SETTINGS_MAX_CONCURRENT_STREAMS` and flow-control windows** for high-throughput APIs so a few streams don't starve the rest.

## Quick Refs

HTTP/2 vs 1.1: binary framing · single-connection multiplexing · HPACK header compression · per-stream flow control · (deprecated) server push. Version is negotiated via TLS **ALPN** (`h2`); plaintext `h2c` exists but no browser supports it. **TCP HoL blocking remains** — fixed only by HTTP/3.

Frame types: DATA, HEADERS, PRIORITY, RST_STREAM, SETTINGS, PUSH_PROMISE, PING, GOAWAY, WINDOW_UPDATE, CONTINUATION. Key settings: `MAX_CONCURRENT_STREAMS` (default 100), `INITIAL_WINDOW_SIZE` (65535).

```bash
curl --http2 -v https://example.com 2>&1 | grep -i 'HTTP/2\|ALPN'
nghttp -nv https://example.com          # detailed HTTP/2 frame trace
# Verify ALPN negotiated h2
openssl s_client -connect example.com:443 -alpn h2 </dev/null 2>/dev/null | grep ALPN
```

## Interview Prep

**Mid**: "HTTP/2 vs HTTP/1.1 — what changed?"

**Senior**: "Why does HTTP/2 still have HoL blocking?"

**Staff**: "When wouldn't you use HTTP/2?"

## Next Topic

→ [T04 — HTTP/3 Over QUIC](T04-HTTP3.md)
