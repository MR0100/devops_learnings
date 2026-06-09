# L03/C08/T02 — Anycast IP

## Learning Objectives

- Understand anycast in production
- Compare to unicast
- Apply to CDN and DNS

## Anycast Recap

One IP advertised from many physical locations. BGP routing picks "nearest" path for each client.

```
1.1.1.1 announced from:
  - Tokyo PoP (Cloudflare)
  - London PoP
  - SF PoP
  - 300+ others

Client in Berlin → routes to nearest (probably London)
Client in Tokyo → routes to Tokyo
```

## Why It Works for the Internet

- Internet routing converges quickly
- Most clients want closest endpoint
- One IP → many servers handles scale + redundancy
- Failover by withdrawing advertisement

## Production Examples

### DNS Roots
13 logical root nameservers; each anycast across hundreds of physical servers.

### Public Resolvers
1.1.1.1 (Cloudflare), 8.8.8.8 (Google), 9.9.9.9 (Quad9). All anycast.

### CDN Edges
Cloudflare's edge IP for your domain might be one address; routes to PoP near client.

### AWS Global Accelerator
Customer gets 2 static anycast IPs. Anywhere on Internet → routes to AWS backbone → routes to chosen endpoint (ALB, NLB, EC2, EIP).

### AWS S3 Endpoints
S3 buckets accessible via global endpoint that anycasts to AWS edge locations.

## TCP and Anycast

Stateful TCP could theoretically break if routing shifts mid-flow.

Reality:
- Routing changes infrequent
- ISPs use stable ECMP (hash on 5-tuple)
- Most TCP connections survive
- For very long-lived: client reconnects acceptable

QUIC connection migration handles this gracefully.

## UDP and Anycast

Perfect fit. Single-packet exchanges (DNS):
- Each query independently routed
- No state between queries
- Routing change between queries OK

## How Anycast Withdraws

```
PoP A failing:
  Stops BGP announce
  Withdraws prefix from upstream
  ISPs update routes
  Clients now route to next-nearest PoP (B)
  ← Total convergence: seconds to minute
```

Much faster than DNS-based failover (which depends on TTLs).

## DDoS Absorption

Attacker sends 100 Tbps at anycast IP.
- Attack spreads across all PoPs (each absorbing a fraction)
- No single PoP overwhelmed
- Cloudflare claims 200+ Tbps total capacity

Versus unicast (one IP one location): 100 Tbps directly hammers one IP.

## Performance

Typical RTT improvements vs Internet path to single origin:
- US user → 10-30ms to nearest CDN PoP (vs 80-150ms to origin if far)
- EU user → 10-30ms
- Asia user → 10-30ms

Massive improvement for global services.

## Configuring Anycast (for you)

Most teams: don't run own anycast. Use:
- CDN (Cloudflare, CloudFront, Fastly)
- AWS Global Accelerator
- Cloud-provider DNS (Route 53)

Running your own:
- Get an ASN (~$500/year)
- Get IPs (PI or PA)
- Connect to multiple ISPs in multiple PoPs
- BGP everywhere

Significant cost; usually not worth it.

## Reading Anycast Behavior

```bash
# Different PoPs see different paths
ssh tokyo-vps "dig @1.1.1.1 google.com +stats"   # routes through Cloudflare Tokyo
ssh london-vps "dig @1.1.1.1 google.com +stats"  # London
```

Same IP, different responses (typically same content, different cache).

## Limitations

- **Stateful TCP across long sessions**: rare but possible breaks
- **Sticky sessions**: harder (no concept; each request may go elsewhere)
- **Local diagnostics**: hard to test specific PoP (use override-IP options if CDN supports)

## Multi-Anycast (HA)

Two distinct anycast IPs for redundancy:
- AWS Global Accelerator: provides 2 IPs
- Use both in DNS
- Client failover if one address unreachable

## Operating

```bash
# Trace path to anycast IP (see which PoP)
mtr 1.1.1.1

# Cloudflare provides looking-glass
curl http://1.1.1.1/cdn-cgi/trace
```

## Future

Anycast remains foundational. Combined with QUIC's connection migration: even more resilient.

## Interview Prep

**Mid**: "What's anycast?"

**Senior**: "Anycast + TCP — does it work?"

**Staff**: "Build a globally-distributed service. Anycast layer choices?"

## Next Topic

→ [T03 — Edge Computing](T03-Edge-Computing.md)
