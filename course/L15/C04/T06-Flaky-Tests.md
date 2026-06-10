# L15/C04/T06 — Flaky Test Management

## Learning Objectives

- Detect flakes
- Fix or quarantine

## Flaky Test

Sometimes passes, sometimes fails on identical code.

Causes:
- Timing / race conditions
- External deps (network, time)
- Test order dependencies
- Resource leaks
- Non-deterministic data

## Why Bad

- Eroded trust ("just rerun")
- Real failures missed
- Wasted time investigating
- Slows pipeline

## Detection

### Retry Patterns
```yaml
- run: pytest --reruns 3
```

If test passes on retry: flaky.

Track:
- Test name
- Times re-run
- Pass-on-retry rate

## Quarantine

Move flaky to separate suite:
```python
@pytest.mark.flaky
def test_something():
    ...
```

```bash
pytest -m "not flaky"   # PR / merge gate
pytest -m flaky          # nightly investigation
```

For: unblock pipeline; track separately.

## Fix Vs Quarantine

### Fix Always Preferred
Real cause; gone forever.

### Quarantine
Temporary; track. Pay debt down.

For: don't accumulate quarantined indefinitely.

## Root Causes

### Time
```python
# Bad
assert is_today(time_field) == True

# Good
assert is_today(time_field, now=fixed_time)
```

### Random
```python
# Bad
random.choice([1, 2, 3])

# Good
random.seed(42)
random.choice([1, 2, 3])
```

### Async
```python
# Bad
await send_email(user)
assert email_received_by(user)   # may not have arrived

# Good
await send_email(user)
wait_for(lambda: email_received_by(user), timeout=5)
```

### Order
```python
# Bad: test A leaves DB state; test B fails
# Good: each test cleans up

@pytest.fixture(autouse=True)
def reset_db():
    db.clean()
    yield
    db.clean()
```

### Network
```python
# Bad
response = requests.get(EXTERNAL_API)

# Good (mock or use VCR)
@vcr.use_cassette('test_external.yaml')
def test():
    response = requests.get(EXTERNAL_API)
```

### Resource
```python
# Bad: resource leak across tests
file_handle = open('/tmp/cache')

# Good: cleanup
@pytest.fixture
def file_handle():
    f = open('/tmp/cache')
    yield f
    f.close()
```

## CI Detection

```yaml
- name: Run tests with retries
  run: pytest --reruns 3 --json-report --json-report-file=results.json

- name: Track flakes
  run: |
    jq '.tests[] | select(.outcome == "passed" and .rerun > 0)' results.json
```

## Dashboard

Track per-test:
- Pass rate
- Pass-on-retry rate
- Time-to-pass distribution

Tools:
- Buildkite Test Analytics
- CircleCI Insights
- Custom (Grafana)

For: prioritize flake fixes.

## Quarantine Workflow

1. Test fails intermittently
2. Add `@pytest.mark.flaky` annotation
3. File ticket
4. Owner investigates
5. Fix
6. Remove quarantine marker

Track ticket age.

## Ban Flaky Imports

```python
# Don't import from real network in tests
import socket
socket.gethostbyname = lambda *a: '1.2.3.4'   # mock
```

For: enforce isolation.

## Test Containers Snapshots

Same start state every time:
```python
@pytest.fixture
def db():
    container = PostgresContainer("postgres:15")
    container.start()
    # Load snapshot
    yield container
    container.stop()
```

For: reproducibility.

## Flaky Test Anti-Patterns

### Auto-Retry Without Tracking
```bash
pytest --reruns 100   # always passes eventually
```

Hides bugs.

### Ignore
Comment out without fixing.

### Skip on CI Only
```python
@pytest.mark.skipif(os.environ.get("CI"), reason="flaky")
```

Tests pass locally; fail in prod.

### Per-Test Sleeps
```python
time.sleep(5)   # "hope it's done"
```

Slow + still flaky.

## Best Practices

- Track flake rate
- Auto-quarantine on threshold
- Owner per test
- Quarantine debt budget
- Fix > quarantine
- Mocks for externals
- Fixed time, fixed random in tests
- Order-independent

## Common Mistakes

- Retry indefinitely (hide)
- No tracking (silent decay)
- Quarantine forever (debt)
- Sleeps everywhere (slow)
- Tests depend on each other

## Bisecting Flakiness

```bash
# Run test many times to confirm flake
for i in {1..50}; do pytest tests/test_X.py::test_Y; done
```

If varies: flaky.

For: confirm.

## Detection at Merge

```yaml
- name: Check flake
  run: |
    pytest --reruns 3 -p no:cacheprovider 2>&1 | tee out.txt
    if grep -q "RERUN" out.txt; then
      echo "Flaky test detected"
      exit 1   # block merge
    fi
```

Strict: don't merge with re-runs.

## False Positive

Real failure misdiagnosed as flake. Investigate before quarantine.

## Tools

### pytest-rerunfailures
```bash
pip install pytest-rerunfailures
pytest --reruns 3 --reruns-delay 1
```

### Jest retry
```javascript
jest.retryTimes(3);
```

### Mocha retries
```javascript
this.retries(3);
```

## Real Examples

### Google
~10% of test runs include flakes. Big investment in mitigation.

### FB
Test Insights; quarantine flow.

### Most companies
Suffer; under-invest in fix.

## Cultural

Treat flakes as P1 bugs:
- Track
- Assign
- Fix or quarantine
- Don't ignore

For: trust restored.

## Quick Refs

```bash
# Detect
pytest --reruns 3
jest --testFailureExitCode 1

# Mark
@pytest.mark.flaky
jest.retryTimes(3)

# Run quarantined
pytest -m flaky

# Skip quarantined
pytest -m "not flaky"
```

## Interview Prep

**Mid**: "What's a flaky test."

**Senior**: "Manage flakes at scale."

**Staff**: "Test reliability strategy."

## Next Topic

→ Move to [L15/C05 — Artifact Management](../C05/README.md)
