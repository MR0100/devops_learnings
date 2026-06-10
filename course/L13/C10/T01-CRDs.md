# L13/C10/T01 — Custom Resource Definitions (CRDs)

## Learning Objectives

- Extend K8s API with CRDs
- Apply OpenAPI schema validation

## CRD

Custom Resource Definition. Extends K8s API with new types.

K8s built-in: Pod, Service, Deployment, ...
CRD adds: WebService, MongoCluster, RedisInstance, anything.

## Why CRDs

- Domain-specific abstractions
- Operator pattern foundation
- Declarative APIs for tools
- Self-service infrastructure

## Anatomy

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: webservices.apps.mycompany.io
spec:
  group: apps.mycompany.io
  names:
    plural: webservices
    singular: webservice
    kind: WebService
    shortNames: [ws]
  scope: Namespaced       # or Cluster
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: [image, replicas]
            properties:
              image:
                type: string
              replicas:
                type: integer
                minimum: 1
                maximum: 100
          status:
            type: object
            properties:
              availableReplicas:
                type: integer
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.availableReplicas
```

## Use Custom Resource

After CRD installed:
```yaml
apiVersion: apps.mycompany.io/v1
kind: WebService
metadata:
  name: my-app
spec:
  image: nginx:1.27
  replicas: 3
```

kubectl works:
```bash
kubectl get webservices
kubectl get ws
kubectl describe webservice my-app
```

## OpenAPI Validation

Schema validates spec at apply time:
```yaml
schema:
  openAPIV3Schema:
    type: object
    required: [spec]
    properties:
      spec:
        type: object
        required: [image]
        properties:
          image:
            type: string
            pattern: '^[a-z0-9./-]+(:[a-z0-9.-]+)?$'
          replicas:
            type: integer
            minimum: 1
            default: 1
          environment:
            type: string
            enum: [dev, staging, prod]
```

Reject invalid:
```bash
kubectl apply -f bad.yaml
# Error: WebService.apps.mycompany.io "x" is invalid:
#   spec.image: Required value
```

## Versioning

CRD can have multiple versions:
```yaml
versions:
- name: v1
  served: true
  storage: true
  schema: ...
- name: v2
  served: true
  storage: false
  schema: ...
```

`served`: served by API server.
`storage`: which version stored in etcd. Only one storage=true.

## Conversion Webhooks

For schema changes between versions:
```yaml
conversion:
  strategy: Webhook
  webhook:
    clientConfig:
      service:
        name: my-conversion-webhook
        namespace: default
        path: /convert
    conversionReviewVersions: [v1]
```

Webhook converts between versions on demand.

For breaking changes: required.

## Status Subresource

```yaml
subresources:
  status: {}
```

Enables `/status` subresource:
- Update via `PUT /apis/.../webservices/x/status`
- Operator updates Status; doesn't trigger spec change events

Best practice for controllers.

## Scale Subresource

```yaml
subresources:
  scale:
    specReplicasPath: .spec.replicas
    statusReplicasPath: .status.availableReplicas
    labelSelectorPath: .status.labelSelector
```

Enables `kubectl scale`:
```bash
kubectl scale webservice/my-app --replicas=5
```

And HPA:
```yaml
spec:
  scaleTargetRef:
    apiVersion: apps.mycompany.io/v1
    kind: WebService
    name: my-app
```

For controller-managed workloads.

## Printer Columns

For `kubectl get`:
```yaml
additionalPrinterColumns:
- name: Image
  type: string
  jsonPath: .spec.image
- name: Replicas
  type: integer
  jsonPath: .spec.replicas
- name: Available
  type: integer
  jsonPath: .status.availableReplicas
- name: Age
  type: date
  jsonPath: .metadata.creationTimestamp
```

```bash
kubectl get webservice
# NAME    IMAGE        REPLICAS   AVAILABLE   AGE
# my-app  nginx:1.27   3          3           1d
```

## Categories

Group resources:
```yaml
categories: [all, apps]
```

`kubectl get all` includes WebServices.

## Default Values

```yaml
properties:
  replicas:
    type: integer
    default: 1
