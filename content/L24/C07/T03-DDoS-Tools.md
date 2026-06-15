# L24/C07/T03 — AWS Shield, Cloudflare DDoS Protection

## Learning Objectives

- Use DDoS services
- Compare

## AWS Shield

Standard (free):
- All AWS users
- Basic protection
- Volumetric

Advanced (paid):
- $3000/month base
- 24/7 SRT (Shield Response Team)
- Cost protection
- Reporting
- WAF included

## Setup

```bash
aws shield-advanced subscribe
aws shield-advanced create-protection --resource-arn arn:aws:ec2:...
```

For: enterprise.

## CloudFront + Shield

```
Internet → CloudFront (Shield) → Origin
```

CloudFront absorbs.

## Cloudflare

All plans get DDoS protection:
- Free: basic
- Pro: advanced
- Enterprise: highest

## Cloudflare Spectrum

L4 for non-HTTP:
- SSH, Minecraft, etc.
- DDoS protected

## Akamai Prolexic

Enterprise scrubbing:
- DDoS-as-a-service
- BGP diversion
- Massive capacity

## Google Cloud Armor

GCP DDoS:
- Adaptive Protection (ML)
- WAF rules
- Bot management

## Imperva / Radware

Other commercial.

## Choose

| | AWS Shield Advanced | Cloudflare | Akamai |
|---|---|---|---|
| Tier | $3k/mo+ | free + paid | enterprise |
| Coverage | AWS resources | global edge | global edge |
| WAF | included | included | included |
| Bot mgmt | partial | yes | yes |

For: most: Cloudflare.
For AWS-heavy: Shield.
For enterprise: Akamai.

## Reduce Attack Surface

- Hide origin IP (use CDN)
- Restrict ports
- VPC private
- WAF rules

## Origin Cloaking

Origin IP not public:
- Only CDN knows
- Whitelist CDN IPs at origin

For: stop direct attacks.

## Real Attacks

### GitHub Memcached
1.35 Tbps; mitigated by Akamai.

### AWS 2020
2.3 Tbps; mitigated.

### Cloudflare 71 Mrps
2023; auto-mitigated.

## Detection

CDN sees:
- Sudden volume
- Geographic anomaly
- Rate spike

Auto-trigger mitigation.

## Cost Protection

AWS Shield Advanced:
- Refund DDoS-related costs (EC2, ELB)

Cloudflare:
- Unlimited mitigation included

For: financial protection.

## SRT

AWS Shield Advanced:
- 24/7 expert team
- Mitigation help
- Forensics

For: complex attacks.

## Practice

- Game day with simulated DDoS
- Verify defenses
- Build runbook

## Best Practices

- CDN front everything public
- WAF + Bot management
- DDoS protection enabled
- Origin hidden
- Monitor + alerts
- Runbook

## Common Mistakes

- Origin exposed
- No protection
- Don't test
- No runbook (when attack: chaos)

## Quick Refs

```
AWS Shield Std: free
AWS Shield Advanced: $3k/mo+; SRT
Cloudflare: included all plans
Akamai: enterprise scrubbing
GCP: Cloud Armor

Always:
- CDN / proxy
- Hide origin
- Rate limit
- Monitor
```

## Interview Prep

**Mid**: "DDoS services."

**Senior**: "Pick service."

**Staff**: "DDoS strategy."

## Next Topic

→ Move to [L25 — Chaos Engineering & Resilience Testing](../../L25/README.md)
