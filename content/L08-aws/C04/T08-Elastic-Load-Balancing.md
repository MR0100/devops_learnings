# L08/C04/T08 — Elastic Load Balancing (ALB, NLB, GWLB)

## Learning Objectives

- Pick the right load balancer type (L4 vs L7)
- Configure target groups, listeners, and health checks
- Understand cross-zone balancing and sticky sessions

## ELB Family

Elastic Load Balancing distributes incoming traffic across targets (EC2, IP, Lambda, containers) in multiple AZs. Four types:

| Type | Layer | Protocols | Use |
|---|---|---|---|
| ALB (Application) | L7 | HTTP, HTTPS, gRPC | Web apps, microservices, path/host routing |
| NLB (Network) | L4 | TCP, UDP, TLS | Ultra-low latency, static IP, millions of req/s |
| GWLB (Gateway) | L3 (IP) | GENEVE (6081) | Inline appliances (firewalls, IDS/IPS) |
| CLB (Classic) | L4/L7 | HTTP, HTTPS, TCP | Legacy only — do not use for new builds |

CLB is the original generation; ALB/NLB/GWLB are the modern "v2" load balancers. Use ALB or NLB for new workloads.

## L4 vs L7

- **L4 (NLB)**: operates on TCP/UDP. Forwards packets without reading application content. Preserves the client source IP, extremely fast, fixed per-AZ IP. No knowledge of HTTP paths or headers.
- **L7 (ALB)**: terminates the connection and reads HTTP. Can route on host, path, header, method, query string, and source IP. Can rewrite, redirect, authenticate, and return fixed responses. Higher feature set, slightly higher latency than NLB.

Rule of thumb: HTTP/gRPC → ALB; raw TCP/UDP or you need a static IP / source-IP preservation → NLB.

## Listeners

A listener checks for connection requests on a protocol + port and applies rules.

```
ALB listener :443 (HTTPS)
  rules (evaluated by priority, lowest first):
    1. host = api.example.com, path = /v1/*  → forward to api-tg
    2. path = /static/*                       → forward to static-tg
    3. header X-Canary = true                 → forward to canary-tg
    default                                   → forward to web-tg
```

- ALB rules support conditions (host, path, http-header, http-request-method, query-string, source-ip) and actions (forward, redirect, fixed-response, authenticate-cognito, authenticate-oidc).
- NLB listeners are simpler: protocol + port → target group (no content rules).
- TLS termination: attach an ACM certificate; ALB/NLB decrypt and (optionally) re-encrypt to targets.

## Target Groups

A target group is the routing destination. It holds targets and the health-check config.

Target types:
- `instance` — EC2 instance IDs (LB resolves the primary ENI)
- `ip` — IP addresses (on-prem via DX/VPN, ECS awsvpc tasks, peered VPCs)
- `lambda` — invoke a Lambda function (ALB only)
- `alb` — an ALB as a target of an NLB (static IP in front of L7 routing)

```bash
aws elbv2 create-target-group \
  --name api-tg --protocol HTTP --port 8080 \
  --vpc-id vpc-xxxx --target-type ip \
  --health-check-path /healthz --health-check-interval-seconds 15
```

Routing algorithms (ALB): `round_robin` (default) or `least_outstanding_requests` (good for uneven request cost). NLB uses a flow hash (5-tuple).

## Health Checks

The LB only sends traffic to healthy targets.

- **ALB**: HTTP/HTTPS probe to a path; healthy when it returns the configured matcher (e.g. `200-299`).
- **NLB**: TCP, HTTP, or HTTPS probe. TCP checks only confirm the port accepts a connection — prefer an HTTP check against a real health endpoint so app-level failures are caught.

Key knobs: interval, timeout, healthy/unhealthy threshold, success matcher. Make the health endpoint cheap and dependency-aware (it should fail if a critical downstream is unreachable, but not flap on transient blips).

## Cross-Zone Load Balancing

Determines whether a node in one AZ can send traffic to targets in other AZs.

- **ALB**: cross-zone is always on and free. Traffic spreads evenly across all healthy targets regardless of AZ.
- **NLB / GWLB**: cross-zone is off by default. Each AZ's node only forwards to targets in its own AZ, so uneven target counts per AZ cause uneven load. You can enable it, but cross-AZ data transfer is then billed.

If you enable client-facing DNS across AZs, keep target counts balanced per AZ when cross-zone is off.

