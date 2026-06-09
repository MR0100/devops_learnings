# L08/C12/T02 — CDK (TypeScript, Python)

## Learning Objectives

- Use CDK
- Build constructs

## CDK

Cloud Development Kit: define infrastructure in programming languages.

Languages:
- TypeScript (most popular)
- Python
- Java
- C#
- Go (preview)

Compiles to CloudFormation; deploys.

## Why CDK

vs CFN YAML:
- Programmatic (loops, conditionals)
- Type-checking (IDE help)
- Reusable constructs
- Easier complex setups
- Generates CFN under hood

vs Terraform:
- AWS-native; deep service support
- TypeScript / Python familiar to devs
- Built on CFN (so similar drift / change set behavior)

## Install

```bash
npm install -g aws-cdk
```

## Initialize

```bash
mkdir my-app && cd my-app
cdk init app --language typescript
```

Project structure:
```
my-app/
├── bin/my-app.ts    # entry
├── lib/my-app-stack.ts # stack
├── package.json
├── cdk.json         # config
└── tsconfig.json
```

## Basic Stack

```typescript
import * as cdk from "aws-cdk-lib";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export class MyAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, "MyBucket", {
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    const fn = new lambda.Function(this, "Handler", {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset("lambda"),
      handler: "app.handler",
      environment: {BUCKET: bucket.bucketName},
    });

    bucket.grantRead(fn);    // automatic IAM
  }
}
```

`grantRead`: high-level; auto-generates IAM policy.

## Deploy

```bash
cdk bootstrap         # one-time per account+region
cdk synth             # generate CFN
cdk diff              # vs deployed
cdk deploy            # deploy
cdk destroy           # tear down
```

## Bootstrap

CDK needs S3 bucket for asset uploads + IAM role:
```bash
cdk bootstrap aws://123/us-east-1
```

Once per account+region.

## Constructs

Three levels:
- **L1**: 1:1 CFN resource (auto-generated)
- **L2**: opinionated higher-level (aws-cdk-lib)
- **L3**: pattern (aws-solutions-constructs)

Most app code uses L2.

## L1 Example
```typescript
import { CfnBucket } from "aws-cdk-lib/aws-s3";
const bucket = new CfnBucket(this, "Bucket", {versioningConfiguration: {status: "Enabled"}});
```

Maps directly to CFN.

## L2 Example
```typescript
const bucket = new s3.Bucket(this, "Bucket", {
  versioned: true,
  encryption: s3.BucketEncryption.KMS_MANAGED,
});
```

Higher-level; sensible defaults.

## L3 Example
```typescript
import { ApiGatewayToLambda } from "@aws-solutions-constructs/aws-apigateway-lambda";

new ApiGatewayToLambda(this, "ApiToLambda", {
  lambdaFunctionProps: {
    runtime: lambda.Runtime.PYTHON_3_11,
    handler: "app.handler",
    code: lambda.Code.fromAsset("lambda"),
  },
});
```

Pattern: complete API + Lambda in one construct.

## Custom Constructs

Build your own:
```typescript
export class MyWebApp extends Construct {
  public readonly url: string;
  
  constructor(scope: Construct, id: string, props: MyWebAppProps) {
    super(scope, id);
    
    const bucket = new s3.Bucket(this, "Assets", {...});
    const cf = new cloudfront.Distribution(this, "CDN", {...});
    
    this.url = cf.distributionDomainName;
  }
}
```

Reusable across teams.

## Multiple Stacks

```typescript
// bin/my-app.ts
const app = new cdk.App();
new NetworkStack(app, "Network");
new AppStack(app, "App", {vpc: networkStack.vpc});
new DbStack(app, "Db", {vpc: networkStack.vpc});
```

Each stack independent CFN.

## Cross-Stack References

CDK handles:
```typescript
const network = new NetworkStack(app, "Network");
new AppStack(app, "App", {vpc: network.vpc});

// In AppStack constructor:
// Can use props.vpc; CDK auto-creates CFN exports
```

vs CFN manual `!ImportValue`.

## Context

```bash
cdk deploy --context env=prod
```

In code:
```typescript
const env = this.node.tryGetContext("env");
```

Or `cdk.json`:
```json
{
  "context": {
    "env": "dev"
  }
}
```

## Environment

Specify account + region:
```typescript
new AppStack(app, "AppStack", {
  env: {
    account: "123",
    region: "us-east-1"
  }
});
```

For multi-account: deploy per environment.

## Assets

Bundle code:
```typescript
new lambda.Function(this, "F", {
  code: lambda.Code.fromAsset("lambda/"),
});
```

CDK zips, uploads to S3, references in Lambda.

Container assets:
```typescript
new lambda.DockerImageFunction(this, "F", {
  code: lambda.DockerImageCode.fromImageAsset("docker-image/"),
});
```

CDK builds image, pushes to ECR.

## Permissions

High-level helpers:
```typescript
bucket.grantRead(fn);          # auto-IAM
queue.grantSendMessages(fn);
table.grantReadWriteData(fn);
```

Cleaner than writing IAM JSON.

## Testing

Unit tests for CDK:
```typescript
import { Template } from "aws-cdk-lib/assertions";

test("bucket created", () => {
  const stack = new MyAppStack();
  const template = Template.fromStack(stack);
  template.resourceCountIs("AWS::S3::Bucket", 1);
});
```

Catch regressions.

## CDK Pipelines

Self-mutating CI/CD:
- Stack defines pipeline
- Pipeline deploys app stacks
- Pipeline updates itself

```typescript
const pipeline = new CodePipeline(this, "Pipeline", {...});
pipeline.addStage(new MyStage(this, "Prod", {env}));
```

Full IaC + CI/CD in one repo.

## Limitations

- Synthesis takes seconds (slower iteration than HCL)
- Generated CFN can be huge
- Sometimes leaky abstractions

## CDK vs Terraform

| | CDK | Terraform |
|---|---|---|
| Language | TS/Python/Java/C# | HCL |
| Provider | AWS-native | Multi-cloud |
| State | CFN | Self-managed |
| Modules | Constructs | Modules |
| Learning curve | Lower (if know lang) | DSL to learn |
| Community | Growing | Massive |
| Drift | CFN detect | terraform plan |

For AWS-only + dev team: CDK.
For multi-cloud / Terraform ecosystem: Terraform.

## CDKTF

CDK for Terraform: TS/Python → Terraform. Best of both?

Niche but growing.

## Best Practices

- Constructs for reuse
- Separate networking from app stacks
- Environment-specific stacks
- Tests for stacks
- CDK Pipelines for self-deploy
- Bootstrap per account+region

## Common Mistakes

- Single huge stack (slow deploys)
- Hardcoded values (use context / props)
- Lots of L1 (defeats purpose; use L2)
- Manual changes (drift)
- Sharing too much state via context

## Quick Refs

```bash
# Init
cdk init app --language typescript

# Bootstrap
cdk bootstrap

# Synth (preview)
cdk synth

# Diff
cdk diff

# Deploy
cdk deploy

# Destroy
cdk destroy
```

## Interview Prep

**Mid**: "CDK basics."

**Senior**: "Custom construct design."

**Staff**: "CDK vs Terraform tradeoffs."

## Next Topic

→ [T03 — SAM for Serverless](T03-SAM.md)
