# L10/C07/T02 — AWS CDK (TypeScript, Python)

## Learning Objectives

- Use AWS CDK
- Pick vs Terraform

## Recap from L08/C12/T02

CDK basics covered. This focuses on Terraform comparison + advanced.

## CDK vs Terraform

| | CDK | Terraform |
|---|---|---|
| Language | TS/Python/Java/C#/Go | HCL |
| Cloud | AWS-native | Multi |
| State | CloudFormation | Self-managed |
| Modules | Constructs (L1/L2/L3) | Modules |
| Drift | CFN detection | terraform plan |
| Community | Growing | Largest |
| Learning curve | Lower (if know lang) | DSL |
| Cost | Free | Free + paid TFC |

## L1 / L2 / L3 Constructs

### L1 (Cfn Resources)
```typescript
import { CfnBucket } from "aws-cdk-lib/aws-s3";

const bucket = new CfnBucket(this, "Bucket", {
    versioningConfiguration: { status: "Enabled" },
});
```

1:1 with CFN. Raw.

### L2 (Recommended)
```typescript
import * as s3 from "aws-cdk-lib/aws-s3";

const bucket = new s3.Bucket(this, "Bucket", {
    versioned: true,
    encryption: s3.BucketEncryption.S3_MANAGED,
    blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
});
```

Higher-level; sensible defaults.

### L3 (Patterns)
```typescript
import { ApplicationLoadBalancedFargateService } from "aws-cdk-lib/aws-ecs-patterns";

const service = new ApplicationLoadBalancedFargateService(this, "App", {
    taskImageOptions: { image: ContainerImage.fromRegistry("nginx") },
    publicLoadBalancer: true,
});
```

Pattern: complete service in one construct.

## CDK Stack

```typescript
import { Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";

export class MyStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);
        
        // Resources...
    }
}
```

## App + Stack

```typescript
// bin/app.ts
import { App } from "aws-cdk-lib";
import { MyStack } from "../lib/my-stack";

const app = new App();

new MyStack(app, "prod-stack", {
    env: { account: "123", region: "us-east-1" },
});

new MyStack(app, "staging-stack", {
    env: { account: "456", region: "us-east-1" },
});
```

Multiple stacks; per environment.

## Construct Composition

```typescript
export class WebAppConstruct extends Construct {
    public readonly url: string;
    
    constructor(scope: Construct, id: string, props: WebAppProps) {
        super(scope, id);
        
        const vpc = new ec2.Vpc(this, "Vpc");
        const cluster = new ecs.Cluster(this, "Cluster", { vpc });
        const service = new ecs_patterns.ApplicationLoadBalancedFargateService(this, "Service", {
            cluster,
            taskImageOptions: { image: props.image },
        });
        
        this.url = service.loadBalancer.loadBalancerDnsName;
    }
}
```

Reusable. Used as:
```typescript
const app = new WebAppConstruct(this, "MyApp", {
    image: ContainerImage.fromRegistry("nginx"),
});
```

## Cross-Stack References

```typescript
// network-stack.ts
this.vpc = new ec2.Vpc(...);

// app-stack.ts
new App(this, "App", { vpc: networkStack.vpc });
```

CDK auto-generates CFN exports.

## Context

`cdk.json`:
```json
{
  "context": {
    "env": "dev"
  }
}
```

Code:
```typescript
const env = this.node.tryGetContext("env");
```

For: env-specific values.

## Deploy

```bash
cdk bootstrap   # one-time per account+region
cdk synth       # generate CFN
cdk diff        # vs deployed
cdk deploy      # apply
cdk destroy     # tear down
```

## Hot Reload (cdk watch)

```bash
cdk watch
```

Re-synth on code change; deploys delta.

For: fast iteration.

## CDK Pipelines

