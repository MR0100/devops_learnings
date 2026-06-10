# L24/C03/T01 — Kong, Tyk, AWS API Gateway

## Learning Objectives

- Use API gateways
- Compare options

## API Gateway

Layer in front of backend APIs:
- AuthN/Z
- Rate limit
- Quotas
- Transformations
- Monitoring
- Caching

## Kong

Lua + Nginx based:
- Plugin ecosystem
- Self-host or Konnect (SaaS)

```bash
curl http://kong:8001/services -d "name=my-svc" -d "url=http://my-app:8000"
curl http://kong:8001/services/my-svc/routes -d "paths[]=/api"
```

## Plugins

- Auth (Key, JWT, OAuth2, OIDC)
- Rate limiting
- ACL
- Transformations
- Logging (HTTP, Kafka, Datadog)

```bash
curl http://kong:8001/services/my-svc/plugins -d "name=rate-limiting" -d "config.minute=100"
```

## Konnect

Hosted Kong:
- Multi-region
- Managed
- $$$

## Tyk

Similar to Kong:
- Go-based
- API analytics
- Multi-tenant

For: similar use cases.

## AWS API Gateway

Managed:
- REST API
- HTTP API (faster, cheaper)
- WebSocket API

```bash
aws apigatewayv2 create-api --name my-api --protocol-type HTTP
```

Integrates with:
- Lambda
- ALB
- VPC Link

## API Gateway Features

- Throttling
- Caching
- Usage plans
- API keys
- IAM auth
- JWT (Cognito)
- Custom authorizer

## Azure API Management

Microsoft's managed gateway.

## GCP API Gateway

GCP-native.

## Self-Host vs Managed

| | Self | Managed |
|---|---|---|
| Cost | infra | per-request |
| Ops | yours | none |
| Customization | full | limited |
| Vendor lock | none | yes |

## When Gateway

- Many APIs (centralize concerns)
- Multi-team APIs
- Strict policies needed
- Public APIs

## When Not

- Single API
- Internal only
- Performance critical (extra hop)

## Architecture

```
Internet → API Gateway → Microservices
                ├─ Auth
                ├─ Rate limit
                ├─ Quota
                └─ Logging
```

## Microservices Pattern

```
Gateway → user-service
       → order-service
       → payment-service
```

Each service: focused on logic.
Gateway: cross-cutting.

## Rate Limiting

Per:
- API key
- IP
- User
- Org

```yaml
# Kong
config:
  minute: 100
  hour: 1000
  policy: redis
```

## Quota

Monthly limits per consumer:
- Free tier
- Paid tiers

For: monetization.

## Best Practices

- Single gateway per env
- Plugins for cross-cutting
- Health checks
- Observability
- IAM / mTLS to backend

## Common Mistakes

- Gateway in critical path without HA
- All logic in gateway (too coupled)
- No backup
- Skipping observability

## Quick Refs

```bash
# Kong
curl http://kong:8001/services / routes / plugins

# AWS
aws apigatewayv2 create-api / create-route / create-stage
```

## Interview Prep

**Mid**: "What's API gateway."

**Senior**: "Kong vs AWS."

**Staff**: "Gateway architecture."

## Next Topic

→ [T02 — Auth, Rate Limiting, Quotas](T02-Auth-RateLimit.md)
