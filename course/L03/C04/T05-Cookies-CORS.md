# L03/C04/T05 — Cookies, CORS, Same-Origin Policy

## Learning Objectives

- Configure cookies safely
- Apply CORS correctly without over-opening
- Understand Same-Origin Policy

## Cookies

State client-side. Sent by server, returned with each subsequent request.

```
Server: Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600; Domain=example.com
Client: Cookie: session=abc123    (on every subsequent request)
```

## Cookie Attributes

| Attribute | Purpose |
|---|---|
| HttpOnly | Inaccessible to JS (prevent XSS theft) |
| Secure | Only sent over HTTPS |
| SameSite=Strict | Never sent cross-site |
| SameSite=Lax | Sent on top-level navigation (default modern) |
| SameSite=None | Sent always (requires Secure) |
| Domain | Which domain (default: setting origin) |
| Path | Which URL path |
| Max-Age | Expiry in seconds |
| Expires | Absolute expiry |
| Partitioned | Per top-level partition (CHIPS; emerging) |

## Cookie Best Practices

- **HttpOnly**: always for session cookies
- **Secure**: always
- **SameSite=Strict**: most secure; some UX cost (post-login redirect issues)
- **SameSite=Lax**: good default
- **Short Max-Age**: limit damage if stolen
- **Domain-scoped**: don't share across subdomains unnecessarily

## Same-Origin Policy

Browser security model: JS from origin A can't read responses from origin B (unless B says OK).

**Origin** = scheme + host + port:
- `https://example.com` and `https://api.example.com` — different origins (different host)
- `https://example.com` and `https://example.com:8080` — different (different port)
- `https://example.com:443` and `https://example.com` — same (default port)

Without SOP: every site could read your bank, email, social media.

## What SOP Restricts

- JS reading response (XHR, fetch)
- Reading iframe content (if cross-origin)
- Reading canvas (if loaded cross-origin image)
- Service workers' scope

## What SOP Doesn't Restrict

- Sending requests (always allowed; "no-cors" mode)
- Loading images, scripts, stylesheets from anywhere
- Submitting forms anywhere (CSRF risk)

## CORS

Cross-Origin Resource Sharing. Server explicitly allows cross-origin reads.

```
Browser: Origin: https://app.example.com  (set automatically)
Server:  Access-Control-Allow-Origin: https://app.example.com
         (matches → browser allows JS to read response)
```

If server doesn't respond appropriately, browser blocks JS access.

## CORS Preflight

For "non-simple" requests (custom headers, POST with JSON, etc.):

```
Browser sends OPTIONS first:
OPTIONS /api/foo
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: X-Custom

Server responds:
204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: POST, GET, DELETE
Access-Control-Allow-Headers: X-Custom, Content-Type
Access-Control-Max-Age: 3600   (cache preflight)

Browser sends actual request:
POST /api/foo
Origin: https://app.example.com
X-Custom: value
```

Preflight adds latency. Use Max-Age to cache.

## CORS with Credentials

```
JS: fetch(url, {credentials: 'include'})
Browser sends cookies/auth

Server response must include:
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://specific.origin.com   (NOT *)
```

Can't combine `Access-Control-Allow-Origin: *` with credentials. Security feature.

## Common CORS Mistakes

- **Wildcard `*` everywhere**: too permissive
- **Echoing Origin without validation**: enables any origin
- **No Vary: Origin**: cache returns wrong CORS headers
- **OPTIONS not handled**: 404 on preflight blocks all subsequent
- **Server-side checks bypassed**: CORS is BROWSER-only; servers must still authz

## Common Server Patterns

### Nginx
```nginx
location /api/ {
    add_header Access-Control-Allow-Origin "$http_origin" always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Vary "Origin" always;
    
    if ($request_method = "OPTIONS") {
        add_header Access-Control-Allow-Methods "GET, POST, DELETE" always;
        add_header Access-Control-Allow-Headers "Content-Type, X-Custom" always;
        add_header Access-Control-Max-Age "3600" always;
        return 204;
    }
}
```

Validate `$http_origin` against allowlist; don't just echo.

### Express (Node)
```javascript
const cors = require('cors');
app.use(cors({
  origin: ['https://app.example.com', 'https://admin.example.com'],
  credentials: true,
  maxAge: 3600,
}));
```

## CSRF

Different attack: site B causes browser to submit a form to site A (with A's cookies attached).
- Defense: SameSite cookies, CSRF tokens, double-submit cookies
- CORS doesn't protect against CSRF (different attack vector)

## CSP (Content Security Policy)

Header restricting what resources a page can load:
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; img-src 'self' data:; report-uri /csp-report
```

Stops XSS attacks (attacker can't inject script from arbitrary origin).

## Subresource Integrity (SRI)

```html
<script src="https://cdn.com/lib.js" 
        integrity="sha384-..." 
        crossorigin="anonymous"></script>
```

Browser verifies hash; refuses to execute if tampered.

## Interview Prep

**Mid**: "What's SameSite cookie?"

**Senior**: "Walk through CORS preflight."

**Staff**: "Design auth for a SPA + API across subdomains."

## Next Chapter

→ [C05 — TLS / SSL Deep Dive](../C05/README.md)
