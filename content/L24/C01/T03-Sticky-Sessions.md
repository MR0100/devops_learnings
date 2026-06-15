# L24/C01/T03 — Sticky Sessions

## Learning Objectives

- Use sticky sessions
- Avoid when possible

## Sticky Session

Same client → same backend:
- Session state on backend
- Subsequent requests routed there

## Why

If backend stores state in memory:
- User cart on backend A
- If routed to B: cart missing

For: in-memory state.

## Why Avoid

- Hot backend (popular user)
- Failover: state lost
- Scaling complications
- Not cloud-native

For: stateless preferred.

## Stateless Pattern

Store state in:
- Redis
- DB
- Client (cookie)

Backend doesn't need session affinity.

## Sticky via Cookie

LB sets cookie:
```
Set-Cookie: backend=server-1; HttpOnly
```

LB reads cookie; routes.

## Sticky via Hash

Hash client IP:
```
backend = backends[hash(client_ip) % N]
```

Same IP → same backend.

Issue: NAT (many clients same IP).

## Sticky via App Cookie

App sets cookie with backend ID:
```python
response.set_cookie('backend', current_server_id)
```

LB reads; routes.

## Failover

If backend dies:
- Cookie still points there
- LB falls back to another
- State lost (graceful degradation)

## Drain Connections

Before removing backend:
- Stop new connections
- Existing finish (or timeout)

For: graceful.

## Use Cases

### Legacy
In-memory session apps. Lift-and-shift.

### WebSocket
Need same backend for connection.

### State-heavy
Where moving state expensive.

## Best to Avoid

For new apps:
- Session in Redis
- JWT tokens
- Stateless

## K8s

For sticky:
```yaml
sessionAffinity: ClientIP
```

Or Ingress controller config.

## Nginx

```nginx
upstream web {
    ip_hash;
    server web1;
    server web2;
}

# Or cookie
upstream web {
    sticky cookie srv_id expires=1h;
    server web1;
    server web2;
}
```

## HAProxy

```
backend web
  cookie SRV_ID insert indirect nocache
  server web1 :80 cookie web1
  server web2 :80 cookie web2
```

## ALB (AWS)

Target group:
```bash
aws elbv2 modify-target-group-attributes \
  --target-group-arn ... \
  --attributes Key=stickiness.enabled,Value=true \
              Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

## TTL

Sticky for how long?
- Short (5 min): light affinity
- Long (1 hr): heavier

For: balance load distribution.

## Best Practices

- Avoid when possible
- Session in Redis
- Cookie-based sticky if needed
- TTL reasonable
- Plan for failover

## Common Mistakes

- Default sticky everywhere (limits scale)
- IP hash with NAT (hot spots)
- No TTL (permanent)
- No state backup (lose on failover)

## Quick Refs

```nginx
upstream X { ip_hash / sticky cookie }
```

```yaml
sessionAffinity: ClientIP
sessionAffinityConfig:
  clientIP:
    timeoutSeconds: 10800
```

## Interview Prep

**Mid**: "Sticky sessions."

**Senior**: "When sticky."

**Staff**: "Stateless design."

## Next Topic

→ Move to [L24/C02 — Reverse Proxies](../C02/README.md)
