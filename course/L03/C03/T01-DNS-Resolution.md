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

## Interview Prep

**Junior**: "Walk through DNS resolution for www.google.com."

**Mid**: "Recursive vs iterative — explain."

**Senior**: "Why does DNS sometimes fall back to TCP?"

**Staff**: "Pod can't resolve external hosts. Walk through diagnosis."

## Next Topic

→ [T02 — Record Types](T02-Record-Types.md)
