# L08/C07/T03 — Lambda Layers, Extensions

## Learning Objectives

- Use Layers for shared code
- Use Extensions for observability

## Layers

Reusable .zip packages mounted at /opt in Lambda. Common deps shared across functions.

```bash
mkdir -p python/lib/python3.11/site-packages
pip install requests -t python/lib/python3.11/site-packages/
zip -r layer.zip python

aws lambda publish-layer-version \
  --layer-name my-libs \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.11
```

Attach to function:
```bash
aws lambda update-function-configuration \
  --function-name myFn \
  --layers arn:aws:lambda:us-east-1:123:layer:my-libs:1
```

Up to 5 layers per function.

## When Layers

- Heavy deps (pandas, numpy) shared across functions
- Custom shared code
- Third-party utilities (Lambda Powertools)
- Reduce function .zip size (deployment faster)

## When NOT Layers

- Function-specific code
- Versioning complexity not worth it
- Container images: layers not needed (everything in image)

## Layer Permissions

Layers are per-account / shared:
```bash
aws lambda add-layer-version-permission \
  --layer-name my-libs \
  --version-number 1 \
  --statement-id share \
  --principal "*" \
  --action lambda:GetLayerVersion
```

## AWS-Provided Layers

- Lambda Powertools (Python, Node, Java)
- Datadog, New Relic, others (vendor extensions)

## Layer Version

Immutable. New version → new ARN:
- arn:...:layer:my-libs:1
- arn:...:layer:my-libs:2

Functions reference specific version.

## Extensions

Lambda Extensions API: external processes (e.g., observability agents) running alongside function.

Lifecycle:
- Init (with function init)
- Invoke (per invocation)
- Shutdown (when instance ends)

## Use Cases

- Observability (Datadog, NewRelic, Honeycomb)
- Secrets pre-fetch
- Configuration cache
- Custom log routers

## Build

External process; communicates via /opt/extensions/<name>:
```bash
#!/bin/bash
while true; do
  # poll extension API
  curl http://$AWS_LAMBDA_RUNTIME_API/2020-01-01/extension/event/next
done
```

Most use SDK / template.

## Internal Extensions

Run in function process (not separate). Shorter spinup; bound to runtime.

## Cost

Extension runs in Lambda execution time → adds to your bill.

For observability agents: ~10-30ms init overhead.

## Lambda Powertools

Library (not strictly a layer, but commonly used as one):
- Structured logging
- Metrics (EMF format)
- Tracing (X-Ray)
- Idempotency wrapper
- Validation
- Parameters helper
- Feature flags

```python
from aws_lambda_powertools import Logger, Metrics, Tracer

logger = Logger()
metrics = Metrics()
tracer = Tracer()

@logger.inject_lambda_context
@metrics.log_metrics
@tracer.capture_lambda_handler
def handler(event, context):
    logger.info("handling event", extra={"event_type": event["type"]})
    metrics.add_metric(name="custom", unit="Count", value=1)
    with tracer.capture_method(name="process"):
        return process(event)
```

For production Python Lambda: Powertools mandatory.

## Common Patterns

### Lambda + Layer + Extension
- Layer: code deps
- Extension: monitoring agent
- Function: business logic

### Shared Lambda Powertools
One layer in account; all functions reference.

### Vendor Observability
Datadog extension: auto-instruments; sends metrics directly (skip CloudWatch ingestion cost).

## Layer Naming

Convention:
- `<purpose>-<runtime>`: my-libs-py311
- `<vendor>`: datadog-lambda

ARN includes account + version; tracked per function.

## Updating Layer

New version → update function config:
```bash
aws lambda update-function-configuration \
  --function-name myFn \
  --layers arn:aws:lambda:us-east-1:123:layer:my-libs:2
```

Each function manually updates (no auto-track latest).

## Layer Limits

- 5 layers per function
- 250 MB total unzipped (function + layers)
- Layer .zip: 50 MB

## Lambda Insights

AWS-provided extension for enhanced metrics:
- CPU
- Memory
- Network
- Disk
- Per-invocation

Cost: extra (~$1/M invocations).

## Cleaning Old Versions

Layers accumulate; old versions still billed (storage):
```bash
aws lambda delete-layer-version --layer-name my-libs --version-number 1
```

Lifecycle: keep last N; delete older.

## Container vs Layers

Container image:
- Everything bundled
- Up to 10 GB
- No layers needed (Dockerfile RUNs)
- ECR pull cost / startup

Layers:
- For ZIP-based functions
- Easier to share deps
- Smaller individual function ZIPs

For complex: container.
For shared deps: layers.

## Best Practices

- Layers for shared deps; not function-specific
- Version layers properly
- Extensions for vendor observability
- Lambda Powertools for Python
- Avoid 5-layer max (consolidate)
- Document layer purpose

## Common Mistakes

- Layer with single function's code (defeats purpose)
- No version pinning in function
- Heavy extensions (slows cold start)
- Layer for tiny libs (overhead > benefit)

## Quick Refs

```bash
# Publish layer
aws lambda publish-layer-version --layer-name my-libs --zip-file fileb://layer.zip --compatible-runtimes python3.11

# Attach
aws lambda update-function-configuration --function-name myFn --layers arn:...

# List
aws lambda list-layers
aws lambda list-layer-versions --layer-name my-libs
```

## Interview Prep

**Mid**: "When use Layers."

**Senior**: "Lambda observability options."

**Staff**: "Manage 100 functions sharing libs."

## Next Topic

→ [T04 — Cold Starts & Mitigations](T04-Cold-Starts.md)
