# L08/C09/T04 — WAF & Shield

## Learning Objectives

- Use WAF for L7 protection
- Distinguish Shield Standard vs Advanced

## WAF (Web Application Firewall)

Layer 7 firewall for HTTP/HTTPS:
- SQL injection
- XSS
- Bad bots
- Rate limiting
- Country block
- Custom rules

## Where

Attach to:
- CloudFront
- API Gateway (REST)
- ALB
- AppSync
- App Runner

NOT directly attached to NLB (L4); use CloudFront/ALB in front.

## Web ACL

Rules container. Rules ordered; first matching wins.

```yaml
WebACL:
  - Rule 1: BlockSQLi
  - Rule 2: RateLimit per IP
  - Rule 3: AWS managed core
  - Default: Allow
```

## Rule Types

- **Custom**: your conditions
- **Rate-based**: per-IP rate
- **AWS Managed**: AWS-curated
- **Marketplace**: third-party

## AWS Managed Rules

Pre-built rule groups:
- Core (CRS): general web attacks
- Known bad inputs
- SQLi
- Linux / Windows
- POSIX
- Bot Control (paid)
- Account Takeover Prevention (ATP, paid)

```yaml
ManagedRuleGroup:
  Vendor: AWS
  Name: AWSManagedRulesCommonRuleSet
```

Free + paid groups.

## Custom Rules

```yaml
Rules:
  - Name: BlockIfCountryX
    Priority: 0
    Action: Block
    Statement:
      GeoMatchStatement:
        CountryCodes: [CN, RU]
```

JSON-like; visualizer in console.

## Rate-Based

```yaml
Rules:
  - Name: RateLimit
    Priority: 1
    Statement:
      RateBasedStatement:
        Limit: 2000
        AggregateKeyType: IP
    Action:
      Block: {}
```

2000 requests in 5 min from same IP → block.

## Logging

Send all matched requests to:
- CloudWatch Logs
- S3 (via Firehose)
- Kinesis Data Firehose

For analysis (Athena query).

## Common Rules

### SQL Injection
Managed: `AWSManagedRulesSQLiRuleSet`.

### XSS
In Core (`AWSManagedRulesCommonRuleSet`).

### Rate Limit Login
```yaml
Statement:
  AndStatement:
    Statements:
      - ByteMatchStatement: ... # path == /login
      - RateBasedStatement: ...
```

### Country Block
```yaml
GeoMatchStatement:
  CountryCodes: [CN, IR, KP]
```

### Bot Block
AWS Managed Bot Control (paid).

## Tarpit / CAPTCHA

CAPTCHA action: serve CAPTCHA page; valid attempts pass.

Challenge action: client must solve cryptographic puzzle.

For: bots / abuse.

## Pricing

- $5/mo per Web ACL
- $1/mo per rule
- $0.60 per million requests
- Managed rules: some free, some paid extra

For typical 10-rule ACL + 10M requests: ~$15/mo + $6 = $21/mo.

## Shield

DDoS protection.

### Shield Standard
- Free
- Auto-enabled
- Protects against common L3/L4 DDoS
- For all CloudFront, ALB, NLB, EC2, Route 53

### Shield Advanced
- $3,000/mo per organization + data fees
- Comprehensive DDoS
- 24/7 DDoS response team
- Cost protection (refund if scale-up needed)
- Custom mitigations
- Visibility into attacks

For: high-profile / mission-critical targets.

## DDoS Patterns

### L3/L4 (volumetric)
- UDP flood, SYN flood
- Shield Standard handles most

### L7 (application)
- HTTP flood, slow loris
- WAF rate-based handles most
- Shield Advanced for severe

## Use With CloudFront

Place WAF on CloudFront:
- Filtering at edge (closest to attacker)
- Shield protects CloudFront infra
- Origin (ALB / S3) protected by exclusion

For static content + WAF: minimize attack surface.

## Tuning

False positives: legitimate requests blocked.

Use Count action first:
```yaml
Action: Count   # log; don't block
```

Run for a few days. Review false positives. Then switch to Block.

## CAPTCHA

CAPTCHA action: present puzzle; pass on solve.

Used for:
- Suspicious requests
- Login pages
- High-value endpoints

User experience tradeoff.

## Bot Control

AWS Managed: detects bots:
- Verified search engines (allow)
- Crawlers, scrapers (block / CAPTCHA)
- Distributed (advanced)

$10/M requests + $2/mo. Worth for public sites.

## Account Takeover Prevention (ATP)

Specific for login pages:
- Detect credential stuffing
- Compromised credentials
- Bot logins

Costs more; for accounts of value.

## WAF for API Gateway

WAF on REST API (not HTTP API). Or place HTTP API behind CloudFront with WAF.

## Multi-Region Web ACL

Web ACL is regional. For multi-region:
- Per-region ACL
- Or CloudFront ACL (global; covers all CF distributions)

## Common Mistakes

- Block before testing (Count first)
- Rate limit too low (legit traffic blocked)
- No logging (can't tune)
- Rules misordered (less specific blocks more specific)
- WAF without Shield Advanced expectation (DDoS still hits)

## Best Practices

- Managed rules baseline
- Custom rules for app-specific
- Rate-based on /login, /signup, /api
- Logs to S3
- Count mode initially; tune
- Geo restriction if applicable
- WAF on CloudFront for static

## Monitoring

CloudWatch:
- AllowedRequests
- BlockedRequests
- CountedRequests
- Per-rule metrics

Alert on:
- Sudden block spike
- Bypass attempt patterns

## Bypassing WAF

If origin reachable directly (not just through CloudFront): WAF can be bypassed.

Restrict origin access:
- ALB SG: only CloudFront IPs (use AWS-managed prefix list)
- S3 bucket policy: only OAC

## Visibility

WAF Dashboard / CloudWatch:
- Top blocked
- Top sources
- Top rules

For investigation.

## Logs Analysis

Athena over WAF logs in S3:
```sql
SELECT terminatingRuleId, COUNT(*) 
FROM waf_logs 
WHERE action = 'BLOCK'
GROUP BY 1
```

Top blocking rules; tune.

## Quick Refs

```bash
# Create Web ACL
aws wafv2 create-web-acl --name myACL --scope REGIONAL --default-action Allow={} --rules ...

# Associate
aws wafv2 associate-web-acl --web-acl-arn ... --resource-arn arn:aws:elasticloadbalancing:...

# Get metrics
aws cloudwatch get-metric-statistics --namespace AWS/WAFV2 --metric-name BlockedRequests ...
```

## Interview Prep

**Mid**: "WAF use cases."

**Senior**: "Tune WAF for SaaS app."

**Staff**: "DDoS strategy."

## Next Topic

→ Move to [L08/C10 — Messaging & Streaming](../C10/README.md)
