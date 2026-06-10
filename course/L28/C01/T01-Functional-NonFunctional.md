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

**Junior**: "What's NFR."

**Mid**: "Capture in design."

**Senior**: "Drive trade-offs."

**Staff**: "NFR strategy."

## Next Topic

→ [T02 — Capacity Estimation Math](T02-Capacity-Math.md)
