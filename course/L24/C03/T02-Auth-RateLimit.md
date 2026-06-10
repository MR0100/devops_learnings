# L24/C03/T02 — Auth, Rate Limiting, Quotas

## Learning Objectives

- Auth at gateway
- Limit + quota

## Auth Options

### API Key
Simple header:
```
X-API-Key: abc123
```

Gateway validates.

### JWT
```
Authorization: Bearer eyJhbGc...
```

Gateway verifies signature.

### OAuth2 / OIDC
- Token from IdP
- Gateway validates
- Optional introspection

### mTLS
Client cert. Strongest.

### Basic
Username + password. Legacy.

## JWT at Gateway

```yaml
plugins:
  - name: jwt
    config:
      claims_to_verify: [exp]
      key_claim_name: iss
```

Verify; pass user claims to backend.

## OIDC Flow

```
Client → IdP → token
Client → Gateway (with token) → Verify → Backend
```

Gateway verifies via JWKS endpoint.

## Rate Limit

Per:
- IP (broad)
- API key (per consumer)
- User ID (per user)
- Header value

```yaml
# Kong
config:
  policy: redis
  redis_host: redis
  minute: 100
  hour: 5000
```

## Distributed Rate Limit

Multiple gateway instances:
- Coordinate via Redis
- Or local with sliding window

For: accurate global limits.

## Burst

```yaml
config:
  burst: 50    # allow burst
  rate: 10/s   # sustained
```

Token bucket: tokens refill at rate; burst up to bucket.

## Sliding Window

More accurate:
- Track timestamps
- Decay smoothly

Trade-off: memory.

## Fixed Window

Simpler:
- Count per minute / hour
- Reset at boundary

For: most use cases.

## Quota

Monthly:
- 1M requests for free tier
- 10M for paid

```yaml
plugins:
  - name: quota
    config:
      monthly: 1000000
```

Hit quota:
- Block until reset
- Or charge overage

## Plans / Tiers

- Free: 1k/day
- Basic: 100k/day
- Pro: unlimited

Tied to API key.

## Per-Endpoint

```yaml
routes:
  /api/expensive: { limit: 10/min }
  /api/cheap: { limit: 1000/min }
```

For: protect expensive ops.

## Auth + Rate Limit Combined

```yaml
plugins:
  - jwt
  - rate-limiting-advanced:
      identifier: consumer
```

Rate limit per authenticated user.

## Spike Arrest

Protect backend:
- Per-second cap
- Block on excess

For: even unintentional traffic spikes.

## Concurrent Connections

```nginx
limit_conn perip 10;
```

10 concurrent per IP.

## Black/Whitelist

```yaml
plugins:
  - ip-restriction:
      allow: ['10.0.0.0/8']
      deny: ['1.2.3.4']
```

## Audit Log

```yaml
plugins:
  - http-log:
      http_endpoint: 'https://siem/'
```

For: track API access.

## Best Practices

- Auth at gateway (zero-trust)
- Tiered rate limits
- Quotas for monetization
- Per-route customization
- Distributed limit storage
- Audit log

## Common Mistakes

- Auth at backend (gateway useless)
- No rate limit
- Same limit for all
- No quota tracking
- Skip audit

## Quick Refs

```yaml
# Kong plugins
key-auth / jwt / oauth2 / oidc
rate-limiting / rate-limiting-advanced
quota
ip-restriction
http-log / file-log
```

## Interview Prep

**Mid**: "Auth at gateway."

**Senior**: "Rate limiting algorithms."

**Staff**: "Multi-tenant gateway."

## Next Topic

→ [T03 — Gateway API (Kubernetes)](T03-Gateway-API.md)
