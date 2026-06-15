# L03/C07/T04 — BGP and Anycast

## Learning Objectives

- Understand BGP fundamentals
- Recognize Internet routing
- Apply anycast for global services

## BGP Basics

Border Gateway Protocol. The Internet's "policy routing protocol."

- Connects Autonomous Systems (ASes)
- Each AS has an ASN (e.g., 16509 = Amazon)
- iBGP within an AS; eBGP between ASes
- ~110,000 ASes on the Internet

## How BGP Works

ASes advertise prefixes they own:
```
AS 16509 announces: 52.94.0.0/16 reachable through me
```

Neighbors hear; share with their neighbors.

Each AS receives many paths to same prefix; picks one based on:
1. Local preference (you decide)
2. Shortest AS_PATH
3. MED (Multi-Exit Discriminator)
4. eBGP over iBGP
5. Tie-breakers

## Path Attributes

- **AS_PATH**: list of ASes traversed (prevent loops)
- **NEXT_HOP**: next router IP
- **LOCAL_PREF**: prefer one path over another (internal preference)
- **MED**: suggest preferred path to upstream
- **COMMUNITY**: tags for policy

## Why BGP Causes Outages

- **Hijacks**: AS advertises prefixes not theirs
- **Leaks**: AS advertises customer's prefixes upstream
- **Configuration errors**: typo cascades globally
- **No authentication by default**

Famous outages:
- Facebook 2021 (BGP withdrew their prefixes; site disappeared)
- Cloudflare 2019 (third-party leak)
- YouTube 2008 (Pakistan hijack)

## RPKI

Resource Public Key Infrastructure. Cryptographically validate origin.
- AS X says "I'm authorized to announce prefix Y"
- Other ASes can verify
- Slowly being deployed; helps but not universal

## BGP in AWS

AWS runs BGP on:
- Direct Connect VIFs
- VPN tunnels
- TGW peering

Your on-prem advertises your prefixes; AWS advertises VPC CIDRs.

## Anycast

Same IP advertised from MANY locations. Routing decides which one (typically nearest).

### Use Cases

| Service | Anycast IP |
|---|---|
| DNS root servers | 13 logical names; each anycasted |
| Cloudflare 1.1.1.1 | Public DNS |
| Google 8.8.8.8 | Public DNS |
| AWS Global Accelerator | Customer anycast IPs |
| AWS CloudFront | CDN edge IPs |
| Cloudflare CDN | Edge IPs |
| Many CDNs | Edges |

### Benefits
- Sub-100ms RTT from anywhere
- Built-in DDoS absorption (load spreads across PoPs)
- Failover (withdraw advertisement from failing PoP → routing shifts)

### Limitations
- Stateful connections (TCP): routing changes can break flows
- Modern: most TCP connections survive thanks to route stability
- UDP (DNS, QUIC): naturally OK with re-routing

## How Anycast Works

```
Cloudflare announces 1.1.1.1 from 300+ PoPs worldwide
Each PoP advertises via eBGP to nearby ISPs
Each ISP sees: shortest AS_PATH to 1.1.1.1 → forwards there
Client packets follow

Withdraw advertisement from a PoP (planned or failure):
ISPs update routing tables
Clients now reach nearest other PoP
```

## TCP Survival with Anycast

A change in routing mid-flow could break TCP. In practice:
- Routing changes infrequent enough that most flows survive
- ISPs use hash-based ECMP that's stable within a session
- For HTTP: connection close → retry → goes to new PoP

QUIC connection migration is even better for this.

## Multipath Anycast

Multiple PoPs respond from same path. ECMP distributes packets.
- Each TCP flow consistently hashed to one path
- Survives single-PoP failure

## When YOU might use BGP

For most teams: never directly. BGP runs in your cloud provider's network.

You DO use BGP if:
- Running on-prem with Direct Connect
- Multi-homed (multiple ISPs)
- Large enterprise WAN
- Building DDoS-resilient infrastructure

