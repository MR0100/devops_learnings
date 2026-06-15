# L17/C06/T02 — Semantic Conventions

## Learning Objectives

- Use standard attributes
- Make telemetry portable

## Why

Without conventions:
- One app: `http_status`
- Another: `status_code`
- Another: `response.code`

Hard to query / aggregate.

With:
- Standard names
- Standard formats
- Portable across tools

## OTel Spec

```
service.name
service.version
service.namespace
deployment.environment

http.request.method
http.response.status_code
url.full
url.path
server.address

db.system  (postgresql, mysql, etc.)
db.statement
db.user

messaging.system
messaging.destination

rpc.system
rpc.method
```

## Categories

### Resource
What's emitting:
- service.name
- service.version
- host.name
- container.id
- k8s.pod.name
- k8s.namespace.name

### Span
About the operation:
- http.*
- db.*
- rpc.*
- messaging.*

## HTTP Conventions

Span attributes (stable HTTP semconv, v1.23+):
```
http.request.method = "GET"
url.full = "https://api.example.com/users/123"
http.response.status_code = 200
user_agent.original = "..."
```

> **Migration note:** the older attributes `http.method`, `http.url`,
> `http.status_code`, `http.target`, and `http.host` were **deprecated**
> when the HTTP semantic conventions reached Stable. Use
> `http.request.method`, `url.full`, `http.response.status_code`,
> `url.path` + `url.query`, and `server.address` + `server.port`
> respectively. Old SDKs/backends may still emit the legacy names — set
> `OTEL_SEMCONV_STABILITY_OPT_IN=http` to emit the stable set during a
> dual-emit migration.

Span name: HTTP method + low-cardinality route.

```
"GET /users/{id}"
NOT "GET /users/123"
```

## DB

```
db.system = "postgresql"
db.connection_string = ...
db.user = "app"
db.name = "myapp_prod"
db.statement = "SELECT * FROM users WHERE id = $1"
db.operation = "SELECT"
```

## Messaging

```
messaging.system = "kafka"
messaging.destination = "events"
messaging.operation = "publish"
messaging.message_id = ...
```

## RPC

```
rpc.system = "grpc"
rpc.service = "MyService"
rpc.method = "GetUser"
```

## Cloud

```
cloud.provider = "aws"
cloud.region = "us-east-1"
cloud.availability_zone = "us-east-1a"
cloud.account.id = "..."

aws.ecs.task.arn = ...
aws.lambda.invoked_arn = ...
```

## K8s

```
k8s.pod.name = "myapp-abc"
k8s.namespace.name = "prod"
k8s.deployment.name = "myapp"
k8s.node.name = "node1"
k8s.cluster.name = "us-east-1"
```

## Process

```
process.pid
process.runtime.name = "python"
process.runtime.version = "3.12"
```

## Custom

Org-specific:
```
custom.tenant_id = "..."
custom.feature_flag = "..."
```

Use namespace prefix.

## Resource Detection

OTel SDKs auto-detect:
- Cloud (AWS metadata, GCP metadata)
- K8s (pod info via env vars)
- Container

```yaml
processors:
  resourcedetection:
    detectors: [aws_ec2, gcp, k8s, system]
```

## Naming

- Lowercase
- Dot-separated
- Plural where applicable
- Avoid trailing modifiers (use child attribute)

```
db.system   GOOD
dbSystem    BAD
DB_SYSTEM   BAD
```

## Standard Span Names

HTTP server: `GET /users/{id}`
HTTP client: `GET`
DB: `SELECT users`
RPC: `MyService/GetUser`

## Status Codes

```
SpanStatus:
  OK
  ERROR
  UNSET
```

Don't set OK explicitly.

## Errors

```
Status: ERROR
exception.type = "ConnectionError"
exception.message = "..."
exception.stacktrace = "..."
```

## Span Kind

```
SERVER (inbound HTTP/RPC)
CLIENT (outbound)
PRODUCER (queue produce)
CONSUMER (queue consume)
INTERNAL (no I/O)
```

## Metrics Conventions

```
http.server.request.duration   (seconds, histogram)
http.server.request.body.size  (bytes, histogram)
http.server.response.body.size (bytes, histogram)

db.client.connections.usage    (connections, updown_counter)
```

## SemConv Stability

- Stable
- Experimental

Track changes. Update SDKs.

## Why Important

Querying:
```
{ service.name = "api", http.response.status_code = "500" }
```

Standard names → backend understands.

Vendors map their UI to conventions.

## Migration Tip

```yaml
processors:
  attributes:
    actions:
      - key: my-custom-attr
        action: extract
        pattern: ^(?P<service_name>[^.]+)\..*
        from_attribute: service.name
```

Rename existing attrs to standard.

## Best Practices

- Use semantic conventions everywhere
- Resource attrs at service init
- Standard span names
- Status: only ERROR for errors
- Span kind correct
- Stable conventions in prod

## Common Mistakes

- Custom names overriding standards
- Trailing IDs in span name (high cardinality)
- Missing resource attrs
- Wrong span kind
- Plaintext PII in attrs

## Span Name Cardinality

High cardinality span names:
```
"GET /users/123"
"GET /users/456"
```

Bad: explodes index.

Use:
```
"GET /users/{id}"
```

Route templated.

## Custom Conventions

For:
- Tenant IDs
- Feature flags
- Custom metadata

Prefix with org namespace:
```
mycompany.tenant_id
mycompany.feature_flag.checkout_redesign
```

## Quick Refs

```
service.name
service.version
deployment.environment

http.request.method / http.response.status_code / url.full
db.system / .statement
rpc.system / .method
messaging.system / .destination

cloud.provider / .region
k8s.pod.name / .namespace.name
```

## Interview Prep

**Mid**: "What's semantic conventions."

**Senior**: "Portability via convention."

**Staff**: "OTel adoption."

## Next Topic

→ [T03 — Auto-Instrumentation](T03-Auto-Instrumentation.md)
