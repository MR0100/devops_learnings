# L10/C07/T03 — CDK for Terraform (CDKTF)

## Learning Objectives

- Use CDKTF
- Combine CDK style + Terraform

## CDKTF

CDK style; Terraform under hood.

Code → synth → Terraform JSON → terraform apply.

For: programming language + Terraform ecosystem.

## Install

```bash
npm install -g cdktf-cli
cdktf init --template=typescript --providers=aws@~>5.0
```

## Project

```typescript
// main.ts
import { Construct } from "constructs";
import { App, TerraformStack } from "cdktf";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";

class MyStack extends TerraformStack {
    constructor(scope: Construct, id: string) {
        super(scope, id);
        
        new AwsProvider(this, "aws", { region: "us-east-1" });
        
        new S3Bucket(this, "my_bucket", {
            bucket: "my-unique-bucket",
            versioning: [{ enabled: true }],
        });
    }
}

const app = new App();
new MyStack(app, "my-stack");
app.synth();
```

## Synth

```bash
cdktf synth
```

Generates Terraform JSON in `cdktf.out/stacks/my-stack/cdk.tf.json`.

## Deploy

```bash
cdktf deploy
```

Runs `terraform init && terraform apply` internally.

Or:
```bash
cdktf synth
cd cdktf.out/stacks/my-stack
terraform init
terraform apply
```

For: standard Terraform workflow on generated.

## Provider Generation

```bash
cdktf get
```

Downloads providers + generates typed bindings.

```json
// cdktf.json
{
  "terraformProviders": [
    "aws@~> 5.0",
    "google@~> 5.0"
  ],
  "terraformModules": [
    "terraform-aws-modules/vpc/aws@~> 5.0"
  ]
}
```

## Modules

```typescript
import { Vpc } from "./.gen/modules/terraform-aws-modules/vpc/aws";

new Vpc(this, "vpc", {
    name: "my-vpc",
    cidr: "10.0.0.0/16",
    azs: ["us-east-1a", "us-east-1b", "us-east-1c"],
    privateSubnets: ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
});
```

Use existing Terraform modules.

## Backend

```typescript
new S3Backend(this, {
    bucket: "tfstate",
    key: "stacks/my-stack/terraform.tfstate",
    region: "us-east-1",
});
```

Standard Terraform backends.

## CDKTF vs CDK

| | CDK | CDKTF |
|---|---|---|
| Backend | CloudFormation | Terraform |
| Cloud | AWS-native | Multi via TF providers |
| Drift | CFN | terraform plan |
| Tooling | AWS-specific | Terraform ecosystem |
| Maturity | Higher | Growing |

For: CDK style + Terraform features → CDKTF.
For: AWS-only → CDK.

## CDKTF vs Pulumi

Both: programming language + Terraform providers (under).

CDKTF: HashiCorp-developed; tighter Terraform integration.
Pulumi: Independent; broader ecosystem; richer SDK.

For Terraform users: CDKTF easier transition.
For greenfield: Pulumi might be more polished.

## Use Cases

### Migrate HCL → Code
For complex logic; loops, classes.

### Type Safety
Compile-time checking; IDE help.

### Reuse Constructs
Classes for repeated patterns.

## Stack Output

```typescript
import { TerraformOutput } from "cdktf";

new TerraformOutput(this, "bucket_name", {
    value: bucket.bucket,
});
```

```bash
cdktf output
```

## Variables

```typescript
import { TerraformVariable } from "cdktf";

const env = new TerraformVariable(this, "env", {
    type: "string",
    default: "dev",
});

new S3Bucket(this, "b", {
    bucket: `bucket-${env.value}`,
});
```

## Iteration

```typescript
const envs = ["dev", "staging", "prod"];
for (const env of envs) {
    new S3Bucket(this, `bucket-${env}`, {
        bucket: `my-${env}-bucket`,
    });
}
```

Vanilla TypeScript loops. Cleaner than HCL `for_each`.

## Conditional

```typescript
if (env === "prod") {
    new BackupVault(this, "backup", { ... });
}
```

## Aspects

```typescript
import { Aspects } from "cdktf";

class TagAspect implements IAspect {
    visit(node: IConstruct): void {
        if (node instanceof TerraformResource) {
            (node as any).tagsInput = { Env: "prod" };
        }
    }
}

Aspects.of(this).add(new TagAspect());
```

For: cross-cutting concerns.

## Imports (Existing Resources)

```typescript
S3Bucket.generateConfigForImport(this, "existing", "my-existing-bucket");
```

Then `cdktf plan` shows import.

## Stack Dependencies

```typescript
const networkStack = new NetworkStack(app, "network");
const appStack = new AppStack(app, "app", { vpc: networkStack.vpc });
```

Pass references across stacks.

## CI/CD

```yaml
- run: npm install
- run: cdktf get
- run: cdktf synth
- run: cdktf deploy --auto-approve
```

Or split:
```yaml
- run: cdktf synth
- run: cd cdktf.out/stacks/X && terraform plan
- # approval
- run: cd cdktf.out/stacks/X && terraform apply plan
```

## Testing

Snapshot tests:
```typescript
import { Testing } from "cdktf";

test("creates bucket", () => {
    const stack = new MyStack(Testing.app(), "test");
    expect(Testing.synth(stack)).toMatchSnapshot();
});
```

Or specific:
```typescript
expect(Testing.synth(stack)).toHaveResource(S3Bucket);
```

## When CDKTF

- TypeScript / Python team
- Terraform ecosystem
- Want type safety
- Complex logic

## When Pure Terraform

- Team comfortable with HCL
- Simple infrastructure
- HCL features sufficient

## When Pulumi

- Multi-cloud first-class
- Want polished SDK
- Not tied to Terraform

## Best Practices

- Stacks per env/region
- Constructs for reuse
- Aspects for tags
- Tests
- Lock CDKTF version
- Generate providers regularly

## Common Mistakes

- All in one stack
- No type safety usage (loose any)
- Forgetting cdktf get
- Outdated provider bindings

## Migration HCL → CDKTF

1. Convert HCL to CDKTF:
```bash
cdktf convert --provider aws@~>5.0 < main.tf > main.ts
```

2. Cleanup; refactor to classes
3. Test
4. Adopt

## Pulumi Comparison

```typescript
// Pulumi (TypeScript)
import * as aws from "@pulumi/aws";
const bucket = new aws.s3.Bucket("my", {versioning: {enabled: true}});

// CDKTF (TypeScript)
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
const bucket = new S3Bucket(this, "my", { bucket: "my", versioning: [{enabled: true}] });
```

Similar; details differ.

## Multi-Cloud

```typescript
new AwsProvider(this, "aws", { region: "us-east-1" });
new GoogleProvider(this, "google", { project: "my-project" });

new S3Bucket(this, "s3", { ... });
new GoogleStorageBucket(this, "gcs", { ... });
```

Mix providers per stack.

## Quick Refs

```bash
cdktf init --template=typescript
cdktf get
cdktf synth
cdktf plan
cdktf deploy
cdktf destroy
cdktf output
```

## Interview Prep

**Mid**: "CDKTF purpose."

**Senior**: "CDKTF vs Pulumi."

**Staff**: "Programming-language IaC strategy."

## Next Topic

→ Move to [L10/C08 — Best Practices](../C08/README.md)
