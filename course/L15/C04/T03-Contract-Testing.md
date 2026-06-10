# L15/C04/T03 — Contract Testing (Pact)

## Learning Objectives

- Use contract testing
- Avoid integration test reliance

## Problem

Microservices:
- Service A calls Service B
- B changes API
- A breaks in prod

E2E tests catch but: slow, fragile, hard to maintain.

## Contract Testing

Consumer + provider agree on contract:
- Consumer: "I send this; expect this"
- Provider: "I accept this; return this"

Both tested independently against contract.

## Pact

Popular contract testing framework:
- Consumer-driven
- Pact files (JSON)
- Broker for sharing

## Consumer Test

```javascript
// In Service A (consumer)
const provider = new Pact({
  consumer: 'ServiceA',
  provider: 'ServiceB',
});

await provider.addInteraction({
  state: 'user exists',
  uponReceiving: 'a request for user',
  withRequest: {
    method: 'GET',
    path: '/users/123',
  },
  willRespondWith: {
    status: 200,
    body: { id: 123, name: 'Alice' },
  },
});

// Code that calls Service B
const user = await fetchUser(123);
expect(user.id).toBe(123);

await provider.verify();
```

Generates pact file.

## Pact File

```json
{
  "consumer": { "name": "ServiceA" },
  "provider": { "name": "ServiceB" },
  "interactions": [{
    "providerState": "user exists",
    "description": "a request for user",
    "request": { "method": "GET", "path": "/users/123" },
    "response": {
      "status": 200,
      "body": { "id": 123, "name": "Alice" }
    }
  }]
}
```

## Provider Verification

```javascript
// In Service B (provider)
const opts = {
  providerBaseUrl: 'http://localhost:8080',
  pactUrls: ['./pacts/serviceA-serviceB.json'],
  providerStatesSetupUrl: 'http://localhost:8080/provider-states',
};

new Verifier(opts).verifyProvider();
```

Runs B; sends each interaction; verifies.

## Provider State

For setup:
```javascript
// Service B handler
app.post('/provider-states', (req, res) => {
  if (req.body.state === 'user exists') {
    // Insert user 123 in test DB
  }
  res.send('OK');
});
```

For: pre-seed state.

## Pact Broker

Central server:
- Stores pact files
- Tracks versions
- Verification results
- Notifications

```bash
docker run -p 9292:9292 pactfoundation/pact-broker
```

## CI Integration

```yaml
# Consumer (Service A)
- run: npm test   # generates pact
- run: pact-broker publish ./pacts \
       --consumer-app-version=$VERSION \
       --broker-base-url=$BROKER_URL

# Provider (Service B)
- run: pact-provider-verifier \
       --provider-app-version=$VERSION \
       --pact-broker-base-url=$BROKER_URL
```

## CanIDeploy

Before deploying B:
```bash
pact-broker can-i-deploy \
  --pacticipant=ServiceB \
  --version=$VERSION \
  --to=production
```

Returns true if compatible with all production consumers.

For: safe deploys.

## Workflow

```
1. A test: define contract (consumer)
2. CI: publish pact
3. Broker: stores
4. B CI: verify against latest pact
5. B can-i-deploy: check
6. Both deploy independently
```

## Vs E2E

| | Contract | E2E |
|---|---|---|
| Speed | Fast (per service) | Slow |
| Reliability | High | Flaky |
| Maintenance | Low | High |
| Coverage | Boundaries | User journey |

For: contract beats E2E for service boundaries.

## When Contract Tests

- Microservices
- Multiple teams
- Independent deploys
- API contracts critical

## When Not

- Monolith (no service boundary)
- Tightly coupled team (less benefit)
- Few services (E2E simple enough)

## Limitations

- Doesn't catch business logic bugs
- Provider state setup tedious
- Schema only; not behavior

For: complement with other tests.

## Schema Contract

OpenAPI / gRPC:
- Define schema
- Generate client / server
- Validate at boundary

```yaml
openapi: 3.0.0
paths:
  /users/{id}:
    get:
      parameters: ...
      responses:
        '200':
          content:
            application/json:
              schema: ...
```

For: schema-based.

## Spring Cloud Contract

Java-specific:
```groovy
Contract.make {
  request {
    method 'GET'
    url '/users/123'
  }
  response {
    status 200
    body([id: 123, name: 'Alice'])
  }
}
```

## Provider-Driven (Anti-Pattern Sometimes)

OpenAPI spec → consumer adapts.

Risk: changes break consumers without warning.

For: provider-driven OK if change management strict.

## Consumer-Driven

Consumer says what it needs.

Provider verifies it can deliver.

For: aligned interests.

## Versioning

Contract versioning:
- Per consumer release
- Multiple versions live
- Provider verifies vs all active

## Webhooks

Pact Broker can notify on:
- New pact
- Verification result

For: pipeline integration.

## Real Examples

### REA Group
Early Pact adopter.

### IAG, Telstra
Australian shops.

### Many fintech / e-commerce
Avoid prod incidents.

## Best Practices

- Consumer-driven
- Per-API contract
- Broker centralized
- can-i-deploy gates
- Provider states minimal
- Avoid testing business logic in contracts

## Common Mistakes

- Test business logic via contracts (wrong tool)
- No can-i-deploy
- Broker not used (file-shared)
- Out-of-date contracts
- Tight coupling via overly specific matchers

## Matchers

```javascript
willRespondWith: {
  body: {
    id: Matchers.like(123),       // type match
    name: Matchers.string('Alice'), // any string
    email: Matchers.email(),
    created: Matchers.iso8601DateTime(),
  }
}
```

For: flexible matching.

## Alternative: GraphQL Contracts

Schema is contract. Type changes break.

For GraphQL: schema versioning + breaking change checks.

## gRPC Contracts

.proto file = contract.
Backward-compatible changes; tooling enforces.

For gRPC: schema-first.

## OpenAPI Diff

```bash
oasdiff compare old.yaml new.yaml --strict
```

Detect breaking changes.

For: REST API change management.

## Best Practices Recap

```
Contract tests:
- For service boundaries
- Consumer-driven
- Broker centralized
- can-i-deploy gates
- Pair with unit + small E2E
```

## Quick Refs

```bash
# Pact
npm install --save-dev @pact-foundation/pact

# Broker
docker run -p 9292:9292 pactfoundation/pact-broker

# Publish
pact-broker publish ./pacts --consumer-app-version=V --broker-base-url=URL

# Verify
pact-provider-verifier --pact-broker-base-url=URL --provider-app-version=V

# Can-I-deploy
pact-broker can-i-deploy --pacticipant=X --version=V --to=production
```

## Interview Prep

**Mid**: "What's contract testing."

**Senior**: "Pact workflow."

**Staff**: "Microservices testing strategy."

## Next Topic

→ [T04 — Performance, Load, Soak Tests](T04-Performance-Load-Soak.md)
