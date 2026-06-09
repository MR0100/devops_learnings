# L24/C03 — API Gateway

## Topics

- **T01 Kong, Tyk, AWS API Gateway** — Common gateways
- **T02 Auth, Rate Limiting, Quotas** — Core capabilities
- **T03 Gateway API (Kubernetes)** — Modern Ingress

## API Gateway vs Reverse Proxy

| | Reverse Proxy | API Gateway |
|---|---|---|
| Layer | L4 + basic L7 | L7-focused |
| Auth | Pass-through | Built-in (OAuth, JWT, etc.) |
| Rate limit | Available | First-class |
| Schema validation | No | OpenAPI integration |
| Plugin ecosystem | Modules | Rich plugins |
| Use | LB, edge | API platforms |

A gateway is a specialized reverse proxy with API-specific features.

## What an API Gateway Does

1. **Authentication**: validate tokens (OAuth, JWT, API key)
2. **Authorization**: enforce scopes / roles
3. **Rate limiting** per client / token / route
4. **Request transformation**: rewrite, add headers, transform payloads
5. **Response transformation**: same
6. **Routing**: by path, method, headers
7. **Caching** of GET responses
8. **Throttling** to protect backends
9. **Observability**: per-route metrics
10. **Versioning** of APIs

## Kong

Most popular open-source API gateway. Postgres or Cassandra backed; or DB-less (declarative config).

```yaml
# kong.yml (DB-less)
_format_version: "3.0"
services:
  - name: api
    url: http://api-backend:8080
    routes:
      - name: api-route
        paths: ["/api"]
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 100
          policy: redis
          redis_host: redis
      - name: prometheus
```

### Strengths
- Mature plugin ecosystem (auth, logging, transformations)
- Performant (Nginx + Lua under the hood)
- Free OSS + commercial enterprise
- Kubernetes Ingress Controller available

## Tyk

OSS gateway, written in Go.
- Lighter than Kong
- Cloud, hybrid, or self-hosted
- Strong for API products (developer portal, monetization)

## AWS API Gateway

Managed by AWS. Two main types:

### REST API
- More features (caching, throttling, validation)
- Higher cost (~$3.50 / million requests)
- Best for traditional REST APIs

### HTTP API
- Subset of features
- Cheaper (~$1 / million requests)
- Best for simple HTTP proxies, especially to Lambda

### WebSocket API
- For real-time
- $1 / million messages + $0.25 / million connection-minutes

### Integration
- Lambda (proxy or non-proxy)
- HTTP backend
- AWS service direct (e.g., S3, DynamoDB)
- VPC link to private resources

### Authorizers
- IAM
- Cognito User Pool
- Lambda authorizer (custom)
- JWT (HTTP API)

### Cost Consideration
At high QPS, API Gateway can be more expensive than an ALB + auth Lambda. Calculate based on traffic.

## Other Gateways

- **Apigee** (Google): enterprise; deep API management
- **Mulesoft** (Salesforce): enterprise integration
- **Express Gateway**: Node.js-based
- **KrakenD**: Go, high-performance
- **Gravitee**: OSS + enterprise

## Auth Patterns

### API Key
- Simple; per-customer
- Limited security (rotate often)
- Header: `X-API-Key: abc123`

### OAuth 2.0 / OIDC
- Token-based
- Verify against IdP (Auth0, Cognito, Keycloak)
- Refresh tokens for long sessions

### JWT
- Self-contained token
- Verify signature; no DB lookup
- Carry claims (user_id, scopes)

```python
# Verify
import jwt
payload = jwt.decode(token, public_key, algorithms=["RS256"], audience="my-api")
user_id = payload["sub"]
```

### mTLS
- Both sides present certs
- For service-to-service or high-security APIs

## Rate Limiting

### Token Bucket
- Bucket of N tokens
- Refilled at rate
- Each request consumes a token
- Empty bucket = reject

### Fixed Window
- Counts per minute / hour
- Simple but bursty at window boundaries

### Sliding Window
- Smoother than fixed
- Track requests over rolling window

### Distributed Rate Limit
- State in Redis (Lua script for atomicity)
- All gateway instances share

### Per Whom?
- Per IP (basic; CGNAT issues)
- Per API key (better)
- Per user (after auth)
- Per route + per user (most granular)

## Gateway API (Kubernetes)

Next-gen K8s Ingress. Multi-role friendly.

### Resources
- **GatewayClass**: a controller type (Istio, Contour, etc.)
- **Gateway**: an instance, with listeners
- **HTTPRoute / TCPRoute / GRPCRoute**: routing rules

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: istio
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls:
        certificateRefs: [{ name: my-cert }]

---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-route
spec:
  parentRefs:
    - name: my-gateway
  hostnames: ["api.example.com"]
  rules:
    - matches:
        - path: { type: PathPrefix, value: /v1 }
      backendRefs:
        - name: my-api-v1
          port: 8080
          weight: 90
        - name: my-api-v2
          port: 8080
          weight: 10
```

### Why Replace Ingress
- Role separation (infra team owns Gateway, app team owns Route)
- Multi-protocol (HTTP, gRPC, TCP, UDP)
- Richer routing (weighted, traffic split, retries)
- Standardized across controllers

### Implementations
- Istio
- Envoy Gateway
- Contour
- Cilium
- AWS Gateway API Controller for ALB

## When API Gateway

| Need | Pick |
|---|---|
| Public API with auth + rate limit | Kong / AWS API GW / Tyk |
| K8s internal traffic L7 | Ingress (Nginx / Traefik) or Gateway API |
| API product (devs consume) | Apigee / Kong with portal |
| Pure routing, no API features | Plain reverse proxy is enough |
| Lambda backend | AWS API Gateway natural fit |

## Interview Themes

- "API gateway vs reverse proxy"
- "Auth options at gateway"
- "Rate limiting algorithms"
- "Gateway API vs Ingress"
- "Walk through API design + gateway choices"
