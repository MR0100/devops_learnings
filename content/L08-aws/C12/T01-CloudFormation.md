# L08/C12/T01 — CloudFormation (Templates, Stacks, StackSets)

## Learning Objectives

- Use CloudFormation
- Manage stacks

## CloudFormation

AWS-native IaC. Declarative YAML/JSON. Free.

## Template Anatomy

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: My stack

Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small]

Mappings:
  RegionMap:
    us-east-1: {AMI: ami-xxxx}

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: MyVPC

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: us-east-1a

Outputs:
  VpcId:
    Value: !Ref MyVPC
    Export:
      Name: my-vpc-id
```

## Sections

- Description
- Parameters (inputs)
- Mappings (lookups)
- Conditions
- Resources (required)
- Outputs (exports + console display)

## Intrinsic Functions

- `!Ref X`: reference parameter / resource (returns physical ID)
- `!GetAtt X.Attribute`: attribute of resource
- `!Sub "x-${VarName}"`: substitution
- `!Join [",", [a, b, c]]`: concat
- `!Split [",", "a,b,c"]`: split
- `!Select [0, [a, b]]`: pick element
- `!FindInMap [MapName, key1, key2]`: lookup
- `!If [Cond, True, False]`: conditional
- `!ImportValue x`: cross-stack reference

## Stacks

Deploy template → Stack:
```bash
aws cloudformation create-stack --stack-name myStack --template-body file://t.yaml --parameters ...
```

Stack tracks resources; can update / delete.

## Change Sets

Preview changes before apply:
```bash
aws cloudformation create-change-set --stack-name myStack --change-set-name myChange --template-body ...
aws cloudformation describe-change-set --change-set-name myChange --stack-name myStack
aws cloudformation execute-change-set --change-set-name myChange --stack-name myStack
```

Like Terraform plan.

## Drift Detection

Detect manual changes:
```bash
aws cloudformation detect-stack-drift --stack-name myStack
```

Reports resources changed outside CFN.

## Nested Stacks

Re-use templates as modules:
```yaml
Resources:
  NestedStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3/.../shared.yaml
      Parameters:
        ParamX: value
```

For: reuse infrastructure patterns.

## Cross-Stack References

Export from one stack; import in another:
```yaml
# Stack A
Outputs:
  VpcId:
    Value: !Ref MyVPC
    Export:
      Name: shared-vpc-id

# Stack B
Resources:
  MySG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue shared-vpc-id
```

Stack B blocked from deleting if A still references.

## StackSets

Deploy stacks across multiple accounts + regions:
```bash
aws cloudformation create-stack-set --stack-set-name baseline --template-body ...
aws cloudformation create-stack-instances --stack-set-name baseline --accounts 111 222 --regions us-east-1 us-west-2
```

For: org-wide baselines (IAM roles, log groups, etc.).

## Conditions

```yaml
Conditions:
  IsProd: !Equals [!Ref Env, prod]

Resources:
  ProdOnly:
    Type: AWS::S3::Bucket
    Condition: IsProd
    Properties: {...}
```

Resource created only if condition true.

## Custom Resources

Lambda-backed: custom logic in CFN:
```yaml
MyResource:
  Type: Custom::MyThing
  Properties:
    ServiceToken: arn:aws:lambda:...
    InputData: ...
```

Lambda invoked for Create/Update/Delete; reports back.

For: things CFN doesn't natively support.

## CDK vs CFN

CFN: YAML/JSON declarative.
CDK: TypeScript/Python/Java code → compiles to CFN.

CDK easier for complex logic; CFN simpler templates.

(Covered T02.)

## SAM

CloudFormation extension for serverless:
- Lambda
- API Gateway
- DynamoDB
- Step Functions

```yaml
Transform: AWS::Serverless-2016-10-31

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Runtime: python3.11
      Handler: app.handler
      Events:
        Api:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

Transforms to CFN at deploy.

## CLI vs Console

Console: quick test; visual; drift visible.
CLI: scripting; CI/CD.

For prod: CI/CD always.

## Rollback

On failure during update: auto-rollback to previous state.

Disable for debugging:
```bash
aws cloudformation update-stack --stack-name myStack --disable-rollback ...
```

Then manually fix.

## DeletionPolicy

Prevent accidental delete:
```yaml
Resources:
  MyDB:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Retain     # don't delete on stack delete
    UpdateReplacePolicy: Retain # don't delete if replaced
```

For databases, S3 with data.

## Conditional Resource

```yaml
Conditions:
  IsProd: !Equals [!Ref Env, prod]

Resources:
  BackupBucket:
    Condition: IsProd
    Type: AWS::S3::Bucket
```

## Parameter Constraints

```yaml
Parameters:
  CidrBlock:
    Type: String
    AllowedPattern: ^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$
    Description: VPC CIDR
```

Validate at parameter input.

## NoEcho

Mark sensitive params:
```yaml
Parameters:
  Password:
    Type: String
    NoEcho: true
```

Not displayed in console / API.

For passwords: SecretsManager preferred.

## SecretsManager Dynamic Reference

```yaml
DBPassword: '{{resolve:secretsmanager:my-secret:SecretString:password}}'
```

CFN resolves at deploy; not in template.

## Stack Limits

- 500 resources per stack
- 200 parameters
- 200 outputs
- 60 conditions

For larger: nested stacks.

## Cost

CloudFormation: free.
StackSets cross-region: small per-region fee.

## CFN vs Terraform

| | CFN | Terraform |
|---|---|---|
| Vendor | AWS | HashiCorp |
| Multi-cloud | No (AWS only) | Yes |
| State | Managed | Self-managed |
| Modules | Nested stacks | Modules |
| Drift | Detection built-in | terraform plan |
| Community | Smaller | Massive |

For AWS-only + AWS partnership: CFN.
For multi-cloud or larger community: Terraform.

## Drift Causes

- Manual console changes
- Other tools changing
- AWS-side modifications (rare)

Mitigate via SCP + good ops discipline.

## CodePipeline Integration

Common pattern:
1. Git push → CodePipeline
2. Source stage: Git
3. Build stage: CodeBuild (test)
4. Deploy stage: CFN deploy
5. Approve manual
6. Deploy prod

For multi-env: parameter per stage.

## Common Mistakes

- Manual changes (drift)
- No version control (template in S3 only)
- Hardcoded values (parameterize)
- Huge templates (split via nested)
- DeletionPolicy default (lose data)
- No tags

## Best Practices

- Templates in Git
- Change sets before update
- Drift detection scheduled
- Modular (nested stacks / SAM)
- Outputs documented
- DeletionPolicy on stateful
- Tag all resources

## Quick Refs

```bash
# Create
aws cloudformation create-stack --stack-name myStack --template-body file://t.yaml --parameters ...

# Update
aws cloudformation update-stack --stack-name myStack --template-body file://t.yaml

# Change set
aws cloudformation create-change-set --stack-name myStack --change-set-name x --template-body file://t.yaml

# Describe
aws cloudformation describe-stacks --stack-name myStack

# Delete
aws cloudformation delete-stack --stack-name myStack
```

## Interview Prep

**Mid**: "CFN basics."

**Senior**: "Cross-stack reference vs nested."

**Staff**: "Multi-account IaC strategy."

## Next Topic

→ [T02 — CDK (TypeScript, Python)](T02-CDK.md)
