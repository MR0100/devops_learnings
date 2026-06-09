# L03/C04/T01 — HTTP Methods, Status Codes, Headers

## Learning Objectives

- Use HTTP methods correctly (idempotent, safe)
- Choose appropriate status codes
- Apply headers for caching, security, content negotiation

## Methods (Verbs)

| Method | Idempotent | Safe | Use |
|---|---|---|---|
| GET | Yes | Yes | Read resource |
| HEAD | Yes | Yes | Read metadata (no body) |
| POST | No | No | Create / arbitrary action |
| PUT | Yes | No | Replace resource |
| PATCH | Sometimes | No | Partial update |
| DELETE | Yes | No | Remove resource |
| OPTIONS | Yes | Yes | CORS preflight, capabilities |
| TRACE | Yes | Yes | Diagnostic; usually disabled |
| CONNECT | No | No | Tunnel (HTTPS through proxy) |

- **Safe**: doesn't modify state. Cacheable, can be repeated freely.
- **Idempotent**: N calls have same effect as 1 call.

## Status Codes

### 1xx Informational
- `100 Continue` — proceed sending body
- `101 Switching Protocols` — WebSocket upgrade
- `103 Early Hints` — preload hints before response

### 2xx Success
- `200 OK` — standard success
- `201 Created` — POST/PUT created resource (include Location header)
- `202 Accepted` — async; not yet processed
- `204 No Content` — success, no body (DELETE typical)

### 3xx Redirect
- `301 Moved Permanently` — cacheable redirect
- `302 Found` — temporary (don't cache)
- `304 Not Modified` — cached version still valid
- `307 Temporary Redirect` — preserves method (vs 302 which may convert POST → GET)
- `308 Permanent Redirect` — like 301 but preserves method

### 4xx Client Error
- `400 Bad Request` — malformed
- `401 Unauthorized` — not authenticated
- `403 Forbidden` — authenticated, no access
- `404 Not Found`
- `405 Method Not Allowed`
- `406 Not Acceptable` — Accept header can't be satisfied
- `409 Conflict` — concurrent modification
- `410 Gone` — permanently removed
- `412 Precondition Failed` — If-Match etc. failed
- `415 Unsupported Media Type` — content-type wrong
- `422 Unprocessable Entity` — validation failed (semantically bad)
- `429 Too Many Requests` — rate limited

### 5xx Server Error
- `500 Internal Server Error`
- `502 Bad Gateway` — upstream returned bad response
- `503 Service Unavailable` — overloaded/maintenance
- `504 Gateway Timeout` — upstream too slow

## Critical Headers

### Request
| Header | Purpose |
|---|---|
| Host | Virtual hosting (required) |
| User-Agent | Client identifier |
| Accept | Preferred response formats |
| Accept-Encoding | Compression (gzip, br) |
| Accept-Language | Locale |
| Authorization | Auth token |
| Cookie | Session/state |
| If-None-Match | Conditional (ETag) |
| If-Modified-Since | Conditional (Last-Modified) |
| Origin | CORS source |
| Referer | Previous page |

### Response
| Header | Purpose |
|---|---|
| Content-Type | Media type of body |
| Content-Length | Body length |
| Content-Encoding | Compression used |
| Cache-Control | Cache directives |
| ETag | Resource version |
| Last-Modified | Modification time |
| Location | Redirect target |
| Set-Cookie | Set state on client |
| Strict-Transport-Security | HSTS |
| Content-Security-Policy | CSP |
| X-Frame-Options | Anti-clickjacking |
| X-Content-Type-Options | nosniff |

## ETag / Conditional Requests

```
GET /resource
→ 200 OK, ETag: "v3", body

Client caches body + ETag.

Later:
GET /resource
If-None-Match: "v3"
→ 304 Not Modified, no body (saves bandwidth)
```

## Compression

```
Request: Accept-Encoding: gzip, br, zstd
Response: Content-Encoding: br
         body is brotli-compressed
```

Typical compression: 60-90% size reduction on text/json/HTML.

## Content Negotiation

Server may serve different content based on Accept:
```
Accept: application/json    → JSON response
Accept: application/xml     → XML response
Accept: text/html           → HTML response
Accept: */*                 → server's choice
```

Server uses `Vary: Accept` to indicate variation for caches.

## CORS Preflight

For non-simple requests (POST with custom headers, etc.):
```
OPTIONS /api/foo
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: X-Custom

→ 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: X-Custom
Access-Control-Max-Age: 3600
```

Browser then sends actual POST.

## Conditional and Cacheable

```
Cache-Control: public, max-age=3600, s-maxage=86400, must-revalidate, immutable
```

- `public` — caches by anyone
- `private` — browser only, not shared caches
- `max-age` — TTL seconds (browser)
- `s-maxage` — TTL for shared caches (CDN)
- `must-revalidate` — must check before serving stale
- `immutable` — never check (for versioned URLs)
- `no-cache` — must revalidate every time
- `no-store` — don't store

## Interview Prep

**Junior**: "GET vs POST."

**Mid**: "Idempotent vs safe. Examples?"

**Senior**: "404 vs 410 vs 405."

**Staff**: "Design caching headers for: HTML page, versioned JS, user-specific API."

## Next Topic

→ [T02 — HTTPS / TLS Handshake](T02-HTTPS-Handshake.md)
