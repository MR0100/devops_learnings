# L15/C04/T01 — Test Pyramid Revisited

## Learning Objectives

- Apply test pyramid
- Avoid common anti-patterns

## Pyramid

```
       /\
      /E2\           Few; slow
     /----\
    /Integ.\         Some; medium
   /--------\
  /  Unit    \       Many; fast
 /------------\
```

Most unit; less integration; fewest E2E.

## Why Pyramid

- Unit: cheap, fast, isolated
- Integration: real components; slower
- E2E: slowest; most realistic

Cost (run time + maintenance) inverse to value (closer to user).

For: balance cost / fidelity.

## Mike Cohn (2009)

Original pyramid concept.

## Anti-Patterns

### Ice Cream Cone (Inverted)
Many E2E, few unit. Slow, flaky.

### Hour Glass
Many unit, many E2E, few integration. Misses interactions.

### All E2E
No unit. Untestable; rewrites for changes.

### All Unit
Misses integration bugs. Mock too much.

## Healthy Balance

For most:
- 70% unit
- 20% integration
- 10% E2E

Adjust by domain.

## Honeycomb (Microservices)

For microservices: integration matters more.

```
Contract: 50%
Integration: 30%
Unit: 20%
```

Each service simple unit; complexity at boundaries.

## Trophy (Frontend)

```
Static (TypeScript): big
Unit: lots
Integration: lots
E2E: few
```

Kent C. Dodds.

## Tests Per Layer

### Unit
Fastest. < 10 ms each.
Single function / class.
Mock dependencies.

### Integration
Real DB, real Redis (Testcontainers).
Many seconds each.

### E2E
Real browser, real services.
Minutes each.

## Why Unit Fast

- No network
- No filesystem (mostly)
- No external services
- In-memory

Run 1000 in seconds.

## Why E2E Slow

- Browser startup
- Service deps
- Real DB
- Sequential UI actions

Each: 30 sec - minutes.

## Cost Analysis

If you have:
- 1000 unit (50 sec total)
- 100 integration (500 sec)
- 10 E2E (300 sec)

Total: ~15 min. Manageable.

Vs:
- 100 unit (5 sec)
- 100 integration (500 sec)
- 1000 E2E (5 hr)

Total: 5 hr. Untenable.

## Pyramid Math

```
Cost = N × time-per-test
Fidelity = closeness-to-real-user

Aim: max(Fidelity / Cost)

Unit:  high fidelity per spent time
E2E:   low fidelity per spent time (despite high absolute)
```

## When to Push Up

### Critical Path
E2E for checkout flow. Worth the cost.

### Cross-Service
Integration tests for important contracts.

### Bug-Prone Areas
E2E to verify after fixes.

## When to Push Down

### Logic
Pure functions: unit.

### Validation
Data shape: unit.

### Algorithms
Algorithmic: unit.

## Test Smells

### Slow Test
> 100 ms unit test: probably not unit.

### Flaky
Network deps in "unit" test.

### Fragile
Breaks on refactor.

### Opaque
Doesn't tell you what failed.

## Refactor

- Pull integration logic to functions → unit
- Pull UI logic to view model → unit
- Test boundaries → integration
- Critical user journeys → E2E

For: shift left.

## Tools

### Unit
- Jest, Mocha (JS)
- pytest (Python)
- JUnit (Java)
- Go test (Go)
- testify (Go)

### Integration
- Testcontainers (real Docker)
- Karate
- Pact (contract)

### E2E
- Cypress
- Playwright
- Selenium (legacy)

### Performance
- k6
- JMeter
- Gatling

## In CI

```
PR:
  - Lint (10 s)
  - Unit (60 s)
  - Integration (5 min)
  - Build artifact
  - Deploy to ephemeral env
  - E2E smoke (5 min)
  - Total: < 15 min

Main:
  - Above + full E2E (30 min)
  - Performance smoke (10 min)

Nightly:
  - Full perf
  - Soak
  - Chaos
```

## Mocking

### Mock externals
HTTP calls, DB, etc.

### Don't mock yourself
If you wrote it, don't mock.

### Avoid over-mocking
Test mocks not code.

For: balance.

## Test Isolation

Each test:
- Independent
- Order doesn't matter
- Can run alone

For: parallel, debug.

## Test Doubles

- Dummy: passed but unused
- Stub: returns canned
- Mock: verifies interaction
- Spy: records calls
- Fake: working impl (in-memory DB)

For: right tool.

## Coverage

```bash
coverage run -m pytest
coverage report --fail-under=80
```

Targets:
- Critical: 90%+
- Important: 80%
- Total: 70-80%

Don't game it.

## Pyramid Per Layer

For libs: heavy unit.
For services: mixed.
For monolith: all layers.

## Best Practices

- Most unit
- Some integration
- Few E2E
- Critical path E2E
- Fast feedback (< 15 min PR)
- Parallel run
- Fail-fast for unit
- Continue for integration/E2E (see all)

## Common Mistakes

- Inverted pyramid
- All E2E
- Flaky tests ignored
- Slow unit tests
- No parallel
- Coverage as goal, not means

## Quick Refs

```
Unit:         many, fast (<10ms), isolated
Integration:  some, medium (seconds), real deps
E2E:          few, slow (minutes), full stack

Healthy: 70/20/10
```

## Interview Prep

**Junior**: "Test pyramid."

**Mid**: "Avoid anti-patterns."

**Senior**: "Per-domain pyramid."

**Staff**: "Testing strategy."

## Next Topic

→ [T02 — Unit, Integration, E2E](T02-Unit-Integration-E2E.md)