```

If not specified: defaulted on apply.

## Required Fields

```yaml
required: [image]
```

Apply without image: rejected.

## Validation Rules (CEL)

Beyond schema:
```yaml
x-kubernetes-validations:
- rule: "self.replicas <= 100"
  message: "Replicas must be <= 100"
```

CEL expressions; logical constraints across fields.

## OpenAPI Patterns

```yaml
properties:
  ip:
    type: string
    format: ipv4
  port:
    type: integer
    minimum: 1
    maximum: 65535
  email:
    type: string
    format: email
```

Built-in formats.

## Map Type

```yaml
labels:
  type: object
  additionalProperties:
    type: string
```

Arbitrary key-value map.

## Array Type

```yaml
hostnames:
  type: array
  items:
    type: string
  minItems: 1
  maxItems: 100
```

## Nested Object

```yaml
database:
  type: object
  required: [host, port]
  properties:
    host:
      type: string
    port:
      type: integer
    credentials:
      type: object
      properties:
        secretRef:
          type: string
```

## Server-Side Apply

CRDs support server-side apply (3-way merge based on field ownership).

For controllers: avoid conflicting with users editing same field.

## Conversion Strategy

- None: only one version
- Webhook: custom conversion logic

For multi-version CRDs.

## Install CRD

```bash
kubectl apply -f crd.yaml
```

Cluster-scoped resource. All namespaces see it.

## Install Operator (CRD + Controller)

```bash
# CRD
kubectl apply -f crd.yaml
# RBAC
kubectl apply -f rbac.yaml
# Controller Deployment
kubectl apply -f controller.yaml
```

Or via Helm chart.

## Delete CRD

```bash
kubectl delete crd webservices.apps.mycompany.io
```

Deletes ALL custom resources of this type.

DANGEROUS in production.

## Finalizers

Block delete until finalizer removed:
```yaml
metadata:
  finalizers:
  - mycompany.io/cleanup
```

Controller:
1. Sees DeletionTimestamp + finalizer
2. Cleans up external resources
3. Removes finalizer
4. K8s actually deletes

For: ensure cleanup before deletion.

## Status vs Spec

- Spec: user's desired state
- Status: observed state by controller

```yaml
status:
  type: object
  properties:
    phase:
      type: string
      enum: [Pending, Ready, Failed]
    conditions:
      type: array
      items: ...
```

Conditions: standard pattern (Ready, Progressing, etc.).

## kubebuilder for CRD Generation

Generates CRD YAML from Go types:
```go
// +kubebuilder:validation:Required
// +kubebuilder:validation:Minimum=1
Replicas int32 `json:"replicas"`
```

Avoid hand-writing CRD YAML.

## OperatorHub

CRDs + Operators distributed via OperatorHub.io.

For: install community operators.

## Best Practices

- OpenAPI schema strict
- Status subresource
- Printer columns for kubectl
- Defaults for optional
- Required for must-have
- Validation rules (CEL)
- Conversion webhook for breaking
- Finalizers for cleanup

## Common Mistakes

- No schema (anything accepted)
- No status (controller can't report)
- No printer columns (kubectl unhelpful)
- Loose types (string when enum)
- No required fields

## Performance

CRDs in etcd. Many CRs:
- Like any K8s resource
- Watch by controllers
- API Server caches

For huge numbers: scale etcd.

## Schema Migration

Adding optional field: safe.
Renaming: breaking.
Removing required: breaking.

For breaking: new version + conversion webhook.

## Inspection

```bash
kubectl get crd
kubectl describe crd webservices.apps.mycompany.io
kubectl explain webservice.spec
kubectl explain webservice.spec.replicas
```

`kubectl explain` works on CRDs with schema.

## Quick Refs

```bash
# Install
kubectl apply -f crd.yaml

# List
kubectl get crd

# Use CR
kubectl apply -f my-cr.yaml
kubectl get webservices
kubectl describe webservice my-app

# Edit
kubectl edit webservice my-app
```

## Interview Prep

**Junior**: "What's a CRD."

**Mid**: "Spec vs Status."

**Senior**: "CRD versioning."

**Staff**: "Design CRD for X domain."

## Next Topic

→ [T02 — Controller Pattern](T02-Controller-Pattern.md)
