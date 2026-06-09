# L03/C03 — DNS Deep Dive

## Chapter Overview

DNS is the most-overlooked critical infrastructure. It causes more outages than people realize. Senior+ engineers must understand resolvers, caching, propagation, and DNS-as-load-balancer patterns.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-DNS-Resolution.md) | DNS Resolution Flow (Recursive vs Iterative) | 1 hr |
| [T02](T02-Record-Types.md) | Record Types (A, AAAA, CNAME, MX, TXT, SRV, NS, SOA) | 0.5 hr |
| [T03](T03-Caching-TTLs.md) | DNS Caching, TTLs, and Why TTLs Lie | 1 hr |
| [T04](T04-DNSSEC.md) | DNSSEC | 0.5 hr |
| [T05](T05-DNS-Load-Balancing.md) | DNS as a Load Balancer (Route53, GeoDNS) | 1 hr |

## Resolution Flow

```
Client (stub resolver, e.g., glibc)
   │ 1. query (UDP 53)
   ▼
Recursive resolver (8.8.8.8, 1.1.1.1, /etc/resolv.conf)
   │ checks cache; if miss:
   ▼
.  (root nameservers, 13 of them, anycast)
   │ "ask the com TLD servers"
   ▼
.com (TLD nameservers)
   │ "ask example.com's NS servers"
   ▼
ns1.example.com  (authoritative)
   │ "A record: 93.184.216.34"
   ▼
back through resolver (caches), back to client
```

**Stub resolver** asks one resolver. **Recursive resolver** queries the chain iteratively.

## DNS Record Types

| Record | Purpose |
|---|---|
| A | IPv4 address |
| AAAA | IPv6 address |
| CNAME | Alias to another name |
| MX | Mail exchanger (priority + name) |
| TXT | Arbitrary text (SPF, DKIM, domain verification) |
| SRV | Service record (priority, weight, port, name) — used for SIP, XMPP, K8s headless services |
| NS | Authoritative nameservers for a domain |
| SOA | Start of Authority (zone metadata: serial, refresh, retry, expire) |
| PTR | Reverse DNS (IP → name) |
| CAA | Certificate Authority Authorization (who can issue certs) |
| ALIAS / ANAME | Apex CNAME (proprietary; Route 53 alias, Cloudflare CNAME flattening) |

## CNAME Rules (Subtle)

- A CNAME cannot coexist with other records at the same name
- A zone apex (e.g., `example.com`) CANNOT be a CNAME (RFC) — that's why ALIAS/Route53 alias exists
- Resolvers follow CNAMEs to A/AAAA records

## TTLs and Why They Lie

A TTL says "cache this for N seconds." But:

1. **OS resolvers** cache (varies)
2. **Browsers** cache (~30s–5min, often longer)
3. **Application** libraries cache (JVM caches forever by default — `networkaddress.cache.ttl`)
4. **CDN edge** caches
5. **NAT/CGNAT** boxes cache
6. **Recursive resolvers** may extend TTLs

So a 60-second TTL change can take an hour to fully propagate. Plan failovers accordingly.

### Lowering TTL Pre-Migration

When planning a DNS change, lower TTLs to 60s **at least 1 TTL period before** the change. So if current TTL is 1h, change to 60s 1h before the actual migration.

## DNS as Load Balancer

### Geographic Routing (GeoDNS)
- AWS Route 53 geolocation routing policies
- Cloudflare GeoIP
- Used for: latency optimization, compliance

### Weighted Routing
- Split traffic 70/30 between two stacks (canary)
- Route 53 weighted records

### Failover Routing
- Active/passive: only return passive's IP if active health checks fail
- Route 53 health checks

### Latency-Based Routing
- Return IP of nearest region by measured latency
- Route 53 latency policy

### Caveats
- TTLs lie — instant failover is impossible via DNS
- Some clients ignore TTLs (Java)
- Anycast is faster for true low-latency routing

## DNSSEC

Cryptographic signing of DNS records. Prevents spoofing/cache poisoning.

Chain of trust: root → TLD → your zone, each signed with DNSKEY/RRSIG records.

Reality: adoption is patchy. Larger orgs use it for high-value domains. Not a panacea.

## Production DNS Architecture

```
[Public DNS (Route 53, Cloudflare)]
        │
        ▼
[Edge layer (CDN, ALB)]
        │
        ▼
[Internal DNS (Route 53 private zone, CoreDNS in K8s)]
        │
        ▼
[Services]
```

K8s uses **CoreDNS** as cluster DNS:
- `svc.cluster.local` is the cluster domain
- Pods inherit `nameserver = cluster IP of CoreDNS`
- ndots:5 in `/etc/resolv.conf` causes search-domain explosion (covered in L13)

## Tools

```bash
dig +trace example.com           # full resolution path
dig @8.8.8.8 example.com         # query specific resolver
dig -x 8.8.8.8                   # reverse lookup
nslookup example.com
host example.com
getent ahosts example.com        # respects /etc/nsswitch
drill                            # alternative to dig
delv                             # DNSSEC validating
```

## Common Production Issues

- **TTL too long pre-migration** — extended outage during DNS swap
- **JVM caches forever** — pods don't pick up DNS changes
- **`search` domain explosion** in K8s — every internal lookup does 5+ queries
- **Resolver pinned to one IP** — that IP becomes a SPOF
- **Glue records out of sync** — recursive queries fail in weird ways
- **DNSSEC misconfiguration** — domain unreachable

## Interview Themes

- "Walk me through resolving www.google.com"
- "Why might a DNS change not propagate in expected time?"
- "Design DNS-based failover; what are the caveats?"
- "CoreDNS in K8s — how does it work?"
- "Why can't a zone apex be a CNAME?"
