# L06/C04/T01 — REST API Design Principles

## Learning Objectives

- Design RESTful APIs that scale
- Apply HTTP semantics correctly

## REST Recap

REST = Representational State Transfer. Architectural style; not a protocol.

Principles:
- Resources (nouns); not actions (verbs)
- Standard HTTP methods
- Stateless
- Cacheable
- Uniform interface

## URLs as Resources

```
GET    /users               # list
GET    /users/{id}          # one
POST   /users               # create
PUT    /users/{id}          # replace
PATCH  /users/{id}          # update
DELETE /users/{id}          # delete

GET    /users/{id}/orders   # nested
```

Nouns plural. Lower case. Use hyphens (`user-profiles` not `userProfiles`).

## HTTP Methods

| | Idempotent | Safe |
|---|---|---|
| GET | yes | yes |
| HEAD | yes | yes |
| OPTIONS | yes | yes |
| PUT | yes | no |
| DELETE | yes | no |
| POST | no | no |
| PATCH | no | no |

- **Safe**: no side effects
- **Idempotent**: same result for repeated calls

Picking method matters: GET/HEAD should never modify state (caches/proxies assume).

## Status Codes

| Code | Meaning |
|---|---|
| 200 OK | Success |
| 201 Created | Resource created (return URL via Location header) |
| 204 No Content | Success, no body (DELETE) |
| 301 Moved Permanently | URL changed |
| 304 Not Modified | Conditional GET |
| 400 Bad Request | Client error in payload |
| 401 Unauthorized | No auth |
| 403 Forbidden | Authenticated; not allowed |
| 404 Not Found | Resource missing |
| 409 Conflict | State conflict |
| 422 Unprocessable Entity | Validation failure |
| 429 Too Many Requests | Rate limited |
| 500 Internal Server Error | Server bug |
| 502 Bad Gateway | Upstream failed |
| 503 Service Unavailable | Down / overloaded |
| 504 Gateway Timeout | Upstream slow |

Use them precisely.

## Request / Response Format

JSON is default. Use `Content-Type: application/json`.

Request:
```json
POST /users
{
  "name": "alice",
  "email": "a@x.com"
}
```

Response (201):
```json
{
  "id": 42,
  "name": "alice",
  "email": "a@x.com",
  "created_at": "2026-06-09T10:00:00Z"
}
```
Headers: `Location: /users/42`

## Versioning

Three styles:
- URL: `/v1/users`, `/v2/users` (most common, explicit)
- Header: `Accept: application/vnd.myapi.v1+json`
- Query: `/users?api-version=1` (Azure)

URL versioning is simplest; some prefer media types.

## Pagination

For large collections:
```
GET /users?page=2&page_size=50
GET /users?limit=50&offset=100
GET /users?cursor=abc123&limit=50    # cursor-based (best for big data)
```

Response includes:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "def456",
    "has_more": true
  }
}
```

Cursor pagination > offset for large datasets (offset is O(N)).

## Filtering / Sorting

```
GET /users?status=active
GET /users?sort=created_at
GET /users?sort=-created_at        # descending
GET /users?fields=id,name          # sparse fields
```

## Idempotency

Critical for retries. PUT and DELETE are idempotent by spec.

POST not — use Idempotency-Key header:
```
POST /payments
Idempotency-Key: abc123
{"amount": 100}
```
Server stores result per key; replays return cached.

Stripe popularized; now standard for financial.

## Error Format

Consistent shape:
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User 42 does not exist",
    "request_id": "req_abc"
  }
}
```

Or RFC 7807 (problem+json):
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "User Not Found",
  "status": 404,
  "detail": "User 42 does not exist"
}
```

## Validation Errors

Return ALL errors, not just first:
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "errors": [
      {"field": "email", "message": "invalid format"},
      {"field": "age", "message": "must be >= 18"}
    ]
  }
}
```

## Caching

```
Cache-Control: max-age=300
ETag: "abc123"
Last-Modified: Tue, 09 Jun 2026 10:00:00 GMT
```

Client sends:
```
If-None-Match: "abc123"
If-Modified-Since: Tue, 09 Jun 2026 10:00:00 GMT
```

Server returns 304 if unchanged (saves bandwidth).

## Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1717584000
```

If exceeded: 429 with `Retry-After: 60`.

## Authentication

- Bearer token: `Authorization: Bearer <token>`
- API key in header: `X-API-Key: ...`
- HMAC signed: `Authorization: HMAC sig=...,key=...`
- OAuth 2.0 flows for delegated

## CORS

For browser-based clients:
```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization
```

## HATEOAS

Hypermedia links in responses:
```json
{
  "id": 42,
  "name": "alice",
  "_links": {
    "self": "/users/42",
    "orders": "/users/42/orders"
  }
}
```

Theoretically pure REST; practically rare.

## Common Mistakes

- Verbs in URLs (`/getUsers`, `/createOrder`)
- 200 for errors
- Stateful (session in cookie tied to server)
- Returning HTML in JSON API
- Inconsistent error format
- Plural inconsistency (`/user/1` vs `/users`)

## Best Practices

- Use HTTPS
- Validate input
- Rate limit
- Log request IDs
- Document with OpenAPI
- Version from day 1
- Pagination always
- Consistent errors
- Idempotency keys for mutations

## Quick Refs

```text
RESOURCES — nouns, plural, hierarchical
  GET    /v1/orders                 list (paginated, filterable)
  POST   /v1/orders                 create            -> 201 + Location
  GET    /v1/orders/{id}            read              -> 200 / 404
  PUT    /v1/orders/{id}            full replace (idempotent)
  PATCH  /v1/orders/{id}            partial update
  DELETE /v1/orders/{id}            remove            -> 204 / 404
  GET    /v1/orders/{id}/items      sub-resource

STATUS CODES
  200 OK   201 Created   204 No Content
  400 Bad Request   401 Unauthorized   403 Forbidden   404 Not Found
  409 Conflict   422 Unprocessable   429 Too Many Requests
  500 Server Error   503 Unavailable

PAGINATION (cursor — stable under writes)
  GET /v1/orders?limit=50&cursor=eyJpZCI6MTAwfQ
  { "data": [...], "next_cursor": "...", "has_more": true }
```

```http
# Idempotent create — retry-safe mutation
POST /v1/payments
Idempotency-Key: 7e2c-...-9f
Content-Type: application/json
```

```json
// Consistent error envelope (RFC 9457 problem+json shape)
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "amount must be > 0",
  "errors": [{ "field": "amount", "message": "must be > 0" }]
}
```

## Interview Prep

**Junior**: "GET vs POST."

**Mid**: "Idempotency — design payments API."

**Senior**: "Pagination — offset vs cursor."

**Staff**: "API versioning strategy."

## Next Topic

→ [T02 — OpenAPI / Swagger](T02-OpenAPI.md)
