# L15/C04 — Testing in Pipelines

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Test-Pyramid.md) | Test Pyramid Revisited | 0.5 hr |
| [T02](T02-Unit-Integration-E2E.md) | Unit, Integration, E2E | 1 hr |
| [T03](T03-Contract-Testing.md) | Contract Testing (Pact) | 1 hr |
| [T04](T04-Perf-Load-Soak.md) | Performance, Load, Soak Tests | 1 hr |
| [T05](T05-Security-Tests.md) | Security Tests in CI | 1 hr |
| [T06](T06-Flaky-Tests.md) | Flaky Test Management | 0.5 hr |

## The Test Pyramid

```
              ╱╲
             ╱E╲          E2E (few — slow, expensive)
             ╱2E╲
            ╱────╲
           ╱ Integ╲       Integration (some — focused)
          ╱────────╲
         ╱   Unit   ╲     Unit (many — fast, cheap)
        ╱────────────╲
```

Modern adjustment: add **contract tests** between unit and integration.

### Bad Shapes

- **Inverted (Ice Cream Cone)**: lots of E2E, few unit. Slow CI, brittle.
- **Hourglass**: many unit and E2E, few integration. Misses integration bugs.
- **Cupcake**: only E2E. Worst.

## Unit Tests

- Fast (< 1s each)
- No I/O (mocks)
- One thing at a time
- Many of them

Tools: Go test, pytest, Jest, JUnit, etc.

```go
func TestAdd(t *testing.T) {
    cases := []struct{ a, b, want int }{
        {1, 2, 3}, {-1, 1, 0}, {0, 0, 0},
    }
    for _, c := range cases {
        if got := Add(c.a, c.b); got != c.want {
            t.Errorf("Add(%d,%d) = %d, want %d", c.a, c.b, got, c.want)
        }
    }
}
```

## Integration Tests

- Real dependencies (DB, queue, file system)
- Focus on integration points
- Slower (seconds each)
- Some

### Containers in Tests (Testcontainers)
```python
from testcontainers.postgres import PostgresContainer

def test_db():
    with PostgresContainer("postgres:16") as pg:
        # Use real Postgres
        url = pg.get_connection_url()
        run_migrations(url)
        assert_data(url)
```

Real Postgres in CI, no mocking, isolated.

## End-to-End (E2E)

- Whole system from user's perspective
- Slow, expensive
- Few critical paths only

Tools: Cypress, Playwright, Selenium, k6 (HTTP), Postman/Newman.

### Where Run
- After deploy to staging
- Not in PR-blocking (too slow)
- Nightly broader runs

## Contract Tests

Between consumer and producer of an API:
- Consumer declares what it expects (Pact file)
- Producer verifies its API matches the expectation

```javascript
// Consumer test (uses Pact mock)
provider.addInteraction({
    state: 'a user exists',
    uponReceiving: 'get user',
    withRequest: { method: 'GET', path: '/users/42' },
    willRespondWith: { status: 200, body: { id: 42, name: 'Alice' } }
});
```

```bash
# Producer side replays the contract against real service
pact-verify --provider=user-service --pact-broker=https://...
```

### Why
- Independent deploys safe (won't break consumers)
- Catch contract drift early
- No fragile E2E across services

## Performance Tests

### Load Test
Sustained traffic at expected peak.
- Look for: throughput, latency p50/p95/p99
- Tools: k6, Locust, Gatling, JMeter

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,        // virtual users
  duration: '5m',
};

export default function () {
  const r = http.get('https://api.example.com/users');
  check(r, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Stress Test
Beyond expected — find the breaking point.

### Soak Test
Long duration (hours-days) at moderate load. Find memory leaks, slow degradation.

### Spike Test
Sudden burst from low → high.

## Security Tests

### SAST (Static)
- Semgrep, SonarQube, CodeQL
- Scan source for known vuln patterns
- Run on every PR

### DAST (Dynamic)
- OWASP ZAP, Burp Suite
- Scan a running app
- Run nightly or pre-prod

### SCA (Software Composition Analysis)
- Snyk, Trivy, OSV-Scanner
- Scan dependencies for CVEs
- Run on every PR

### Secret Scanning
- Gitleaks, trufflehog
- Scan for leaked keys
- Run on every PR + repo history

### IaC Scanning
- Checkov, tfsec, kics
- Scan Terraform/CloudFormation/K8s manifests
- Run on every PR

## Flaky Tests

A test that sometimes passes, sometimes fails.

### Causes
- Timing dependencies (sleep instead of wait_for)
- Order dependencies (test pollution)
- Network (external services)
- Random ordering
- Resource exhaustion (CI runner under load)
- Concurrency (race conditions)

### Detection
- CI re-run features (GitHub Actions, etc.)
- Flake detection tools (Buildkite test analytics)
- Track per-test flake rate

### Quarantine
Move flaky test out of blocking CI; assign owner to fix; remove from quarantine when stable.

### Why Tolerate Them
- They erode trust in CI
- Engineers retry without fixing
- Real failures get ignored as "probably flaky"

**Rule**: zero-tolerance for flaky tests once detected; quarantine fast, fix fast.

## Test Coverage

- Coverage % isn't a goal in itself
- 100% coverage = 100% of code touched, not 100% of bugs caught
- Focus on critical paths
- Mutation testing for "did the test actually verify?"

## CI Best Practices

- Fast tests first (fail fast)
- Skip slow tests on draft PRs
- Cache test deps (Docker images, packages)
- Parallelize (sharding, matrix)
- Required checks before merge
- Auto-merge bot for green PRs

## Interview Themes

- "Test pyramid — and the alternatives"
- "Why contract tests over E2E across services?"
- "Flaky tests — how to handle?"
- "Performance testing — what types?"
- "Security in CI — what stages?"
