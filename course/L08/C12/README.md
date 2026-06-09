# L08/C12 — Infrastructure as Code on AWS

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-CloudFormation.md) | CloudFormation (Templates, Stacks, StackSets) | 1.5 hr |
| [T02](T02-CDK.md) | CDK (TypeScript, Python) | 1.5 hr |
| [T03](T03-SAM.md) | SAM for Serverless | 0.5 hr |

## CloudFormation

AWS-native IaC. Declarative YAML/JSON.

### Concepts
- **Template**: YAML/JSON describing resources
- **Stack**: deployment of a template; tracks resources created
- **Change Set**: preview of changes before applying
- **Drift Detection**: compare actual vs declared
- **Stack Set**: deploy same stack to multiple accounts/regions

### Template Sections
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: My stack

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

Mappings:
  RegionMap:
    us-east-1: {AmiId: ami-abc}
    us-west-2: {AmiId: ami-def}

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "myapp-${Environment}-${AWS::AccountId}"
      VersioningConfiguration:
        Status: !If [IsProd, Enabled, Suspended]
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  BucketName:
    Value: !Ref MyBucket
    Export:
      Name: !Sub "${AWS::StackName}-BucketName"
```

### Intrinsic Functions
- `!Ref` → resource physical ID
- `!GetAtt resource.Attribute` → resource attribute
- `!Sub "...${var}..."` → string substitution
- `!Join`, `!Select`, `!Split`, `!If`, `!Equals`, `!And`, `!Or`, `!Not`
- `!ImportValue` → from another stack's Outputs

### Stack Operations
```bash
aws cloudformation create-stack --stack-name my --template-body file://t.yaml
aws cloudformation update-stack --stack-name my --template-body file://t.yaml
aws cloudformation delete-stack --stack-name my
aws cloudformation describe-stack-events --stack-name my
aws cloudformation create-change-set ...
aws cloudformation execute-change-set ...
```

### Nested Stacks vs Cross-Stack References

**Nested**:
- Parent stack references child stacks via `AWS::CloudFormation::Stack`
- Tight lifecycle coupling

**Cross-Stack**:
- Outputs exported by one, imported by another
- `!ImportValue exportName`
- Loose lifecycle

### StackSets
Deploy to multiple accounts and regions:
- Org-level (across all accounts in OUs)
- Self-service or service-managed

### Drift Detection
Compare actual resources vs template. Identifies manual changes.

## CDK (Cloud Development Kit)

Define infra in real programming languages. Synthesizes to CloudFormation.

### Languages
TypeScript (most mature), Python, Java, .NET, Go.

### Concepts
- **App**: root construct
- **Stack**: deployable unit (translates to CloudFormation stack)
- **Construct**: building block (L1, L2, L3 abstraction levels)
- **L1 (Cfn*)**: 1:1 with CloudFormation
- **L2**: opinionated, common patterns
- **L3 (Patterns)**: complete architectures (e.g., ApplicationLoadBalancedFargateService)

### Example (TypeScript)
```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';

class MyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'MyBucket', {
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const fn = new lambda.Function(this, 'Fn', {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
    });

    bucket.grantRead(fn);  // automatic IAM
  }
}

const app = new cdk.App();
new MyStack(app, 'MyStack-prod', {env: {region: 'us-east-1'}});
```

### Commands
```bash
cdk init app --language typescript
cdk synth                # output CloudFormation
cdk diff                 # vs deployed
cdk deploy
cdk deploy --all
cdk destroy
cdk bootstrap            # one-time per account/region
```

### CDK vs CloudFormation vs Terraform

| | CloudFormation | CDK | Terraform |
|---|---|---|---|
| Language | YAML/JSON | TS/Python/Java | HCL |
| Multi-cloud | AWS only | AWS only (CDKTF for TF) | All clouds |
| State | AWS-managed | CloudFormation | Self-managed S3+DDB |
| Drift detection | Yes | Yes (via CFn) | Yes |
| Ecosystem | Basic | Growing | Massive |

Use CDK when: AWS-only + TypeScript/Python team.
Use Terraform when: multi-cloud or massive ecosystem of modules.
Use CloudFormation when: simple, AWS-only, no programming needed.

## SAM (Serverless Application Model)

CloudFormation superset for serverless:
- Shorthand for Lambda + API Gateway + DynamoDB + EventBridge etc.
- `AWS::Serverless::Function` resource
- `sam local` runs Lambda locally
- `sam deploy --guided` interactive deploy

```yaml
Transform: AWS::Serverless-2016-10-31

Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod

  HelloFn:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello/
      Handler: index.handler
      Runtime: nodejs20.x
      Events:
        ApiEvent:
          Type: Api
          Properties:
            RestApiId: !Ref MyApi
            Path: /hello
            Method: GET
```

Use SAM when: building primarily serverless apps, want AWS-native experience.

## Best Practices

- Version templates in Git
- Use Change Sets to preview
- One stack per logical unit (don't put everything in one stack)
- Cross-stack outputs/imports for shared resources
- Stack policies to protect critical resources from accidental delete
- `DeletionPolicy: Retain` on databases, buckets
- StackSets for multi-account rollouts
- Drift detection scheduled

## Interview Themes

- "Compare CloudFormation, CDK, Terraform"
- "When CDK over Terraform?"
- "Walk through a Change Set"
- "Stack vs StackSet"
- "How does drift detection work?"
