# L15/C07/T01 — Feature Flags

## Learning Objectives

- Use feature flags
- Manage flag debt

## Feature Flag

Conditional code path; toggle without deploy:
```javascript
if (flags.isEnabled('new-checkout', user)) {
  return newCheckout();
}
return oldCheckout();
```

## Why

- Deploy ≠ release (deploy disabled; toggle later)
- Per-user / per-cohort enablement
- Kill switch (instant disable)
- A/B testing
- Gradual rollout
- Canary
- Operational toggles

## Types

### Release Flags
Short-lived; deploy off; toggle on per cohort.

### Experiment Flags
A/B test.

### Ops Flags
Long-lived; circuit breakers, kill switches.

### Permission Flags
Per-tenant.

## Tools

### LaunchDarkly
Industry leader. Paid; rich.

### Split.io
Similar; analytics integrated.

### Optimizely
Strong A/B focus.

### Statsig
Modern; A/B + experimentation.

### Unleash
OSS option.

### OpenFeature
Standard SDK; provider-agnostic.

### Built-In
ConfigMap, env vars, DB lookup.

## OpenFeature

Standard API; provider-swappable:
```javascript
import { OpenFeature } from '@openfeature/web-sdk';

OpenFeature.setProvider(new LaunchDarklyProvider({...}));

const client = OpenFeature.getClient();
const enabled = await client.getBooleanValue('feature', false);
```

Switch providers without code change.

## Per-User Evaluation

```javascript
const context = {
  userId: user.id,
  email: user.email,
  country: user.country,
  plan: user.plan,
};

const enabled = await client.getBooleanValue('feature', false, context);
```

Rules:
```
Plan == "premium" AND country == "US" → true
Else: false
```

## Targeting

```yaml
rules:
- if: plan == 'premium'
  serve: true
- if: userId IN ['alice@', 'bob@']
  serve: true
- default: false
```

For: gradual rollout.

## Percentage Rollout

```yaml
default: 5%
# 5% of users get true; sticky
```

Hash userId; consistent.

## Flag Hierarchy

```
Targeting rules first
Percentage second
Default fallback
```

## Server vs Client

### Server SDK
- Stateful; evaluates per-user
- Updates near real-time (stream)

### Client SDK
- Initial bootstrap from server
- Cached
- Less secure (visible)

For: server-side rules, client UI.

## Performance

```javascript
// Eager evaluation; cache
const flags = await client.allFlags(context);

// Use without round-trip
if (flags['feature']) ...
```

For: avoid per-call eval.

## Audit

LaunchDarkly etc. log:
- Who toggled
- When
- Per-flag history

For: compliance.

## Flag Lifecycle

```
1. Create
2. Deploy code (off)
3. Test in dev (toggle on)
4. Stage rollout (cohorts)
5. 100%
6. Code becomes default
7. Remove flag + branch
```

For: clean code.

## Flag Debt

Old flags accumulate. Tech debt.

Mitigations:
- Flag expiry dates
- Quarterly cleanup
- Automated reports
- Don't add without removal plan

## Code Patterns

### Strategy
```javascript
function getCheckoutStrategy(user) {
  if (flags.isEnabled('new-checkout', user)) {
    return new NewCheckout();
  }
  return new OldCheckout();
}
```

### Decorator
```javascript
function withFlag(name, oldFn, newFn) {
  return (ctx) => flags.isEnabled(name, ctx) ? newFn(ctx) : oldFn(ctx);
}
```

### Branch
```javascript
if (flags.isEnabled('feature', user)) {
  // New
} else {
  // Old
}
```

## Anti-Patterns

### Nested Flags
```javascript
if (flagA) {
  if (flagB) {
    if (flagC) {  // Combinatorial nightmare
    }
  }
}
```

### Flag Forever
"Just in case" flag stays 5 years.

### Flag for Bug Workaround
Hide bug behind flag; never fix.

### Flag Logic in Business Code
Coupled; hard to test.

## Testing with Flags

```javascript
// Per-test flag state
beforeEach(() => {
  flags.setForTesting('feature', true);
});

afterEach(() => {
  flags.reset();
});
```

For: test both branches.

## Kill Switch

```javascript
if (!flags.isEnabled('payments-service', user)) {
  return showMaintenancePage();
}
```

For: instantly disable.

## Operational vs Release

```
Release flag:    deploy with off; ramp on; delete
Ops flag:        permanent; kill switch
```

Distinguish in flag platform.

## Cost

LaunchDarkly: ~$8-12/user/mo.
Split.io: similar.
Unleash OSS: free, host yourself.

For startups: OSS.
For prod: paid tools save engineer time.

## Flag SDK Best Practices

- Bootstrap on app start
- Stream updates (no polling)
- Cache evaluations
- Fallback to default if SDK fails
- Don't block UI on flag eval

## Privacy

User attributes sent to flag service:
- PII?
- GDPR?

Configure: only send hashed IDs if needed.

## Real Examples

### LinkedIn
LiX system; massive scale.

### Meta
GateKeeper; everything behind flag.

### Etsy
Pioneered flags for deploys.

## Best Practices

- Use flags for risk
- Distinguish release / ops / experiment
- Document each flag
- Expiration dates
- Quarterly cleanup
- Hierarchical fallbacks
- Test both branches

## Common Mistakes

- Flag forever
- No documentation
- Logic in business code
- Nested flags
- No test of both branches
- Forget cleanup

## Quick Refs

```javascript
// OpenFeature
const client = OpenFeature.getClient();
const enabled = await client.getBooleanValue('flag', false, context);

// Targeting
{
  userId: 'alice',
  country: 'US'
}

// Cleanup
- Remove `if (flags...)` and old branch
- Remove flag from platform
- Audit per quarter
```

## Interview Prep

**Mid**: "What's a feature flag."

**Senior**: "Flag lifecycle."

**Staff**: "Flag platform at scale."

## Next Topic

→ [T02 — Flagger, Argo Rollouts](T02-Flagger-Argo-Rollouts.md)