Self-mutating CI/CD:
```typescript
const pipeline = new CodePipeline(this, "Pipeline", {
    pipelineName: "MyPipeline",
    synth: new ShellStep("Synth", {
        input: CodePipelineSource.gitHub("myorg/repo", "main"),
        commands: ["npm install", "npm run build", "npx cdk synth"],
    }),
});

pipeline.addStage(new MyAppStage(this, "Dev"));
pipeline.addStage(new MyAppStage(this, "Prod", { env }));
```

Per-stage: deploy stack.

Pipeline updates itself on code change.

## Assets

Bundle code:
```typescript
new lambda.Function(this, "F", {
    code: lambda.Code.fromAsset("lambda/"),
    runtime: lambda.Runtime.PYTHON_3_11,
    handler: "app.handler",
});
```

CDK zips, uploads to S3, references.

## Container Assets

```typescript
new lambda.DockerImageFunction(this, "F", {
    code: lambda.DockerImageCode.fromImageAsset("docker-image/"),
});
```

CDK builds image, pushes to ECR.

## Aspects

Apply to all in scope:
```typescript
Aspects.of(this).add(new Tag("Env", "prod"));
```

Auto-tags all resources.

## CDK vs Pulumi

Both: real languages, programmatic IaC.

| | CDK | Pulumi |
|---|---|---|
| Cloud | AWS-native (CDK for Terraform extends) | Multi (Terraform providers under) |
| State | CFN | Pulumi Cloud / self |
| Distribution | npm / pip | npm / pip |
| Drift | CFN | Pulumi refresh |
| Cost | Free | Free + paid Cloud |

For AWS: CDK strong.
For multi-cloud: Pulumi.

## CDK Best Practices

- Use L2 (not L1)
- Constructs for reuse
- Aspects for cross-cutting
- Tests
- Pipelines (self-mutating)
- env per stack
- Stack per environment

## Common Mistakes

- All L1 (defeats purpose)
- One giant stack (slow deploy)
- Hardcoded values
- No context (env-specific)
- Bootstrap forgotten

## CDK for Terraform (cdktf)

Use CDK style + Terraform backend:
```typescript
import { Construct } from "constructs";
import { TerraformStack, App } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";

class MyStack extends TerraformStack {
    constructor(scope: Construct, id: string) {
        super(scope, id);
        
        new AwsProvider(this, "aws", { region: "us-east-1" });
        new S3Bucket(this, "Bucket", { bucket: "my-bucket" });
    }
}

const app = new App();
new MyStack(app, "my-stack");
app.synth();
```

Synth → terraform.tf.json → terraform apply.

For: like CDK style + Terraform backend.

## Generated CFN

```bash
cdk synth
# Outputs cdk.out/*.template.json
```

CloudFormation template. Apply via CFN.

For: review, audit.

## Drift Detection

```bash
aws cloudformation detect-stack-drift --stack-name MyStack
```

CFN-native.

CDK can be in sync; CFN drift visible.

## Custom Resources

For things CFN doesn't natively support:
```typescript
new CustomResource(this, "MyResource", {
    serviceToken: provider.serviceToken,
    properties: { ... },
});
```

Lambda-backed.

## Multi-Account

```typescript
new MyStack(app, "ProdStack", {
    env: { account: "PROD_ACCT", region: "us-east-1" },
});

new MyStack(app, "DevStack", {
    env: { account: "DEV_ACCT", region: "us-east-1" },
});
```

Per-account credentials needed.

## CDK Pipelines Cross-Account

Pipeline in tools account; deploys to prod/dev:
```typescript
pipeline.addStage(new MyAppStage(this, "Prod", {
    env: { account: "PROD", region: "us-east-1" },
}));
```

CDK Pipelines handles cross-account roles.

## Quick Refs

```bash
cdk init app --language typescript
cdk bootstrap
cdk synth
cdk diff
cdk deploy
cdk destroy
cdk watch
```

## Interview Prep

**Mid**: "CDK vs Terraform."

**Senior**: "L1/L2/L3 constructs."

**Staff**: "CDK + Pipelines for org."

## Next Topic

→ [T03 — CDK for Terraform (CDKTF)](T03-CDKTF.md)
