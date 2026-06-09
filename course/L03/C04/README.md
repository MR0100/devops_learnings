# L03/C04 — HTTP, HTTPS, HTTP/2, HTTP/3

## Chapter Overview

HTTP is the lingua franca of modern systems. Understanding the evolution from HTTP/1.1 → HTTP/2 → HTTP/3 informs every API design and observability decision.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-HTTP-Methods-Status.md) | HTTP Methods, Status Codes, Headers | 1 hr |
| [T02](T02-HTTPS-Handshake.md) | HTTPS / TLS Handshake (Step by Step) | 1 hr |
| [T03](T03-HTTP2.md) | HTTP/2 Multiplexing & Server Push | 1 hr |
| [T04](T04-HTTP3.md) | HTTP/3 Over QUIC | 1 hr |
| [T05](T05-Cookies-CORS.md) | Cookies, CORS, Same-Origin Policy | 1 hr |

## HTTP/1.1 Anatomy

```
GET /api/users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJ...
User-Agent: Mozilla/5.0
Accept: application/json
Connection: keep-alive

(blank line)
(body, if any)
```

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 123
Cache-Control: max-age=60
ETag: "v3"
Date: Mon, 09 Jun 2026 12:00:00 GMT

{"id": 42, "name": "Alice"}
```

## Methods (Verbs)

| Method | Idempotent? | Safe? | Used For |
|---|---|---|---|
| GET | Yes | Yes | Read |
| HEAD | Yes | Yes | Read metadata only |
| POST | No | No | Create / non-idempotent action |
| PUT | Yes | No | Update / replace |
| PATCH | No (typically) | No | Partial update |
| DELETE | Yes | No | Delete |
| OPTIONS | Yes | Yes | CORS preflight; capability discovery |

**Idempotent** = N invocations have the same effect as 1.
**Safe** = doesn't modify state.

## Status Codes (Production Essentials)

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created (with Location header) |
| 204 | No Content (DELETE success) |
| 301 | Moved Permanently (cacheable) |
| 302 | Found (temporary; not cacheable) |
| 304 | Not Modified (cache hit; respect ETag/If-None-Match) |
| 400 | Bad Request (malformed) |
| 401 | Unauthorized (not authenticated) |
| 403 | Forbidden (authenticated but no access) |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 409 | Conflict (concurrent edit) |
| 410 | Gone (permanently removed) |
| 422 | Unprocessable Entity (validation failed) |
| 429 | Too Many Requests (rate limited; use Retry-After) |
| 500 | Internal Server Error (your bug) |
| 502 | Bad Gateway (upstream broken) |
| 503 | Service Unavailable (overloaded; use Retry-After) |
| 504 | Gateway Timeout |

## Critical Headers

| Header | Purpose |
|---|---|
| Host | Required; virtual hosting |
| Content-Type | Media type of body |
| Content-Length | Body length in bytes |
| Transfer-Encoding | chunked for streaming |
| Authorization | Auth token |
| Cache-Control | Cache directives |
| ETag / If-None-Match | Conditional requests |
| Last-Modified / If-Modified-Since | Same |
| Accept | Negotiate response format |
| Accept-Encoding | gzip, br |
| User-Agent | Client identifier |
| X-Forwarded-For | LB chain (client IP) |
| X-Forwarded-Proto | Original protocol |
| X-Request-Id / traceparent | Correlation IDs |
| Strict-Transport-Security | HSTS |
| Content-Security-Policy | CSP |

## Connection Reuse (HTTP/1.1)

`Connection: keep-alive` was the win of HTTP/1.1. Without it: TCP handshake per request.

But HTTP/1.1 has **head-of-line blocking**: only one request at a time per connection. Workarounds: parallel connections (6 per origin in browsers), pipelining (rarely worked in practice).

## HTTP/2

Binary framing. Single TCP connection multiplexes many concurrent streams.

Features:
- **Multiplexing** — many streams over one TCP connection
- **Header compression** (HPACK) — repeated headers compressed
- **Server push** — server preemptively sends resources (now deprecated; usage minimal)
- **Stream priority** (rarely used)

Caveat: **TCP-level head-of-line blocking remains**. A single packet loss stalls all streams on that connection.

## HTTP/3 (over QUIC)

Moves to UDP-based QUIC. Solves TCP HoL blocking. Each stream is independent.

- Faster connection setup (0-RTT after first)
- Connection migration (laptop changes network → connection survives)
- Better loss recovery

Adoption: 25–30% of Internet traffic by late 2025.

## TLS 1.3 Handshake (1-RTT)

```
Client                       Server
   │ ClientHello              │
   │ (key_share, ciphers)     │
   │ ─────────────────────►   │
   │                          │
   │ ServerHello + key_share  │
   │ {EncryptedExtensions,    │
   │  Certificate,            │
   │  CertificateVerify,      │
   │  Finished}               │
   │ ◄─────────────────────   │
   │                          │
   │ {Finished}               │
   │ ─────────────────────►   │
   │                          │
   │ {HTTP request}           │
   │ ─────────────────────►   │
```

TLS 1.3 dramatically simplifies vs 1.2: 1-RTT (vs 2-RTT), fewer cipher suites, removed broken constructs (RSA key exchange, static DH, MD5, SHA-1).

**0-RTT resumption**: subsequent connections can send data with the ClientHello (replay risk for non-idempotent ops; avoid for state-changing).

## Cookies, CORS, Same-Origin

### Cookies
- `Set-Cookie: session=abc; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600`
- `HttpOnly` — not readable by JS (prevents XSS theft)
- `Secure` — only over HTTPS
- `SameSite=Strict|Lax|None` — CSRF defense

### Same-Origin Policy
Browser restricts JS from one origin (scheme://host:port) reading from another. Without it, every site could read your bank.

### CORS
Server opt-in to allow cross-origin requests:
- `Access-Control-Allow-Origin: https://app.example.com`
- Preflight OPTIONS request for non-simple requests

## HTTP Performance

| Optimization | Win |
|---|---|
| HTTP/2 multiplexing | Eliminates per-request HoL on 1.1 |
| HTTP/3 (QUIC) | Eliminates TCP HoL |
| Connection reuse | Avoids handshake per request |
| Compression (gzip, br) | Reduces transfer size |
| Caching (Cache-Control, ETag) | Avoids transfer entirely |
| CDN | Reduces RTT |

## Interview Themes

- "Compare HTTP/1.1, HTTP/2, HTTP/3 — what each solves"
- "Walk me through a TLS 1.3 handshake"
- "Idempotent — what does it mean for HTTP methods?"
- "Cookies + CORS + SameSite — explain the security model"
- "Why is HTTP/2 still TCP-bound?"
- "When does 0-RTT cause a problem?"
