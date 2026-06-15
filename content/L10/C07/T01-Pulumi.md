# L10/C07/T01 — Pulumi (Real Programming Languages)

## Learning Objectives

- Use Pulumi
- Compare with Terraform

## Pulumi

IaC using real languages:
- TypeScript / JavaScript
- Python
- Go
- C# / .NET
- Java
- YAML

vs Terraform's HCL.

## Install

```bash
brew install pulumi
pulumi login
```

## Init

```bash
mkdir my-infra && cd my-infra
pulumi new aws-typescript
```

Generates project + boilerplate.

## TypeScript Example

```typescript
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("my-bucket", {
    versioning: {
        enabled: true,
    },
    serverSideEncryptionConfiguration: {
        rule: {
            applyServerSideEncryptionByDefault: {
                sseAlgorithm: "AES256",
            },
        },
    },
});

export const bucketName = bucket.id;
```

Standard TypeScript.

## Python Example

```python
import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket("my-bucket",
    versioning=aws.s3.BucketVersioningArgs(enabled=True),
    server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
        rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="AES256",
            ),
        ),
    ),
)

pulumi.export("bucket_name", bucket.id)
```

## Go Example

```go
package main

import (
    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/s3"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
    pulumi.Run(func(ctx *pulumi.Context) error {
        bucket, err := s3.NewBucket(ctx, "my-bucket", &s3.BucketArgs{
            Versioning: &s3.BucketVersioningArgs{
                Enabled: pulumi.Bool(true),
            },
        })
        if err != nil {
            return err
        }
        
        ctx.Export("bucket_name", bucket.ID())
        return nil
    })
}
```

## Stacks

Like Terraform workspaces:
```bash
pulumi stack init dev
pulumi stack init prod
pulumi stack select prod
```

Each stack: own state, own config.

## Configuration

```bash
pulumi config set aws:region us-east-1
pulumi config set --secret db_password mySecret
```

```typescript
const config = new pulumi.Config();
const region = config.require("region");
const dbPassword = config.requireSecret("db_password");
```

Per-stack values.

## Backend

Default: Pulumi Cloud (free for individuals).

Self-hosted:
```bash
pulumi login s3://my-state-bucket
pulumi login azblob://...
pulumi login gs://...
```

## Pros vs Terraform

### Real Languages
- Loops (for, while)
- Conditionals (if, ternary)
- Functions
- Classes / inheritance
- Type checking (TS, Go)
- IDE autocomplete

### Better Abstractions
- Reusable classes
- Inheritance for similar resources
- Standard library functions

### Same Provider Ecosystem
Pulumi uses Terraform providers under the hood (via Pulumi providers wrapping).

## Cons vs Terraform

### Smaller Community
Fewer modules, examples.

### Language Choice = Lock-in
Team must know language.

### State Backend
Pulumi Cloud (paid for teams) or self-host.

### Less Mature
Terraform has 10 years; Pulumi ~5.

## Components (Reusable)

```typescript
class WebApp extends pulumi.ComponentResource {
    constructor(name: string, args: WebAppArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:WebApp", name, {}, opts);
        
        const lb = new aws.lb.LoadBalancer(...);
        const cluster = new aws.ecs.Cluster(...);
        const service = new aws.ecs.Service(...);
        
        this.url = lb.dnsName;
    }
    
    public readonly url: pulumi.Output<string>;
}

const app = new WebApp("my-app", {
    image: "nginx",
    desiredCount: 3,
});
```

Reusable as class.

## Outputs

```typescript
const bucket = new aws.s3.Bucket(...);
export const bucketUrl = pulumi.interpolate`https://${bucket.bucketDomainName}`;
```

Outputs are async (Output<T>). Use `pulumi.interpolate` for string interp.

## Apply

```bash
pulumi up
# Shows diff
# y/n
```

Like terraform apply.

## Destroy

```bash
pulumi destroy
```

## Stack Outputs

```bash
pulumi stack output
# bucket_name: my-bucket-abc
```

## Cross-Stack References

```typescript
const otherStack = new pulumi.StackReference("org/network/prod");
const vpcId = otherStack.getOutput("vpc_id");

const subnet = new aws.ec2.Subnet("my-subnet", {
    vpcId: vpcId as pulumi.Output<string>,
    ...
});
```

For: cross-team / cross-workload references.

## Comparison Matrix

| | Terraform | Pulumi | CDK |
|---|---|---|---|
| Language | HCL | TS/Python/Go/etc | TS/Python/etc |
| Cloud | Multi | Multi | AWS-native |
| State | Terraform backends | Pulumi Cloud / self | CFN |
| Maturity | High | Medium | Medium |
| Community | Largest | Growing | Growing |
| Cost | Free + paid Cloud | Free + paid Cloud | Free |

## When Pulumi

- Team prefers programming language
- Complex logic (lots of conditionals/loops)
- Want IDE autocomplete + type checking
- Don't want HCL

## When Terraform

- Large community + modules
- HCL acceptable
- Multi-tool standards (Terraform popular)

## When CDK

- AWS-only
- Want TypeScript (CDK biggest there)

## Migration Terraform → Pulumi

```bash
pulumi convert --from terraform
```

Imports existing TF state.

Plus refactor manually for idioms.

## Testing

Use language test frameworks:
```typescript
// TypeScript
import "mocha";
import { expect } from "chai";

describe("Bucket", () => {
    it("has versioning", () => {
        // ...
    });
});
```

```python
# Python
import unittest

class TestBucket(unittest.TestCase):
    def test_versioning(self):
        ...
```

Real test frameworks; familiar.

## Policy as Code

Pulumi CrossGuard:
```typescript
new PolicyPack("aws-policies", {
    policies: [{
        name: "s3-versioning-required",
        enforcementLevel: "mandatory",
        validateResource: validateResourceOfType(aws.s3.Bucket, (bucket, args, reportViolation) => {
            if (!bucket.versioning?.enabled) {
                reportViolation("S3 bucket must have versioning");
            }
        }),
    }],
});
```

For: enforce standards.

## CI/CD

```yaml
- uses: pulumi/actions@v4
  with:
    command: up
    stack-name: prod
    cloud-url: s3://my-state
```

GitHub Actions integration.

## Best Practices

- Components for reuse
- Strong typing
- Config per stack
- Cross-stack refs for dependencies
- Tests
- Policy as Code
- Semver for components

## Common Mistakes

- Synchronous treating async outputs
- Hardcoded values
- No tests
- Big main file (split into components)

## Quick Refs

```bash
pulumi new aws-typescript
pulumi stack init NAME
pulumi up
pulumi destroy
pulumi config set KEY VALUE
pulumi stack output
pulumi refresh
```

## Interview Prep

**Mid**: "Pulumi vs Terraform."

**Senior**: "When pick Pulumi."

**Staff**: "Pulumi for 100-team platform."

## Next Topic

→ [T02 — AWS CDK (TypeScript, Python)](T02-AWS-CDK.md)
