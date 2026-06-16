# L03/C03/T04 — DNSSEC

## Learning Objectives

- Understand DNSSEC's purpose
- Recognize the chain of trust
- Know when it matters and when it doesn't

## What DNSSEC Solves

DNS originally had NO authentication. An attacker could:
- Spoof responses (cache poisoning)
- Inject malicious IPs
- Redirect traffic

DNSSEC adds cryptographic signatures so resolvers can verify responses came from the authoritative source.

## How It Works

Each zone:
1. Generates a signing key pair (ZSK — Zone Signing Key)
2. Signs every record set (RRSet) → produces RRSIG records
3. Parent zone publishes a hash of your public key (DS record)
4. Root key is in resolvers' trust store

```
Root ─── publishes DS for .com ─── verifies via DNSKEY for root (trust anchor)
.com ─── publishes DS for example.com ─── verifies via root signing
example.com ─── signs all records (RRSIG) ─── verifies via DS at .com level
```

If any link broken: validation fails.

## Records

- **DNSKEY**: public key for the zone
- **RRSIG**: signature over a record set
- **DS**: hash of child zone's DNSKEY (at parent level)
- **NSEC / NSEC3**: prove non-existence (the "X doesn't exist" record, signed)

## Validation

Resolver:
1. Get answer (e.g., A record + RRSIG)
2. Get DNSKEY for the zone
3. Verify RRSIG using DNSKEY
4. Verify DNSKEY using DS at parent
5. Verify DS using parent's DNSKEY
6. Walk up to root (trust anchor)

If all sign: AD (Authentic Data) flag set.

## Reality

DNSSEC adoption is patchy. Why:
- **Operational complexity**: key management, signing, rollover
- **Larger response sizes**: more often TCP fallback
- **Many domains don't have it**: <10% of domains signed
- **Resolvers don't all validate**: some skip
- **Browsers don't enforce**: usually don't check AD flag

## When to Care

| Need | DNSSEC matters |
|---|---|
| High-value domain (banking, government) | Yes |
| Critical infrastructure | Yes |
| Defense in depth | Worth considering |
| Small site | Optional |
| Internal corp DNS | Rarely matters |

## Key Rollover

Periodically replace keys:
- **ZSK rollover** (Zone Signing Key): frequent, automated
- **KSK rollover** (Key Signing Key): rare, coordination with registrar

If rollover messed up → zone fails validation → "domain doesn't exist" for users.

## Pre-Provisioning Failure Modes

Famous DNSSEC outages:
- Slack 2021 — DNSSEC misconfiguration
- Various banks — key expired
- Microsoft — multiple incidents

DNSSEC adds availability risk in exchange for integrity gain.

## DoH and DoT

Encryption of the DNS query itself (not the answer):
- **DNS over HTTPS (DoH)**: HTTPS to resolver (Cloudflare 1.1.1.1, Google 8.8.8.8)
- **DNS over TLS (DoT)**: TCP+TLS to resolver
- **DNS over QUIC (DoQ)**: emerging

These prevent:
- ISP snooping
- Public-network ARP/DNS spoofing
- Censorship by IP blocking

But they DON'T prevent:
- Spoofed responses from the resolver itself (DNSSEC covers that)
- Resolver logging

Best practice: DoH/DoT + DNSSEC validation = comprehensive privacy + integrity.

## Configuring (Cloud)

### Route 53
- Enable DNSSEC at hosted zone level
- AWS handles key management
- Configure DS at registrar

### Cloudflare
- DNSSEC toggle in dashboard
- Cloudflare handles everything

### Self-hosted (BIND)
- `dnssec-policy auto;` in zone config
- Tools handle signing + rollover

## Monitoring

DNSViz: https://dnsviz.net/ — visualize DNSSEC chain for any domain.

```bash
dig +dnssec example.com         # show DNSSEC records
delv example.com                # validating resolver
dig +cd example.com             # check disabled (bypass validation)
```

## Common Mistakes

- **Letting a KSK or signature expire**: RRSIGs and keys have expiry. An expired signature makes the whole zone fail validation — validating resolvers return SERVFAIL and the domain effectively "disappears" (the Slack/bank-style outages).
- **Botching the chain of trust at the parent**: enabling signing without publishing the matching DS record at the registrar (or publishing a stale DS after a KSK rollover) breaks validation while the zone looks fine locally.
- **Confusing DNSSEC with encryption**: DNSSEC authenticates answers (integrity), it does *not* encrypt queries. Privacy needs DoH/DoT/DoQ; the two solve different problems.
- **Assuming clients enforce it**: most browsers don't check the AD flag. DNSSEC protects validating *resolvers*, not necessarily the end application — defense in depth, not a silver bullet.
- **Ignoring response-size growth**: signatures inflate responses, increasing TCP fallback and amplification-attack surface. Firewalls that block TCP/53 or large UDP break signed zones.
- **Rolling keys without overlap**: removing the old DNSKEY before resolvers' cached RRSIGs expire causes transient validation failures. Honor TTLs during rollover.

## Best Practices

- **Automate key management and rollover** (Route 53 / Cloudflare managed DNSSEC, or BIND `dnssec-policy auto`) — manual signing and rollovers are the leading cause of DNSSEC outages.
- **Monitor signature expiry and the DS chain proactively**; alert well before RRSIGs expire and validate the chain with DNSViz after every key change.
- **Combine DNSSEC with DoH/DoT** for integrity *and* privacy — they're complementary, not alternatives.
- **Allow TCP/53 and large EDNS UDP responses** end-to-end so signed answers aren't truncated or dropped.
- **Stage KSK rollovers with the registrar** and overlap old/new keys across cached-TTL windows to avoid validation gaps.

## Quick Refs

DNSSEC records: **DNSKEY** (zone public key) · **RRSIG** (signature over an RRset) · **DS** (hash of child DNSKEY, published at parent) · **NSEC/NSEC3** (signed proof of non-existence). Validation walks RRSIG→DNSKEY→DS up to the root trust anchor; success sets the **AD** flag.

DoH/DoT/DoQ encrypt the *query*; DNSSEC authenticates the *answer* — use both.

```bash
dig +dnssec example.com        # show RRSIG/DNSKEY/DS records
delv example.com               # validating lookup (reports "fully validated")
dig +cd example.com            # checking disabled — bypass validation to compare
dig DS example.com             # DS record at the parent (delegation)
# Visualize the full chain:  https://dnsviz.net/
```

## Interview Prep

**Mid**: "What is DNSSEC?"

**Senior**: "Why isn't DNSSEC universally deployed?"

**Staff**: "Trade-offs of enabling DNSSEC on a high-traffic domain?"

## Next Topic

→ [T05 — DNS as a Load Balancer](T05-DNS-Load-Balancing.md)
