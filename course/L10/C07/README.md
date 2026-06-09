# L10/C07 — Pulumi & CDK

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Pulumi.md) | Pulumi (Real Programming Languages) | 1 hr |
| [T02](T02-AWS-CDK.md) | AWS CDK (TypeScript, Python) | 1 hr |
| [T03](T03-CDKTF.md) | CDK for Terraform (CDKTF) | 0.5 hr |

## Pulumi

IaC using real programming languages: TypeScript, Python, Go, Java, .NET.

```typescript
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const env = config.require("env");

const bucket = new aws.s3.Bucket("data", {
    versioning: { enabled: true },
    tags: { Environment: env },
});

export const bucketName = bucket.id;
```

### Why Pulumi
- Loops, conditionals, types
- Real testing (mocha, pytest)
- IDE support, refactoring
- Multi-cloud (uses same providers as Terraform — TF plugins, then CrossLang)
- Stack outputs feed into other stacks easily

### State
- Pulumi Cloud (SaaS, default) — like Terraform Cloud
- Self-hosted backend (S3, Azure Blob, etc.) — like Terraform OSS

### Vs Terraform
| | Pulumi | Terraform |
|---|---|---|
| Language | TS/Py/Go/Java/.NET | HCL |
| Multi-cloud | Yes | Yes |
| Ecosystem | Smaller | Largest |
| Engineer onboarding | Easier (real lang) | New DSL |
| State | SaaS or self | SaaS or self |

Use Pulumi if your team is strong in TS/Python and likes real lang ergonomics. Use Terraform for the largest ecosystem.

## AWS CDK

Define AWS infra in real languages. Synthesizes to CloudFormation.

```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

class MyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new s3.Bucket(this, 'Data', {
      versioned: true,
      encryption: s3.BucketEncryption.KMS_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });
  }
}

const app = new cdk.App();
new MyStack(app, 'MyStack');
```

### Construct Levels
- **L1 (CfnXxx)**: 1:1 with CloudFormation resources
- **L2 (most use)**: opinionated, sensible defaults
- **L3 (Patterns)**: complete arch (e.g., `ApplicationLoadBalancedFargateService`)

### Why CDK
- AWS-native (CloudFormation under the hood)
- AWS-deep (best AWS service coverage)
- TypeScript / Python ergonomics
- Generated AWS-managed types (always current with API)

### CDK Limitations
- AWS-only (use CDKTF for multi-cloud)
- CloudFormation idiosyncrasies surface
- Some resources not yet in CDK (use L1)

### Commands
```bash
cdk init app --language typescript
cdk synth                 # to CloudFormation YAML
cdk diff
cdk deploy
cdk deploy --all
cdk destroy
cdk bootstrap             # one-time
```

## CDK for Terraform (CDKTF)

Use real languages to generate Terraform JSON.

```typescript
import { App, TerraformStack } from "cdktf";
import { Construct } from "constructs";
import * as aws from "@cdktf/provider-aws";

class MyStack extends TerraformStack {
  constructor(scope: Construct, id: string) {
    super(scope, id);
    new aws.provider.AwsProvider(this, "AWS", { region: "us-east-1" });
    new aws.s3Bucket.S3Bucket(this, "Data", { bucket: "my-bucket" });
  }
}

const app = new App();
new MyStack(app, "my-stack");
app.synth();
```

CDKTF synthesizes to `terraform.tf.json`; you run regular `terraform apply`.

### When CDKTF
- Want real language but multi-cloud (Terraform's provider catalog)
- Existing Terraform investment + want better ergonomics
- Less ecosystem maturity than CDK or Pulumi

## CDK vs Pulumi vs Terraform — Choosing

| Need | Pick |
|---|---|
| Multi-cloud + HCL is fine | Terraform |
| AWS-only + TypeScript/Python team | CDK |
| Multi-cloud + want real language | Pulumi |
| Existing Terraform + want code ergonomics | CDKTF |
| Strong type safety, testing | CDK or Pulumi |
| Largest community + 3rd-party modules | Terraform |

## Interview Themes

- "Compare CDK, Pulumi, Terraform"
- "When CDK over Terraform?"
- "What does CDK's synth produce?"
- "L1, L2, L3 constructs — what are they?"
- "Why is Terraform still preferred at many companies?"
