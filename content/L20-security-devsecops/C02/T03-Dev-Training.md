# L20/C02/T03 — Developer Security Training

## Learning Objectives

- Train devs effectively
- Build security culture

## Why

Most vulns: developer mistakes.

Training:
- Awareness
- Skills
- Culture

## Topics

- OWASP Top 10
- Secure coding
- Crypto basics
- Auth/Z
- Input validation
- Secrets handling
- Threat modeling

## OWASP Top 10 (2021)

1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfig
6. Vulnerable Components
7. Authentication Failures
8. Software & Data Integrity
9. Logging & Monitoring Failures
10. SSRF (Server-Side Request Forgery)

Cover each.

## Formats

### Annual Training
Mandatory; 1-2 hours.

For: compliance.

### Workshops
Per-topic deep dive.

### Lunch & Learn
Optional; relevant.

### Capture The Flag
Hands-on hacking.

For: engagement.

### Tabletop
Walk through scenarios.

## Just-in-Time Training

After incident:
- Postmortem references training
- Fill knowledge gap

For: relevant.

## Onboarding

New hire:
- Security training week 1
- Sign code of conduct
- Mentor introduction

For: start right.

## Champions

Per team:
- Security champion
- Liaison to security team
- Internal expert
- Promotes culture

For: scale security team.

## Resources

- OWASP cheat sheets
- PortSwigger Web Security Academy (free)
- HackTheBox / TryHackMe
- Internal wiki

## Internal Wiki

Per topic:
- What it is
- How attackers exploit
- How to prevent
- Code examples

For: reference.

## Code Review

Security as review criterion:
- Security mind-frame
- Checklist
- Tools assist

## Engineering Examples

### SQL Injection
```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

Drill home.

### Hard-Coded Secrets
```python
# Bad
API_KEY = "abc123"

# Good
API_KEY = os.environ["API_KEY"]
```

### Insecure Crypto
```python
# Bad
import hashlib
h = hashlib.md5(password.encode()).hexdigest()

# Good
from passlib.hash import argon2
h = argon2.hash(password)
```

## Measure

Pre/post training:
- Quiz score
- Survey
- CVE rate over time

For: track impact.

## Gamification

- Points for finding vulns
- Leaderboards
- Bug bounty

For: engagement.

## Real Examples

### Google
SecurityKey training for everyone.

### Microsoft
Threat modeling training (S-SDL).

### Many startups
Annual + onboarding minimum.

## Mandatory + Voluntary

- Mandatory: baseline (compliance)
- Voluntary: deep dives (motivated)

## Best Practices

- Mandatory + ongoing
- Practical (hands-on)
- Champions program
- Just-in-time refreshers
- Measure
- Resources accessible

## Common Mistakes

- Click-through training
- One-time only
- No measurement
- Generic (not relevant)
- No follow-up

## Quick Refs

```
Topics: OWASP Top 10, secure coding, crypto, authN/Z
Formats: annual, workshop, CTF, JIT
Champions: per team
Measure: CVE rate, quiz scores
```

## Interview Prep

**Junior**: "Why train developers on security?" — Most vulnerabilities originate in code, so developers who recognize the common classes (injection, broken auth, secrets handling) prevent issues at the source rather than relying on downstream scanning.

**Mid**: "What makes security training actually stick?" — Make it relevant and hands-on — language/framework-specific examples, real findings from your own codebase, and just-in-time guidance at the moment of a risky change rather than an annual slide deck.

**Senior**: "How do you structure a developer security training program?" — Baseline onboarding plus role-specific deep dives, security champions embedded per team, and reinforcement through code review and paved-road defaults, measured by outcomes like vuln-introduction and recurrence rates.

**Staff**: "How do you build a security culture, not just run training?" — Tie security to engineering incentives, make the secure path the easy path via platform defaults, run blameless reviews of security incidents, and use champions to scale ownership so security is treated as a shared quality attribute rather than a gate someone else enforces.

## Next Topic

→ Move to [L20/C03 — Application Security Testing](../C03/README.md)
