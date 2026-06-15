# L27/C04/T01 — DNS-Based Failover

## Learning Objectives

- Use DNS for failover
- Limitations

## DNS Failover

Health checks → DNS record update → traffic shifts.

## Route 53

```bash
aws route53 change-resource-record-sets ...
```

Failover record:
- Primary: us-east-1
- Secondary: us-west-2
- Health check on primary

## TTL

DNS cached by clients.

```
TTL: 60   # 60-sec cache
```

Lower = faster failover; more queries.

Higher = slower failover.

For failover: 60s typical.

## Health Check

```bash
aws route53 create-health-check ...
```

Checks endpoint every N seconds.

If fails: route to secondary.

## Latency-Based

```
us-east-1 → ALB-east
us-west-2 → ALB-west
```

User → nearest.

For: also distributes load.

## Geolocation

```
North America → us-east-1
Europe → eu-west-1
```

For: routing rules.

## Weighted

```
Primary 90%, Secondary 10%
```

For: gradual or A/B.

## Failover Time

```
Detect (health check fails): 30s
Update DNS: instant
Client TTL: 60s

Total: ~1.5 min worst case
```

Some clients cache longer.

## Cache Issues

Java default DNS cache: 30 sec - infinity.
Browser: varies.

For: actual failover may be slower.

## Mitigation

- Lower TTL
- App-level retry (try alternate)
- Use anycast (next topic)

## App-Level Failover

```python
endpoints = ['primary.example.com', 'secondary.example.com']
for ep in endpoints:
    try:
        return call(ep)
    except:
        continue
```

For: client-side; faster than DNS.

## Anycast

Same IP from multiple regions:
- BGP routes to nearest
- Failover via BGP changes

Faster than DNS.

(See L24/C05/T02.)

## Best Practices

- Low TTL (60s for failover records)
- Health checks frequent
- Test failover
- App-level retry as backup
- Document RTO

## Common Mistakes

- High TTL (slow failover)
- No health check (manual failover)
- Trust DNS alone (slow)
- No test

## Quick Refs

```bash
# Route 53
aws route53 create-health-check
aws route53 change-resource-record-sets

# Failover record types: PRIMARY / SECONDARY
```

## Interview Prep

**Mid**: "DNS failover."

**Senior**: "TTL trade-offs."

**Staff**: "Failover architecture."

## Next Topic

→ [T02 — Health Checks](T02-Health-Checks-DR.md)
