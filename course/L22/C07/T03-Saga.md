# L22/C07/T03 — Saga Pattern

## Learning Objectives

- Apply saga
- Handle distributed tx

## Problem

Cross-service transaction:
- Service A: write
- Service B: write
- Service C: write

If C fails: A, B need rollback.

Without distributed transaction (2PC), how?

## Saga

Sequence of local transactions:
- Each step has compensation
- Failure → compensate completed

For: eventual consistency.

## Orchestration

Central orchestrator:
```
Orchestrator → A.do() → B.do() → C.do()
```

If C fails:
```
Orchestrator → B.undo() → A.undo()
```

## Choreography

Each service emits event; others react:
```
Order created → Pay service charges → Inventory reserves → Ship service ships
```

If pay fails: emit OrderFailed; everyone cleans up.

## Compensation

Logical undo:
- Charge → Refund
- Reserve → Release
- Ship → Cancel

Not physical rollback.

## Example: Order

```
1. Create Order (status=PENDING)
2. Charge Card
3. Reserve Inventory
4. Ship
5. Mark Complete
```

If step 3 fails after 2:
- Refund (compensate 2)
- Cancel Order (compensate 1)

## Orchestrator

```python
class OrderSaga:
    def execute(self, order):
        try:
            self.charge(order)
            try:
                self.reserve(order)
                try:
                    self.ship(order)
                except:
                    self.release_reservation(order)
                    raise
            except:
                self.refund(order)
                raise
        except:
            self.cancel_order(order)
```

For: explicit flow.

## Choreography

Service A:
```python
def on_order_created(event):
    charge_card(...)
    emit(PaymentCharged(...))
```

Service B:
```python
def on_payment_charged(event):
    reserve_inventory(...)
    emit(InventoryReserved(...))
```

Service C:
```python
def on_payment_failed(event):
    cancel_order(...)
```

## Compared

| | Orchestration | Choreography |
|---|---|---|
| Logic | central | distributed |
| Visibility | clear | hard |
| Coupling | orchestrator central | event-based |
| Best for | complex | simple |

## Tools

- AWS Step Functions
- Temporal
- Camunda
- Apache Camel

For: orchestration without code.

## Temporal

Workflow engine:
```python
@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order):
        try:
            await workflow.execute_activity(charge, order)
            await workflow.execute_activity(reserve, order)
            await workflow.execute_activity(ship, order)
        except:
            await workflow.execute_activity(refund, order)
```

Reliable; durable; retries.

## Step Functions

JSON state machine:
```json
{
  "StartAt": "Charge",
  "States": {
    "Charge": {
      "Type": "Task",
      "Resource": "arn:...",
      "Next": "Reserve",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "CancelOrder"
      }]
    },
    ...
  }
}
```

## Eventual Consistency

Saga: not atomic.
- Mid-saga, system is inconsistent
- Eventually: consistent

For: tolerate this state.

## Idempotency

Each step idempotent:
- Re-run on failure
- No double-charge

## When Saga

- Microservices spanning
- Cannot use distributed tx
- OK with eventual

## When Not

- Single service (just use ACID)
- Strong consistency required

## Best Practices

- Idempotent steps
- Compensating actions
- Orchestrator or events
- Test failure paths
- Monitor saga state

## Common Mistakes

- Non-idempotent (double-charge)
- Skip compensation (data drift)
- Tight choreography coupling
- No timeout (stuck saga)

## Examples

### E-commerce
Order → Pay → Reserve → Ship

### Travel Booking
Reserve flight → Reserve hotel → Charge card

### Microservices
Across teams' services.

## Quick Refs

```
Saga: sequence of local tx
Compensation: undo on failure
Orchestration: central
Choreography: event-driven
Tools: Temporal, Step Functions, Camunda
```

## Interview Prep

**Mid**: "What's saga."

**Senior**: "Orchestration vs choreography."

**Staff**: "Distributed transactions."

## Next Topic

→ [T04 — Outbox Pattern](T04-Outbox.md)