## Sticky Sessions (Session Affinity)

Pin a client to the same target.

- **ALB duration-based**: LB-generated `AWSALB` cookie; you set the duration.
- **ALB application-based**: your app issues a custom cookie the LB honors.
- **NLB**: source-IP affinity (no cookies at L4).

Stickiness helps for in-memory session state but undermines even load distribution and complicates deploys. Prefer stateless apps with external session storage (ElastiCache/DynamoDB) and use stickiness only when forced.

## Connection Draining (Deregistration Delay)

When a target is deregistered or fails a health check, the LB stops sending new requests but lets in-flight requests finish, up to the deregistration delay (default 300s). Tune it to your longest reasonable request so deploys don't cut connections.

## Connections to Targets

- ALB and NLB scale automatically; AWS recommends DNS-based access, not hardcoding IPs (except NLB static/Elastic IPs which are stable).
- ALB sets `X-Forwarded-For` / `X-Forwarded-Proto` so targets see the real client IP/protocol after L7 termination.
- NLB preserves the source IP natively (targets see the client directly) unless using an `ip` target across certain paths.

## Security & Integration

- ALB integrates with AWS WAF (web ACLs) and with Cognito/OIDC for built-in authentication; NLB does not.
- Security groups: ALB has its own SG; reference it from target SGs rather than opening CIDRs. NLB historically had no SG, but security groups for NLB are now supported.
- ACM provides free public TLS certs with auto-renewal for HTTPS/TLS listeners.

## ALB vs NLB vs GWLB — Picking

- **ALB**: HTTP(S)/gRPC, path/host routing, WAF, auth, Lambda targets, blue/green and canary via weighted target groups.
- **NLB**: extreme throughput/low latency, static/Elastic IP, source-IP preservation, TCP/UDP, PrivateLink producer front-end.
- **GWLB**: transparently insert third-party network appliances (firewall/IDS) in the traffic path using GENEVE; pairs with GWLB endpoints for centralized inspection.

## Common Mistakes

- Using a Classic Load Balancer for a new build instead of ALB/NLB
- TCP-only health checks on an NLB that miss application-layer failures
- Leaving NLB/GWLB cross-zone off with unbalanced targets per AZ, causing hot AZs
- Relying on sticky sessions to hide non-stateless app design
- Deregistration delay shorter than the longest request, cutting connections during deploys
- Hardcoding LB IPs instead of using the DNS name (ALB IPs change)
- Opening target security groups to CIDRs instead of referencing the LB's SG

## Best Practices

- ALB for HTTP/gRPC, NLB for L4/static-IP/throughput, GWLB for inline appliances
- Real HTTP health endpoints that reflect critical downstream health without flapping
- Keep apps stateless; externalize sessions and avoid stickiness where possible
- Front ALB with WAF and use ACM certs with automatic renewal
- Balance targets per AZ (or enable cross-zone deliberately, accepting the data-transfer cost)
- Set deregistration delay to cover your longest request for zero-downtime deploys
- Use weighted target groups for canary/blue-green shifts

## Quick Refs

```bash
# Create an ALB across two public subnets
aws elbv2 create-load-balancer --name web-alb --type application \
  --subnets subnet-aaaa subnet-bbbb --security-groups sg-alb

# Create a target group with an HTTP health check
aws elbv2 create-target-group --name web-tg --protocol HTTP --port 8080 \
  --vpc-id vpc-xxxx --target-type ip --health-check-path /healthz

# Add an HTTPS listener with a default forward action
aws elbv2 create-listener --load-balancer-arn arn:...:loadbalancer/app/web-alb/... \
  --protocol HTTPS --port 443 --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:...:targetgroup/web-tg/...

# Add a path-based routing rule
aws elbv2 create-rule --listener-arn arn:... --priority 10 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=arn:...:targetgroup/api-tg/...

# Check target health
aws elbv2 describe-target-health --target-group-arn arn:...:targetgroup/web-tg/...
```

## Interview Prep

**Junior**: "ALB vs NLB — when do you use each?"

**Mid**: "Walk through listener rules and target groups for path-based routing."

**Senior**: "Explain cross-zone load balancing and how it differs between ALB and NLB."

**Staff**: "Design zero-downtime deploys and weighted canary routing behind an ALB."

## Next Topic

→ Move to [L08/C05 — S3 Deep Dive](../C05/README.md)