## AWS Global Accelerator

- Customer-facing anycast IPs (no need to own AS)
- Traffic enters at edge; routes via AWS backbone
- Lower jitter, faster failover than DNS
- Endpoints in multiple AWS regions

## Operating

```bash
# Check route to a target
mtr 1.1.1.1                  # see path
whois 1.1.1.1                # who owns it (Cloudflare AS 13335)

# BGP looking glasses (test from various ASes)
# https://lg.he.net/ — Hurricane Electric's looking glass
```

## Performance

Anycast typically:
- Sub-30ms RTT from major cities to nearest PoP
- Better than unicast for global services
- Critical for DNS (UDP single-packet exchange)

## Common Mistakes

- **Assuming BGP is authenticated** — by default it isn't; a wrong or malicious announcement (hijack/leak) propagates globally. Origin validation (RPKI) is opt-in.
- **A more-specific prefix wins** — announcing a `/24` overrides someone's `/16` regardless of AS-PATH; this is exactly how hijacks and accidental leaks happen.
- **Withdrawing all routes by accident** — Facebook's 2021 outage was a BGP withdrawal; if your prefixes disappear, so does your service *and* often your out-of-band access.
- **Expecting anycast to do stateful load balancing** — anycast picks a PoP by routing, not by load; it has no session stickiness and no health-based weighting on its own.
- **Fearing TCP breaks on anycast** — in practice routes are stable enough (5-tuple-hashed ECMP) that flows survive; designing around imaginary breakage wastes effort. QUIC migration makes it a non-issue.

## Best Practices

- **Use a managed anycast layer** (CloudFront, Cloudflare, AWS Global Accelerator) rather than running your own AS unless you truly need it — Global Accelerator gives you 2 anycast IPs without owning an ASN.
- **Deploy and validate RPKI ROAs** for prefixes you originate, and prefer upstreams that drop RPKI-invalid routes — it's the cheapest hijack defense.
- Control path selection with the right knob: **LOCAL_PREF** for your own inbound/outbound preference, **AS-PATH prepending / MED** to influence how others reach you.
- **Monitor your prefixes externally** (BGPalerter, looking glasses, RIPEstat) so you find out about a hijack or withdrawal from outside your network, not from customers.
- Lean on anycast's strengths: **fast failover by withdrawing a PoP** and **DDoS spread across PoPs** — design health checks to withdraw a sick PoP automatically.

## Quick Refs

BGP best-path order (simplified): **highest LOCAL_PREF → shortest AS_PATH → lowest MED → eBGP over iBGP → lowest IGP cost → tie-breakers.**

| Attribute | Direction | Effect |
|---|---|---|
| LOCAL_PREF | your network, outbound | prefer one egress path (highest wins) |
| AS_PATH | inbound (via prepend) | longer path = less preferred |
| MED | suggest to neighbor | lower = preferred entry point |
| COMMUNITY | tag | drive peer/upstream policy |

```bash
# Path to an anycast IP (which PoP am I hitting?)
mtr -n 1.1.1.1

# Who owns / which AS announces this IP?
whois 1.1.1.1 | grep -iE "origin|orgname|netname"

# Cloudflare's "which PoP" debug endpoint
curl -s http://1.1.1.1/cdn-cgi/trace | grep -E '^(colo|loc)='

# Public looking glass to see routes from other ASes:
#   https://lg.he.net/   (Hurricane Electric)
```

Anycast fit: **UDP/DNS/QUIC** = ideal (stateless or migration-aware); **long-lived stateful TCP** = usually fine, reconnect on the rare route change.

## Interview Prep

**Mid**: "What is BGP?"

**Senior**: "How does anycast work?"

**Staff**: "Why does Cloudflare DNS resolve fast worldwide?"

**Staff**: "Design DDoS-resilient global service."

## Next Topic

→ [T05 — SD-WAN](T05-SDWAN.md)
