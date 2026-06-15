# L15/C06/T06 — A/B Testing

## Learning Objectives

- Run A/B experiments
- Distinguish from canary

## A/B Testing

Two variants to different users:
- Variant A: control
- Variant B: experiment

Measure: business metric.

For: hypothesis-driven product changes.

## Vs Canary

| | Canary | A/B |
|---|---|---|
| Purpose | Safe rollout | Feature comparison |
| Duration | Hours | Days-weeks |
| Audience | Random % | Targeted (cohort) |
| Metric | Errors, latency | Business (conversion, retention) |
| Outcome | Promote | Keep winner |

## Tools

### Feature Flags
- LaunchDarkly
- Split.io
- Optimizely
- Statsig
- Unleash (OSS)

### A/B Platforms
- Optimizely
- Google Optimize (discontinued; alts)
- Statsig (analytics + flags)
- Mixpanel + flags

## Setup

```javascript
// In code
const variant = featureFlags.getVariant('checkout-redesign', user.id);
if (variant === 'A') {
  // Old checkout
} else if (variant === 'B') {
  // New checkout
}
```

User assigned via:
- Hash user ID
- Random
- Cohort

## Sticky Assignment

User always gets same variant:
- Hash(userId + experiment) mod 100
- < threshold: A; else B

For: consistent experience.

## Allocation

```yaml
checkout-redesign:
  variants:
    A: 50
    B: 50
```

Or:
```yaml
  A: 95
  B: 5    # gradual
```

Ramp up B as data accumulates.

## Metrics

### Primary
What you optimize: conversion rate, revenue per visitor.

### Secondary
Side effects: bounce, session length.

### Guardrails
Don't break: error rate, latency.

## Sample Size

Statistical significance:
- Effect size (small change = large sample)
- Power (typically 80%)
- p-value (often 0.05)

Tools:
- Optimizely calculator
- Custom (statsmodels)

For: avoid premature decisions.

## Duration

Run until significance OR fixed period (e.g. 2 weeks for week-cycle effects).

Stop early: invalid (peeking).

For: pre-register duration.

## Hypothesis

Before experiment:
```
"Changing checkout button color to green will increase conversion by 5%."
```

Post-experiment: accept / reject.

## Analysis

```python
from scipy import stats
import numpy as np

# A group: 1000 users; 50 conversions
# B group: 1000 users; 65 conversions
chi2, p, dof, expected = stats.chi2_contingency([[50, 950], [65, 935]])
print(p)   # < 0.05 = significant
```

Or use platform analytics.

## Pitfalls

### Peeking
Stop early when see positive. Invalid.

### Multiple Tests
Run 20 experiments; 1 hits p < 0.05 by chance. Bonferroni correct.

### Wrong Metric
Optimize sign-up; lose paying users.

### Selection Bias
A: weekday users; B: weekend. Confound.

### Network Effects
Users in same group affect each other.

## Server vs Client

### Server-Side
Backend evaluates flag.
Pros: secret experiments, consistent.
Cons: server round-trip.

### Client-Side
JS evaluates.
Pros: instant.
Cons: visible to user, race conditions.

Choose by need.

## Bucketing

```javascript
function getBucket(userId, experimentId) {
  return hash(userId + experimentId) % 100;
}

if (getBucket(user.id, 'redesign') < 50) {
  variant = 'A';
} else {
  variant = 'B';
}
```

Consistent.

## Long-Term

Flag may stay forever:
- Permanent feature toggle
- Per-tenant config
- Kill switch

Distinguish: experiment vs ops flag.

## Cleanup

```
Experiment ends:
  - Pick winner
  - Set 100% to winner
  - Remove old code
  - Remove flag
```

For: code clean.

## CI/CD Integration

```javascript
const feature = await flags.getValue('new-feature', user);
if (feature) {
  // Code
}
```

Deploy code; toggle flag separately.

For: deploy ≠ release.

## Kill Switch

Toggle off bad feature instantly:
```javascript
const enabled = await flags.getValue('new-feature', user);
if (!enabled) {
  return oldCode();
}
```

For: rollback without redeploy.

## Risk-Based Rollout

```
Week 1: 1% users
Week 2: 5%
Week 3: 25%
Week 4: 100%
```

For: gradual confidence.

## Personalization

```
Variant by user segment:
- New users: variant A
- Returning: variant B
```

For: per-cohort tests.

## Multi-Variate

A/B/C/D/E:
```yaml
variants: { A: 20, B: 20, C: 20, D: 20, E: 20 }
```

More variants = need larger sample.

## Statistical Tools

- t-test (continuous metrics)
- chi-square (categorical)
- bootstrapping (any metric)
- Bayesian (no fixed sample size)

## Bayesian A/B

```
Posterior probability that B > A:
- Update with each data point
- Stop when confident
```

No peeking issue.

Tools: BayesAB.

## Real Examples

### Google
A/B everything. Search, ads, UI.

### Microsoft
Bing experiments; massive scale.

### Netflix
Thumbnails, recommendations.

### Meta
Constant experiments.

## Org Patterns

### Dedicated Experimentation Team
Platform + analysis.

### Per-Team Tools
LaunchDarkly / Statsig self-service.

For FAANGM: dedicated.

## Best Practices

- Hypothesis first
- Pre-register duration
- Bonferroni for multi-test
- Sticky assignment
- Guardrail metrics
- Clean up after
- Document learnings

## Common Mistakes

- Peek + stop early
- Multiple unadjusted tests
- Wrong primary metric
- Forget cleanup
- Network effects ignored
- Selection bias

## Quick Refs

```javascript
// Feature flag
const variant = flags.get('experiment', user.id);

// Track
analytics.track('experiment_exposed', { variant, user_id });

// Conversion
analytics.track('conversion', { variant, value });
```

## Interview Prep

**Mid**: "A/B vs canary."

**Senior**: "Experiment design."

**Staff**: "Experimentation platform."

## Next Topic

→ Move to [L15/C07 — Progressive Delivery](../C07/README.md)
