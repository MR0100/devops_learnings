# L08/C12/T03 — SAM for Serverless

## Learning Objectives

- Use SAM for serverless IaC
- Local dev with SAM

## SAM

Serverless Application Model: CloudFormation extension for serverless.

Simpler syntax for Lambda + API Gateway + DynamoDB + etc.

Compiles to CFN.

## Install

```bash
brew install aws-sam-cli
```

## Init

```bash
sam init --runtime python3.11 --name myapp
```

## template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.11
    Timeout: 30
    Tracing: Active

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.handler
      Environment:
        Variables:
          TABLE_NAME: !Ref MyTable
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get

  MyTable:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: id
        Type: String
```

## Resource Types

- AWS::Serverless::Function (Lambda + auto IAM)
- AWS::Serverless::Api (API Gateway REST)
- AWS::Serverless::HttpApi (API Gateway HTTP)
- AWS::Serverless::SimpleTable (DynamoDB)
- AWS::Serverless::Application (nested SAM)
- AWS::Serverless::StateMachine (Step Functions)
- AWS::Serverless::LayerVersion

## Events

Wire Lambda to trigger:
```yaml
Events:
  Schedule:
    Type: Schedule
    Properties:
      Schedule: rate(1 hour)
  
  S3Event:
    Type: S3
    Properties:
      Bucket: !Ref MyBucket
      Events: s3:ObjectCreated:*
  
  SqsEvent:
    Type: SQS
    Properties:
      Queue: !GetAtt MyQueue.Arn
```

Auto-creates trigger + IAM permissions.

## Build & Deploy

```bash
sam build           # build artifacts
sam deploy --guided # interactive first time
sam deploy          # subsequent
```

`sam deploy --guided`: walks through stack name, region, IAM ack.

Stores config in `samconfig.toml`:
```toml
[default.deploy.parameters]
stack_name = "myapp"
region = "us-east-1"
capabilities = "CAPABILITY_IAM"
```

## Local Dev

### Invoke Function Locally
```bash
sam local invoke MyFunction -e events/api.json
```

Runs in Docker; simulates Lambda.

### Start Local API
```bash
sam local start-api
# → http://localhost:3000
```

Local API Gateway emulator. Hot-reload code.

### Generate Test Event
```bash
sam local generate-event api → event.json
sam local generate-event s3 → event.json
```

### Step Through (Debug)
With debug port:
```bash
sam local invoke MyFunction --debug-port 5858
```

Attach VS Code debugger.

## Build Process

```bash
sam build
```

For each function:
- Detect runtime
- Install deps (pip, npm, etc.)
- Copy to .aws-sam/build/

Use `--use-container` for Linux build in Docker (matches Lambda env).

## Container Lambda

```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    PackageType: Image
    ImageConfig:
      Command: ["app.handler"]
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .
```

SAM builds container; pushes to ECR.

## SAM Pipelines

`sam pipeline init`:
- Generates CI/CD pipeline (CodePipeline, GitHub Actions, Jenkins)
- For multi-account deploy (dev → staging → prod)

## Logs

```bash
sam logs --name MyFunction --tail
```

Stream CloudWatch Logs.

## SAM vs CDK

| | SAM | CDK |
|---|---|---|
| Format | YAML + Transform | Code (TS/Python/...) |
| Focus | Serverless | All AWS |
| Complexity | Simple | More flexible |
| Local dev | Strong | Improving |
| When | Serverless-only | Mixed / general |

For pure serverless: SAM.
For mixed app: CDK.

## SAM Accelerate (Sync)

Fast iteration:
```bash
sam sync --watch
```

On code change: incremental update; no full deploy.

Cuts deploy from minutes to seconds during dev.

## Layer

```yaml
MyLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    LayerName: my-libs
    ContentUri: layer/
    CompatibleRuntimes: [python3.11]

MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Layers:
      - !Ref MyLayer
```

## Policies

SAM has policy templates:
```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - AmazonS3ReadOnlyAccess
      - DynamoDBCrudPolicy:
          TableName: !Ref MyTable
      - SQSPollerPolicy:
          QueueName: !GetAtt MyQueue.QueueName
```

Templates expand to least-privilege.

## Globals

Shared properties:
```yaml
Globals:
  Function:
    Runtime: python3.11
    Timeout: 30
    MemorySize: 512
    Tracing: Active
    Environment:
      Variables:
        LOG_LEVEL: INFO
```

Each function inherits.

## Cross-Account / Multi-Env

Same template; different parameters per env:
```bash
sam deploy --parameter-overrides Env=prod --stack-name myapp-prod
```

Or `samconfig.toml`:
```toml
[prod.deploy.parameters]
stack_name = "myapp-prod"
parameter_overrides = "Env=prod"
```

## Best Practices

- Globals for shared
- Policy templates over inline IAM
- Local dev for fast iteration
- `sam sync` for accelerated dev
- Pipelines for multi-env
- Layers for shared deps

## Common Mistakes

- Manual SAM commands instead of pipeline
- No local testing
- Hardcoded resource ARNs
- Forgetting policy templates

## Integration with CDK

CDK can incorporate SAM (transform). Mostly: pick one.

## Quick Refs

```bash
sam init --runtime python3.11
sam build
sam local invoke MyFunction
sam local start-api
sam deploy --guided
sam logs --name MyFunction --tail
sam sync --watch
```

## Interview Prep

**Mid**: "SAM purpose."

**Senior**: "SAM vs CDK for serverless."

**Staff**: "Serverless deploy pipeline."

## Next Topic

→ Move to [L08/C13 — Security & Compliance](../C13/README.md)
