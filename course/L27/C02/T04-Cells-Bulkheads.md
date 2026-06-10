# L27/C02/T04 — Cells & Bulkheads (Amazon's Approach)

## Learning Objectives

- Use cell architecture
- Isolate failures

## Cell

Independent slice:
- Own infra
- Own DB
- Own LB
- Serves subset of users

Failure: only that cell.

For: blast radius.

## Vs Microservices

Microservices: by function.
Cells: by users / tenants.

Each cell: all services.

## Examples

### Amazon Retail
Many cells; per-region per-tenant.

### Twitter (X)
Cell-based for users.

### Many SaaS
Per-customer cells.

## Benefits

- Limited blast (one cell affected)
- Independent deploy per cell
- Per-tenant isolation
- Easier scale

## Cost

- More infra (each cell)
- More ops

For: justifies for critical scale.

## Cell Sizing

- 1 per region (geo)
- 1 per customer (enterprise)
- N per region (10k users each)

For: trade-off.

## Routing

User → Cell:
- Hash(user_id) % N
- Or sticky assignment
- DB lookup

## Cell Failure

If cell fails:
- Affected users only
- Re-assign (gradual)
- Other cells unaffected

## Per-Cell Deploy

Canary at cell level:
- Deploy to one cell
- Verify
- Promote to next

For: gradual rollout.

## Bulkheads

(See L25/C05/T02.)

Similar concept smaller scale (within service).

Cells: macro.
Bulkheads: micro.

## Cell vs Region

Region: geographic.
Cell: logical (any region).

Cells can span regions.

## Real

### Stripe
Per-customer isolation (some).

### Salesforce
Per-customer "pods" (cells).

### Many enterprise SaaS
Cells.

## Best Practices

- Cell sizing planned
- Stateless routing
- Per-cell observability
- Failover tested
- Cell-aware deploys

## Common Mistakes

- One big cell (no isolation)
- Cells share state (defeats)
- No per-cell monitoring
- Cell-mass deploy at once

## Quick Refs

```
Cell = independent slice
Routing = user → cell
Failure = limited blast
Deploy = per-cell canary
```

## Interview Prep

**Senior**: "Cells."

**Staff**: "Cell architecture."

**Principal**: "Cellular for scale."

## Next Topic

→ Move to [L27/C03 — Data Replication](../C03/README.md)
