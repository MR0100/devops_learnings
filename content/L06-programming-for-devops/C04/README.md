# L06/C04 — API Design

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-REST-Design.md) | REST Design Principles | 1 hr |
| [T02](T02-OpenAPI.md) | OpenAPI / Swagger | 1 hr |
| [T03](T03-gRPC.md) | gRPC and Protocol Buffers | 1.5 hr |
| [T04](T04-Webhooks.md) | Webhooks and Async APIs | 0.5 hr |

## REST Principles

REST = Representational State Transfer (Roy Fielding, 2000).

Constraints:
- **Stateless** — each request stands alone
- **Client-server** — separation of concerns
- **Cacheable** — responses identify cacheability
- **Uniform interface** — resources via URIs, standard methods, self-describing
- **Layered system** — clients can't tell if directly hitting server or proxies
- **(Optional) Code on demand** — server can ship JS/code

### Resource Naming
```
✅ GET    /users               (collection)
✅ GET    /users/42            (resource)
✅ POST   /users               (create)
✅ PUT    /users/42            (replace)
✅ PATCH  /users/42            (partial update)
✅ DELETE /users/42            (delete)
✅ GET    /users/42/orders     (related)

❌ GET    /getUsers
❌ POST   /createUser
❌ GET    /user/42/orders/list
```

Use **plural nouns**. Avoid verbs in URLs. Verbs are HTTP methods.

### Idempotency

| Method | Idempotent | Safe |
|---|---|---|
| GET | Yes | Yes |
| HEAD | Yes | Yes |
| OPTIONS | Yes | Yes |
| PUT | Yes | No |
| DELETE | Yes | No |
| POST | No | No |
| PATCH | Varies | No |

For non-idempotent operations (POST), use **Idempotency-Key** header so retries are safe.

### Versioning

```
/v1/users
Accept: application/vnd.myapi.v1+json
?version=1
```

URL versioning (`/v1/`) is most common and least surprising.

### Pagination

```
GET /users?page=2&per_page=20
GET /users?cursor=eyJpZCI6MTAwfQ              # cursor-based (preferred at scale)
GET /users?limit=20&offset=40                  # offset (simple but slow at scale)
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIwfQ",
    "has_more": true
  }
}
```

### Filtering & Sorting

```
GET /users?status=active&sort=-created_at&fields=id,name
```

### Status Codes

```
200 OK              successful read
201 Created         resource created (include Location header)
204 No Content      successful delete
400 Bad Request     malformed
401 Unauthorized    not auth'd
403 Forbidden       auth'd but no access
404 Not Found
409 Conflict        version conflict / dup key
422 Unprocessable   validation error
429 Too Many        rate limited
500 Internal        your bug
503 Unavailable     overloaded / down
```

### Error Format (consistent)

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "No user with id 42",
    "request_id": "abc-123"
  }
}
```

RFC 7807 (Problem Details) is the modern standard:

```json
{
  "type": "https://example.com/probs/user-not-found",
  "title": "User not found",
  "status": 404,
  "detail": "No user with id 42",
  "instance": "/users/42"
}
```

## OpenAPI / Swagger

Schema-first API design. Document → generate clients, server stubs, mocks.

```yaml
openapi: 3.1.0
info:
  title: Users API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      summary: Get user
      parameters:
      - name: id
        in: path
        required: true
        schema: {type: integer}
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      required: [id, name]
      properties:
        id: {type: integer}
        name: {type: string}
        email: {type: string, format: email}
```

Tools: Swagger UI, ReDoc, openapi-generator, oapi-codegen (Go), datamodel-code-generator (Python).

## gRPC + Protocol Buffers

Binary-encoded RPC. Built on HTTP/2.

```protobuf
// users.proto
syntax = "proto3";
package users.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);    // server streaming
}

message GetUserRequest {
  int64 id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

Generate code:
```bash
protoc --go_out=. --go-grpc_out=. users.proto
```

Why gRPC:
- Binary (smaller, faster than JSON)
- HTTP/2 multiplexing
- Streaming (client, server, bi-di)
- Strong types via .proto
- Wide language support

When NOT gRPC:
- Browser clients (gRPC-Web is awkward)
- Public APIs (REST/JSON is friendlier)
- Cacheable reads (REST + CDN wins)

## GraphQL

One endpoint; client specifies the shape of response.

```graphql
query {
  user(id: 42) {
    name
    orders(last: 5) {
      id
      total
    }
  }
}
```

Pros:
- Client gets exactly what it asks for (no over-fetch)
- One round trip for related data
- Schema-driven

Cons:
- N+1 query risk on backend (fix with DataLoader)
- Caching is hard (one endpoint, varied queries)
- Authorization is per-field complexity
- Less suitable for streaming/bulk

When GraphQL: client-driven, varied data needs, mobile/SPA fan-out. Otherwise REST/gRPC.

## API Gateway Concerns

Independent of style, your API needs:
- Auth (token validation, OIDC)
- Rate limiting
- Quota
- Request/response transformation
- Observability (metrics, traces)
- Versioning
- Documentation

Tools: AWS API Gateway, Kong, Apigee, Tyk, Envoy, Krakend, Gravitee.

## Interview Themes

- "Design a RESTful API for a resource"
- "Compare REST and gRPC"
- "How do you version a public API?"
- "What is idempotency and why does it matter for POST?"
- "Walk through pagination strategies"
- "When GraphQL?"
