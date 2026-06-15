# L03/C03/T01 — DNS Resolution Flow (Recursive vs Iterative)

## Learning Objectives

- Trace a DNS query end-to-end
- Distinguish recursive vs iterative resolution
- Identify each resolver type

## Players

- **Stub resolver**: in your OS (`getaddrinfo`, glibc), asks ONE resolver
- **Recursive resolver**: ISP's DNS (or 8.8.8.8, 1.1.1.1); does the actual lookup work
- **Root servers**: 13 logical names (anycasted); know TLD locations
- **TLD servers**: `.com`, `.org`; know which servers are authoritative for each domain
- **Authoritative servers**: own the actual records for a domain

## Resolution Flow

```
Browser asks: "what is www.example.com?"

Stub resolver → Recursive resolver (8.8.8.8)
                   │
                   ├─ Cache? Yes → return
                   ├─ No: ask Root: "where's .com?"
                   │      Root → "Ask a.gtld-servers.net (and 12 others)"
                   ├─ Ask .com TLD: "where's example.com?"
                   │      TLD → "Ask ns1.example.com"
                   ├─ Ask ns1.example.com: "what is www.example.com?"
                   │      Auth → "93.184.216.34"
                   └─ Cache + return
```

## Recursive vs Iterative

- **Iterative**: server answers what it knows; client follows referrals
- **Recursive**: server does all the work; client gets final answer

Modern: stub → recursive (which acts recursive on behalf of client and iterative when talking to root/TLD/auth).

## Caching

Every layer caches:
- Browser
- OS (glibc nscd, systemd-resolved)
- Recursive resolver
- TTL controls how long

A repeated query usually hits a cache; no chain traversal.

## Public Resolvers

| Provider | IP | Notes |
|---|---|---|
| Google | 8.8.8.8, 8.8.4.4 | Common; logs queries |
| Cloudflare | 1.1.1.1, 1.0.0.1 | Privacy-focused |
| Quad9 | 9.9.9.9 | Malware filtering |
| OpenDNS | 208.67.222.222 | Family filtering |

## Authoritative Server

The server that owns the zone:
- Configured in registrar (NS records at TLD level)
- Examples: Route 53, NS1, Cloudflare, BIND on-prem
- Returns answers without cache; configured by you

## DNS Over TCP

If response > 512 bytes (or 1232 with EDNS0), DNS falls back to TCP.
- Zone transfers (AXFR/IXFR) always TCP
- DNSSEC signatures often push over UDP limit

## Reading dig Output

```bash
$ dig +trace www.example.com

;; QUESTION SECTION:
www.example.com.        IN  A

.                 IN  NS  a.root-servers.net.
com.              IN  NS  a.gtld-servers.net.
example.com.      IN  NS  ns1.example.com.
www.example.com.  IN  A   93.184.216.34
```

`+trace` shows iterative resolution from root.

## Common Tools

```bash
dig www.example.com                # query default resolver
dig @8.8.8.8 www.example.com       # specific resolver
dig +trace www.example.com         # show full path
dig +short www.example.com         # just the answer
nslookup example.com               # older, simpler
host example.com                   # simplest
getent ahosts example.com          # uses nsswitch.conf (db, files, dns order)
```

## Common Issues

- **Local cache stale**: `systemctl restart systemd-resolved` or browser flush
- **Wrong /etc/resolv.conf**: hand-edited then NetworkManager overwrites
- **Glibc caches forever (Java too)**: JVM `networkaddress.cache.ttl=60`
- **Search domain explosion in K8s**: ndots:5 causes many queries

## Common Mistakes

- **Hand-editing `/etc/resolv.conf`**: NetworkManager / systemd-resolved / cloud-init regenerate it on the next event, silently reverting your change. Edit the managing tool's config instead.
- **Assuming the stub resolver does the recursion**: the OS stub asks *one* recursive resolver, which does the iterative walk (root → TLD → authoritative). Mixing up these roles misdiagnoses where a lookup actually fails.
- **Expecting `dig` to mirror the application's result**: `dig` talks straight to a resolver and ignores `nsswitch.conf`, `/etc/hosts`, and glibc/JVM caches. Use `getent ahosts` to see what the app's resolver path returns.
- **Forgetting DNS can use TCP**: responses over 512 bytes (or the EDNS0 size, default 1232) and all zone transfers (AXFR/IXFR) use TCP. Firewalls that allow only UDP/53 break large/DNSSEC answers.
- **Misreading K8s `ndots:5`**: short names get the search list appended first, generating several NXDOMAIN round-trips before the real query. A trailing dot (FQDN) or lower `ndots` avoids the storm.
- **Trusting a single resolver during an incident**: caches diverge. Always cross-check `@8.8.8.8`, `@1.1.1.1`, and the authoritative server before concluding "the record is wrong."

## Best Practices

- **Query the authoritative server directly** when validating a change (`dig @ns1.example.com ...`) to bypass every cache between you and the source of truth.
- **Use `dig +trace`** to follow resolution from the root and pinpoint which delegation (root, TLD, or authoritative) is broken.
- **Set application/runtime DNS TTLs explicitly** — especially the JVM (`networkaddress.cache.ttl`), which caches forever by default and ignores record TTL.
- **In Kubernetes, FQDN-qualify external names** (trailing dot) or tune `ndots` to avoid search-domain query amplification against CoreDNS.
- **Keep DNS observable**: monitor query rate, resolution latency, and NXDOMAIN rate so cache-staleness and delegation breakage show up before users report them.

## Quick Refs

Resolution chain: `stub (OS) → recursive resolver → root → TLD → authoritative`. Each layer caches per TTL. UDP/53 by default; TCP/53 for responses >512B (or EDNS size) and zone transfers.

Public resolvers: Google `8.8.8.8`/`8.8.4.4` · Cloudflare `1.1.1.1` · Quad9 `9.9.9.9` (malware filtering) · OpenDNS `208.67.222.222`.

```bash
dig www.example.com                 # default resolver, A record
dig @8.8.8.8 www.example.com        # query a specific resolver
dig @ns1.example.com example.com    # ask the authoritative server directly
dig +trace www.example.com          # full iterative path from root
dig +short www.example.com          # just the answer
getent ahosts example.com           # what the app's resolver path returns (nsswitch)
host example.com                     # quick lookup
resolvectl status                    # systemd-resolved config + per-link servers
```

## Interview Prep

**Junior**: "Walk through DNS resolution for www.google.com."

**Mid**: "Recursive vs iterative — explain."

**Senior**: "Why does DNS sometimes fall back to TCP?"

**Staff**: "Pod can't resolve external hosts. Walk through diagnosis."

## Next Topic

→ [T02 — Record Types](T02-Record-Types.md)
