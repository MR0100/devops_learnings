# L15/C07 — Progressive Delivery

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Feature-Flags.md) | Feature Flags (LaunchDarkly, Unleash, OpenFeature) | 1 hr |
| [T02](T02-Flagger-Argo-Rollouts.md) | Flagger, Argo Rollouts | 1 hr |
| [T03](T03-Auto-Rollback.md) | Automated Rollback Triggers | 0.5 hr |

## Progressive Delivery

> The deployment, rollout, and traffic shifting of features in stages, gating each by automated analysis or business signals.

It includes:
- Canary deployments (gradual % rollout)
- Feature flags (per-user / per-cohort enablement)
- Automated rollback on bad signals
- Progressive cohorts (employees → beta users → 1% prod → 100%)

## Feature Flags

Decouple **release** (code deployed, dark) from **rollout** (feature enabled).

```javascript
if (await featureFlag.isEnabled('new-checkout', user)) {
  return newCheckoutFlow();
} else {
  return oldCheckoutFlow();
}
```

### Benefits
- Deploy any time (code is dark behind flag)
- Roll out incrementally (employees → beta → 1% → 100%)
- Kill switch (turn off broken feature instantly)
- A/B testing
- Per-tenant features

### Vendors
- **LaunchDarkly** — leader, enterprise
- **Split** — A/B-focused
- **Unleash** — OSS option (self-host)
- **ConfigCat** — simpler, cheaper
- **Optimizely** — experimentation platform
- **AWS AppConfig** — basic AWS-native
- **GrowthBook** — OSS, modern

### OpenFeature
CNCF standard for feature flag SDK. Provider-agnostic:
```javascript
import { OpenFeature } from '@openfeature/server-sdk';
OpenFeature.setProvider(new LaunchDarklyProvider({sdkKey: '...'}));
const client = OpenFeature.getClient();
const enabled = await client.getBooleanValue('new-checkout', false, ctx);
```

Swap providers without code change.

### Flag Lifecycle
1. Created (off everywhere)
2. Enabled for employees
3. Enabled for beta users
4. Rolled out 1% → 100%
5. **Removed from code** ← critical!

Stale flags accumulate. Set TTL; track via Slack reminder.

## Flagger

Operator on top of Istio/Linkerd/App Mesh that automates canary analysis.

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: my-app
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange: { min: 99 }
      interval: 1m
    - name: request-duration-p99
      thresholdRange: { max: 500 }
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.test/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://my-app/"
```

Flagger automatically:
1. Creates canary version
2. Routes 10% traffic
3. Checks metrics every 1 min
4. If passes 5 consecutive checks, increases by 10%
5. If failures, rolls back

## Argo Rollouts

Similar to Flagger but works without a mesh (uses any LB):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: { duration: 10m }
      - setWeight: 40
      - pause: {}                    # manual gate
      - setWeight: 60
      - pause: { duration: 10m }
      - setWeight: 80
      - pause: { duration: 10m }
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: my-app
```

Pairs with AnalysisTemplate referencing Prometheus / Datadog / etc.:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 5m
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prom:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}", status!~"5.."}[5m]))
          / sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

## Automated Rollback Triggers

What signals abort a canary?

### Health Metrics
- Error rate increased
- p95/p99 latency increased
- Throughput dropped
- CPU/Memory spiked

### Business Metrics
- Conversion rate dropped
- Revenue/min dropped
- Specific feature usage dropped

### External Signals
- Customer support tickets spike
- Slack alert from another team

### Implementing
- Flagger / Argo Rollouts handle technical metrics
- Business metrics: custom analysis template hitting your data warehouse
- Manual abort button always available

## Cohorts

Beyond `%`-based, smarter rollouts:
1. **Employees first** — internal dogfood
2. **Beta opt-in users** — willing canaries
3. **Low-impact countries** (e.g., starts in NZ before US)
4. **Free tier** before enterprise customers
5. **Geographic** rollout (region by region)

Feature flag platforms (LaunchDarkly et al.) handle this.

## Decoupling Release from Deploy

Key idea: **deploy** the code (rolling, blue/green) → all dark → **release** the feature (flag flip) → no infra change needed for rollback.

Production deploys then become routine; feature releases are the controlled events.

## Interview Themes

- "Progressive delivery — explain"
- "Walk me through canary with automated analysis"
- "Feature flags — what problems do they solve?"
- "Stale flags — how do you avoid?"
- "Decouple release from deploy"
