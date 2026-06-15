# L20/C03/T02 — DAST (OWASP ZAP, Burp)

## Learning Objectives

- Use DAST tools
- Test running app

## DAST

Dynamic Application Security Testing:
- Runs against deployed app
- Black-box (or grey-box)
- Find runtime vulns

## When

- Pre-prod (staging)
- Pre-launch
- Continuous in CI

## Tools

### OWASP ZAP
Open source:
```bash
docker run owasp/zap2docker-stable zap-baseline.py -t https://staging.example.com
```

Free; community.

### Burp Suite
Commercial (PortSwigger):
- Pro: deep analysis
- Community: basic

Industry standard for pen tests.

### Acunetix
Commercial; scanner.

### Nessus
Network scanner; some app.

### Nuclei
Template-based; community:
```bash
nuclei -u https://staging.example.com -t cves/
```

## ZAP Modes

### Baseline
Quick scan (~ 1 min):
```bash
zap-baseline.py -t URL
```

For: CI; surface-level.

### Full
Deep scan (~ hours):
```bash
zap-full-scan.py -t URL
```

For: pre-launch.

### Authenticated
Login + scan:
```bash
zap-baseline.py -t URL -j -z "-config replacer.full_list(0).description=auth1 ..."
```

For: app behind login.

## Common Findings

- XSS
- SQL injection
- Open redirect
- Missing CSRF token
- Insecure cookies
- Headers missing (CSP, HSTS)
- Outdated TLS

## CI Integration

```yaml
- name: ZAP
  uses: zaproxy/action-baseline@v0.10.0
  with:
    target: 'https://staging.example.com'
    fail_action: true
```

## Authentication

For protected endpoints:
- Provide session token
- Login script
- Browser automation

For: full coverage.

## API DAST

For APIs:
- OpenAPI / Swagger spec
- Test each endpoint

```bash
zap-api-scan.py -t openapi.json -f openapi
```

## Limits

DAST:
- No source code visibility
- Only what reachable
- Slow

For: complement with SAST.

## Burp Workflow

Manual pen test:
1. Spider site
2. Active scan
3. Manual probe
4. Report

For: deep analysis.

## CI vs Manual

CI: quick scan; catch obvious.
Manual: deep + creative.

Both needed.

## Reports

- HTML
- XML
- JSON
- SARIF

## False Positives

DAST often:
- Flag harmless
- Miss real

For: tune + manual review.

## Authenticated Scan Workflow

```
1. Login API call (get session)
2. Set session cookie in ZAP
3. Crawl protected pages
4. Active scan
```

For: full app coverage.

## Headers

ZAP / Burp check:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security
- Content-Security-Policy

Missing: warning.

## CSP

Strong CSP prevents XSS:
```
Content-Security-Policy: default-src 'self'
```

DAST verifies.

## Cookie Security

```
Set-Cookie: session=...; Secure; HttpOnly; SameSite=Strict
```

DAST checks.

## Best Practices

- ZAP in CI (baseline)
- Manual pen test annually
- Authenticated scans
- API spec scans
- Tune false positives

## Common Mistakes

- Skip authenticated (miss most)
- Block on everything (noise)
- One-time (no continuous)
- Skip annual pen test

## Cost

- ZAP: free
- Burp Pro: ~$400/year/user
- Acunetix: enterprise $$$

## Quick Refs

```bash
# ZAP baseline
zap-baseline.py -t URL

# ZAP full
zap-full-scan.py -t URL

# ZAP API
zap-api-scan.py -t openapi.json -f openapi

# Nuclei
nuclei -u URL -t cves/
```

## Interview Prep

**Junior**: "What is DAST?" — Dynamic Application Security Testing probes a running application from the outside (like an attacker), finding runtime issues such as injection, auth flaws, and misconfigurations without access to source.

**Mid**: "SAST vs DAST — when do you use each?" — SAST reads code statically and finds issues early but with false positives; DAST tests the running app and confirms exploitable behavior with fewer false positives but later and with less code coverage — they're complementary, not substitutes.

**Senior**: "How do you run DAST in CI/CD?" — Deploy to an ephemeral staging environment, run authenticated scans against it (seeded credentials, API specs for coverage), and gate on new high-severity findings; full deep scans run on a schedule rather than every PR because they're slow.

**Staff**: "What's the trade-off of DAST coverage vs pipeline speed, and how do you address it?" — Full DAST is too slow to block every deploy, so split into fast smoke scans inline and deep scans out-of-band, drive coverage with API specs and crawl seeds, and combine with IAST/SAST so each technique covers the others' blind spots.

## Next Topic

→ [T03 — IAST & RASP](T03-IAST-RASP.md)
