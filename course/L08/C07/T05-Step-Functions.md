# L08/C07/T05 — Step Functions (Standard vs Express)

## Learning Objectives

- Orchestrate workflows
- Pick Standard vs Express

## Step Functions

State machine service. Coordinate multi-step workflows:
- Lambda → Lambda → Lambda
- With branching, retries, error handling, parallel
- Visualizable; audit trail

## State Machine

JSON definition (Amazon States Language, ASL):
```json
{
  "Comment": "Order processing",
  "StartAt": "Validate",
  "States": {
    "Validate": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:Validate",
      "Next": "Charge",
      "Catch": [{"ErrorEquals": ["ValidationError"], "Next": "Reject"}]
    },
    "Charge": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:Charge",
      "Retry": [{"ErrorEquals": ["TransientError"], "MaxAttempts": 3}],
      "Next": "Ship"
    },
    "Ship": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:Ship",
      "End": true
    },
    "Reject": {
      "Type": "Fail",
      "Error": "ValidationFailed"
    }
  }
}
```

## State Types

- **Task**: invoke service (Lambda, ECS, SQS, etc.)
- **Choice**: branch on input
- **Wait**: pause N seconds or until time
- **Parallel**: run branches concurrently
- **Map**: iterate over items
- **Pass**: transform input → output
- **Fail / Succeed**: terminal

## Service Integrations

Direct AWS service integration (no Lambda needed):
- DynamoDB (PutItem, GetItem)
- SQS (SendMessage)
- SNS (Publish)
- S3 (object ops)
- EventBridge
- ECS / Fargate (RunTask)
- EMR (Add steps)
- Batch
- Glue
- And many more

Saves Lambda cost; simpler.

## Standard vs Express

| | Standard | Express |
|---|---|---|
| Use | Long-running | High-throughput |
| Max duration | 1 year | 5 minutes |
| Pricing | Per state transition | Per execution + duration |
| Execution model | Exactly-once | At-least-once (async) or sync |
| Visibility | History viewable | Logs only |

## Standard

Pricing: $25/M state transitions.

For: long workflows; human-in-the-loop; complex orchestration.

Example: order pipeline (validate → charge → ship → email; can take hours).

## Express

Two variants:
- Asynchronous (fire-and-forget)
- Synchronous (request-response)

Pricing: $1/M executions + ~$0.000044 per GB-second.

For: short-duration, high-volume (10k/sec OK).

Example: IoT event processing.

Cheaper than Standard for short workflows at scale.

## Async Express

Like Lambda async event → process → done. No tracking back.

```bash
aws stepfunctions start-execution --state-machine-arn ... --input '...'
```

## Sync Express

Call; wait for completion; get result. <5 min.

```bash
aws stepfunctions start-sync-execution --state-machine-arn ... --input '...'
```

Replaces Lambda chains.

## Choice State

```json
"CheckType": {
  "Type": "Choice",
  "Choices": [
    {"Variable": "$.type", "StringEquals": "express", "Next": "Fast"},
    {"Variable": "$.amount", "NumericGreaterThan": 1000, "Next": "Review"}
  ],
  "Default": "Standard"
}
```

## Parallel

```json
"FanOut": {
  "Type": "Parallel",
  "Branches": [
    {"StartAt": "ProcessA", "States": {...}},
    {"StartAt": "ProcessB", "States": {...}}
  ],
  "Next": "Combine"
}
```

Branches run concurrently; wait for all; output is array.

## Map (Iterate)

```json
"ProcessOrders": {
  "Type": "Map",
  "ItemsPath": "$.orders",
  "MaxConcurrency": 10,
  "Iterator": {
    "StartAt": "ProcessOne",
    "States": {...}
  },
  "Next": "Done"
}
```

For each item: run sub-state-machine. Up to 10 concurrent.

For huge: Distributed Map (40+ concurrent; reads from S3).

## Retries

Per state:
```json
"Retry": [{
  "ErrorEquals": ["States.TaskFailed"],
  "MaxAttempts": 3,
  "IntervalSeconds": 2,
  "BackoffRate": 2
}]
```

Exponential backoff built-in.

## Error Handling

