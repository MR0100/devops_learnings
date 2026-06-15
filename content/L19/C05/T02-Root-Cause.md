# L19/C05/T02 — Root Cause vs Contributing Factors

## Learning Objectives

- Distinguish root vs contributing
- Avoid simplistic analysis

## Root Cause

The fundamental issue. The reason.

## Contributing Factor

Conditions that worsened/enabled.

## Example

Incident: payment service down.

Root: bad deploy.

Contributing:
- Canary skipped (deadline)
- Monitor lag (3 min)
- Runbook outdated
- DB connection pool small

For: many factors.

## The Five Whys

Iterate:
1. Service down. Why?
2. Bad deploy. Why?
3. Code bug. Why?
4. Insufficient testing. Why?
5. No integration test for that path. Why?
6. Test infrastructure flaky.

Real root: test infra.

But: often more nuanced.

## Limits of Five Whys

- Single thread (real failures have many)
- Stops too soon
- "Why" can be too generic
- Hindsight bias

For: useful but not gospel.

## Complex Systems

Modern systems:
- Multiple causes
- Cascading failures
- Latent conditions

Single "root cause" misleading.

## Causal Factors (Better)

List:
- Necessary conditions
- Sufficient conditions
- Each examined

For: complete picture.

## Latent Conditions

Lurking issues:
- Bad design
- Tech debt
- Process gap

Surfaced by trigger.

For: address latent.

## Trigger vs Cause

Trigger: immediate (the deploy).
Cause: deeper (no validation).

Both matter; different fixes.

## Example: Cloudflare BGP

```
Trigger: Bad BGP regex
Root cause: Regex backtracking
Contributing:
- No staged rollout
- Insufficient testing
- Documentation incomplete
```

Multiple action items per factor.

## Avoid Simplistic

"Alice deployed without checking" — bad analysis.

Better:
- Why didn't process catch?
- Why did Alice deploy that way?
- What signals were missed?

For: improve system.

## Bayesian Thinking

Multiple potential causes:
- Probability each
- Evidence for each
- Most likely (but uncertain)

For: epistemic humility.

## Reality

Often: combination.
- Bug
- Process gap
- Monitor lag
- Human factor
- Architecture limit

All contributed.

## Action Items per Factor

Don't fix only one.

For: comprehensive.

## Just Culture

Acknowledge:
- Humans err
- Systems shape behavior
- Fix systems > blame humans

For: improve.

## Examples

### Software Bug
- Bug in code: root
- No test: contributing
- Deploy without canary: contributing

Three fixes:
- Fix bug
- Add test
- Add canary

### Network
- BGP misconfig: root
- No validation: contributing
- Cross-region propagation: contributing

### Hardware
- Disk failed: root
- No spare: contributing
- Backup not tested: contributing

## Hindsight Bias

After incident:
- Easy to say "should have known"
- Real-time: not obvious

For: don't fault for normal limitations.

## Skill at Time

Engineer didn't know X (hadn't been trained):
- Training gap (contributing)
- Onboarding gap

For: address gaps.

## Knowledge Gaps

Sometimes:
- Documentation missing
- Tribal knowledge

Surfacing these: valuable outcome.

## Postmortem Section

```markdown
## Root Cause Analysis

Multiple factors contributed:

1. **Code bug**: regex backtracking in BGP parser
   - Action: fix regex (P0)
   - Action: add backtracking detection in CI

2. **Deploy process**: no staged rollout for network config
   - Action: add canary deploy for network configs

3. **Monitoring lag**: 3 min between event and alert
   - Action: faster metric scraping

4. **Documentation**: outdated runbook
   - Action: update runbook + automated freshness check
```

## Cynefin

Domain-aware:
- Simple: clear cause
- Complicated: experts can find
- Complex: emergent
- Chaotic: random

For: incident type informs analysis.

## Best Practices

- Multiple contributing factors
- Each actionable
- Avoid sole "root cause"
- Just culture
- Address latent

## Common Mistakes

- One root cause only
- Stop at "human error"
- Blame trigger, not cause
- Hindsight bias
- No follow-through

## Quick Refs

```
Root cause:    fundamental why
Contributing:  conditions worsening
Trigger:       immediate
Latent:        lurking
Multiple:      typical
Action per:    factor
```

## Interview Prep

**Junior**: "What's the difference between a root cause and a contributing factor?" — The root cause is the fundamental reason the incident happened, while contributing factors are the conditions that enabled or worsened it — like a skipped canary, monitoring lag, or an outdated runbook.

**Mid**: "What are the limits of the Five Whys?" — It follows a single causal thread and can stop too soon or land on "human error," but real incidents have many interacting causes, so it's a useful starting tool rather than gospel; you also separate the trigger (the deploy) from the deeper cause (no validation) because they need different fixes.

**Senior**: "Why is a single 'root cause' often the wrong framing?" — Modern distributed systems fail through multiple causes, cascading failures, and latent conditions surfaced by a trigger, so you should enumerate causal factors — each with its own action item — rather than fixing only one and declaring victory.

**Staff**: "How do you analyze failures in complex systems?" — Apply just-culture and Bayesian thinking with epistemic humility (weigh multiple candidate causes by evidence), guard against hindsight bias by judging decisions on what was known at the time, surface latent conditions and knowledge gaps as first-class findings, and use a frame like Cynefin to match the depth of analysis to whether the domain is complicated, complex, or chaotic.

## Next Topic

→ [T03 — Action Items That Stick](T03-Action-Items.md)
