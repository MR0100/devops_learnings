# L28/C01/T01 — Functional vs Non-Functional Requirements

## Learning Objectives

- Identify requirements
- Drive system design

## Functional

What system does:
- "Users can upload images"
- "API returns user profile"
- "System generates reports"

## Non-Functional

How system performs:
- Latency
- Throughput
- Availability
- Scalability
- Security
- Cost

## In Interview

Start:
- Ask clarifying questions
- Establish both types
- Drive design

## Example: URL Shortener

### Functional
- Shorten URL
- Redirect to original
- Custom alias optional
- Analytics

### Non-Functional
- 100M URLs / day shortened
- 1B redirects / day
- p99 redirect < 100 ms
- 99.99% availability
- Cost-conscious

## Drive Decisions

Non-functional drives:
- Architecture
- Tech choice
- Trade-offs

For 1B redirects/day: ~12k/sec.

## SLO Implied

- 99.99%: 4 min/month down
- p99 100 ms: tight latency
- Cost: optimize hot path

## Capacity Math

(See T02.)

## Constraints

- Budget
- Team size
- Time
- Geographic

Affect design.

## Best Practices

- Ask before designing
- Confirm assumptions
- Document
- Revisit during design

## Common Mistakes

- Jump to design
- Ignore non-functional
- Over-engineer
- Miss obvious

## Quick Refs

```
Functional: features
Non-functional: quality

In interview:
- Ask
- Establish both
- Use to drive
```

## Interview Prep

**Junior**: "What's the difference between functional and non-functional requirements?" — Functional is *what* the system does (shorten a URL, return a profile); non-functional is *how well* it does it (latency, throughput, availability, cost). Functional gives you the feature list; non-functional gives you the architecture.

**Mid**: "Why bother with non-functional requirements up front?" — They drive every real decision — 1B redirects/day (~12k QPS) and p99 < 100 ms force a cache and a CDN, while 100/day wouldn't. Capturing them early stops you from designing the wrong system and having to redo it when scale numbers appear.

**Senior**: "How do non-functional requirements turn into trade-offs?" — Each one pushes the design: 99.99% availability implies multi-AZ/region and redundancy; strong consistency rules out async cross-region replication (CAP); aggressive cost targets push you to spot, tiered storage, and caching the hot path. The interview skill is naming the requirement, then committing to the architectural consequence and defending it.

**Staff**: "Walk me through how you'd run requirements-gathering for an ambiguous prompt." — Drive it: ask clarifying questions to pin functional scope, then quantify the non-functionals (DAU, read:write ratio, latency SLO, availability target, budget, compliance). Write them down as explicit assumptions so the interviewer can correct them, derive capacity from them (T02), and revisit them whenever a design choice forces a trade-off. The requirements become the rubric I grade my own design against.

## Next Topic

→ [T02 — Capacity Estimation Math](T02-Capacity-Math.md)