```json
"Catch": [{
  "ErrorEquals": ["CustomError"],
  "Next": "HandleError",
  "ResultPath": "$.error"
}]
```

Catch routes to fallback state.

## Wait

```json
"WaitForApproval": {
  "Type": "Wait",
  "Seconds": 3600,
  "Next": "CheckStatus"
}
```

Or until timestamp.

## Activity / Token

Long-running tasks (e.g., human approval):
```json
"Approval": {
  "Type": "Task",
  "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
  "Parameters": {
    "FunctionName": "RequestApproval",
    "Payload": {"taskToken.$": "$$.Task.Token"}
  },
  "Next": "Continue"
}
```

Lambda receives token; later, human / system calls SendTaskSuccess with token → resume.

## Input / Output

ASL transformations:
- `InputPath`: select subset of input
- `Parameters`: build input for task
- `ResultSelector`: select from task result
- `ResultPath`: where to put result in state
- `OutputPath`: select for next state

Powerful; complex. JSONata (newer) for SQL-like transforms.

## CDK / Workflow Studio

Workflow Studio: visual editor.
CDK: code-defined state machines.

```typescript
const wf = new sfn.StateMachine(this, "OrderFlow", {
  definitionBody: sfn.DefinitionBody.fromChainable(
    new tasks.LambdaInvoke(this, "Validate", {lambdaFunction: validateFn})
      .next(new tasks.LambdaInvoke(this, "Charge", {lambdaFunction: chargeFn}))
      .next(new tasks.LambdaInvoke(this, "Ship", {lambdaFunction: shipFn}))
  )
});
```

## Use Cases

### ETL Orchestration
- Trigger: S3 event
- Steps: validate → transform → load → notify

### Order Processing
- Trigger: API
- Steps: validate → charge → reserve inventory → ship → email

### ML Pipeline
- Steps: data prep → train → eval → deploy

### Approval Flow
- Wait for human approval (token pattern)

### Cron Job
- EventBridge schedule → State machine → many Lambdas

## When Step Functions vs Direct

### Use Step Functions
- Multi-step workflow
- Need retries / error handling
- Visualization helps
- Cross-team workflow
- State transitions auditable

### Skip Step Functions
- Single Lambda
- Lambda calling Lambda once (just have first invoke second)
- Trivial flow

## Cost

Standard: $25/M state transitions + Lambda costs.

Example: 5-state workflow × 1M = $125 + Lambda.

Express: $1/M execution + GB-second.

For short high-volume: Express 10× cheaper.

## Limits

- 25,000 history events per execution (Standard)
- 256 KB input/output max per state
- 1 year max execution (Standard)

For huge: chain executions.

## Distributed Map

Process huge datasets:
- Read from S3 / inline
- 10,000 child executions concurrent
- Each is sub-state-machine
- For ETL on millions of items

## Monitoring

CloudWatch Step Functions metrics:
- ExecutionsStarted / Succeeded / Failed
- ExecutionTime

Per-state metrics if log level configured.

X-Ray integration.

## Common Mistakes

- Step Functions for trivial 2-step (overkill)
- Standard when Express fits (10× cost)
- 256 KB limit hit (store in S3; pass ref)
- No retries on transient errors
- All-or-nothing without Catch
- Forgetting timeout (TimeoutSeconds)

## Best Practices

- Express for short / high-volume
- Standard for long / complex
- Service integrations over Lambda where possible
- Retry on transient
- Catch + handle errors
- Timeout every Task
- Idempotent steps

## Quick Refs

```bash
# Create
aws stepfunctions create-state-machine --name MyFlow --definition file://flow.json --role-arn arn:...

# Start
aws stepfunctions start-execution --state-machine-arn ... --input '{...}'

# Describe
aws stepfunctions describe-execution --execution-arn ...

# History
aws stepfunctions get-execution-history --execution-arn ...
```

## Interview Prep

**Mid**: "When use Step Functions."

**Senior**: "Standard vs Express."

**Staff**: "Workflow design for ETL pipeline."

## Next Topic

→ [T06 — EventBridge, SQS, SNS](T06-EventBridge-SQS-SNS.md)
