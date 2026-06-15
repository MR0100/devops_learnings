# L06/C02/T05 — Boto3 for AWS, the Kubernetes Python Client

## Learning Objectives

- Use boto3 fluently
- Use kubernetes-client for K8s

## Boto3

AWS SDK for Python.

```bash
pip install boto3
```

### Basic
```python
import boto3

s3 = boto3.client("s3")
ec2 = boto3.resource("ec2")
```

`client`: low-level; mirrors API directly.
`resource`: higher-level OO.

### Credentials Discovery
boto3 finds credentials from (in order):
1. `aws_access_key_id` argument
2. Environment vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
3. Shared credentials file: `~/.aws/credentials`
4. Profile via `AWS_PROFILE` env or `Session(profile_name=)`
5. EC2 instance profile / ECS task role / Lambda role
6. SSO

Best practice: instance profiles / IAM roles, not static keys.

### S3 Operations
```python
s3 = boto3.client("s3")

# Upload
s3.upload_file("local.txt", "my-bucket", "remote.txt")

# Download
s3.download_file("my-bucket", "remote.txt", "local.txt")

# List
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket", Prefix="logs/"):
    for obj in page.get("Contents", []):
        print(obj["Key"], obj["Size"])

# Generate presigned URL
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": "file.txt"},
    ExpiresIn=3600,
)
```

### EC2
```python
ec2 = boto3.resource("ec2")
for i in ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]):
    print(i.id, i.instance_type, i.private_ip_address)

# Tag
i.create_tags(Tags=[{"Key": "Owner", "Value": "alice"}])
```

### DynamoDB
```python
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("users")

# Put
table.put_item(Item={"id": "1", "name": "alice"})

# Get
resp = table.get_item(Key={"id": "1"})
item = resp.get("Item")

# Query
resp = table.query(
    KeyConditionExpression=Key("user_id").eq("42"),
)
```

### Pagination
Most list APIs return paginated. Use paginators:
```python
paginator = client.get_paginator("describe_instances")
for page in paginator.paginate():
    for r in page["Reservations"]:
        for i in r["Instances"]:
            print(i["InstanceId"])
```

### AssumeRole
```python
sts = boto3.client("sts")
creds = sts.assume_role(RoleArn="arn:aws:iam::123:role/X", RoleSessionName="me")["Credentials"]

session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)
s3 = session.client("s3")
```

### Error Handling
```python
from botocore.exceptions import ClientError

try:
    s3.head_object(Bucket="b", Key="k")
except ClientError as e:
    if e.response["Error"]["Code"] == "404":
        # object doesn't exist
    else:
        raise
```

## Kubernetes Python Client

```bash
pip install kubernetes
```

### Setup
```python
from kubernetes import client, config

# Load kubeconfig (local dev)
config.load_kube_config()

# Inside a pod
config.load_incluster_config()

v1 = client.CoreV1Api()
apps = client.AppsV1Api()
```

### List Pods
```python
pods = v1.list_pod_for_all_namespaces()
for p in pods.items:
    print(p.metadata.namespace, p.metadata.name, p.status.phase)
```

### Get Specific
```python
pod = v1.read_namespaced_pod("my-pod", "default")
```

### Create Deployment
```python
from kubernetes.client import V1Deployment, V1ObjectMeta, V1DeploymentSpec, ...

deployment = V1Deployment(
    metadata=V1ObjectMeta(name="myapp"),
    spec=V1DeploymentSpec(
        replicas=3,
        selector={"matchLabels": {"app": "myapp"}},
        template=V1PodTemplateSpec(...)
    ),
)
apps.create_namespaced_deployment("default", deployment)
```

### Watch (Streaming)
```python
from kubernetes.watch import Watch

w = Watch()
for event in w.stream(v1.list_pod_for_all_namespaces):
    print(event["type"], event["object"].metadata.name)
```

### Apply YAML
```python
from kubernetes import utils

utils.create_from_yaml(client.ApiClient(), "deploy.yaml")
```

## Async Boto3

For high-throughput AWS work: aioboto3 (community async wrapper).

```python
import aioboto3

async with aioboto3.Session().resource("s3") as s3:
    bucket = await s3.Bucket("my-bucket")
```

## Common Patterns

### List Then Filter
```python
running = [i for i in ec2.instances.all() if i.state["Name"] == "running"]
```

### Bulk Tag
```python
ids = [i.id for i in ec2.instances.all()]
ec2_client.create_tags(Resources=ids, Tags=[{"Key": "Env", "Value": "prod"}])
```

### Stream Logs
```python
logs = boto3.client("logs")
events = logs.filter_log_events(
    logGroupName="/aws/lambda/myfunc",
    startTime=int((datetime.now() - timedelta(hours=1)).timestamp() * 1000),
)
```

## Common Mistakes

- Listing resources without a paginator, so you silently only see the first ~1000 items (`list_objects_v2`, `describe_instances`, etc.).
- Hardcoding static access keys instead of using IAM roles / instance or pod identity (IRSA) — keys leak and never rotate.
- Catching nothing: every AWS call can raise `botocore.exceptions.ClientError`; inspect `e.response["Error"]["Code"]` and handle it.
- Creating a fresh `boto3.client(...)` on every call instead of reusing one — wastes connections and re-resolves credentials each time.
- Calling `config.load_kube_config()` inside a pod; use `config.load_incluster_config()` there and fall back to kubeconfig locally.
- Ignoring `409 Conflict` on Kubernetes updates instead of re-reading the object and retrying on the latest resourceVersion.

## Best Practices

- Use IAM roles, not static keys
- Set timeouts:
```python
boto3.client("s3", config=Config(connect_timeout=5, read_timeout=10))
```
- Retry config:
```python
Config(retries={"max_attempts": 5, "mode": "adaptive"})
```
- Pagination always
- Catch ClientError

## Quick Refs

```python
# boto3 — paginate, retry, timeout, error handling
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

cfg = Config(retries={"max_attempts": 5, "mode": "adaptive"},
             connect_timeout=5, read_timeout=10)
s3 = boto3.client("s3", config=cfg)

paginator = s3.get_paginator("list_objects_v2")
keys = [obj["Key"]
        for page in paginator.paginate(Bucket="my-bucket", Prefix="logs/")
        for obj in page.get("Contents", [])]

try:
    s3.head_object(Bucket="my-bucket", Key="missing")
except ClientError as e:
    if e.response["Error"]["Code"] == "404":
        ...  # handle not-found
    else:
        raise
```

```python
# Assume role
sts = boto3.client("sts")
creds = sts.assume_role(RoleArn="arn:aws:iam::123:role/Deploy",
                        RoleSessionName="tool")["Credentials"]
session = boto3.Session(aws_access_key_id=creds["AccessKeyId"],
                        aws_secret_access_key=creds["SecretAccessKey"],
                        aws_session_token=creds["SessionToken"])
```

```python
# Kubernetes python client — in-cluster vs local
from kubernetes import client, config
try:
    config.load_incluster_config()      # inside a pod (uses ServiceAccount)
except config.ConfigException:
    config.load_kube_config()           # local dev (~/.kube/config)
v1 = client.CoreV1Api()
pods = v1.list_namespaced_pod("default", label_selector="app=web").items
```

## Interview Prep

**Mid**: "boto3 paginators — why?"

**Senior**: "Assume role from Python."

**Staff**: "K8s operator scaffolding (Python or Go)?"

## Next Topic

→ [T06 — Writing CLIs with Click / Typer](T06-Click-Typer.md)
