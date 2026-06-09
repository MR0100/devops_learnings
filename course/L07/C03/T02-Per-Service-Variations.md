# L07/C03/T02 — Per-Service Variations

## Learning Objectives

- Reason about responsibility per service
- Pick services with right control level

## Variations Across Services

Not all "cloud" is the same. Compute services have different shared responsibility splits.

## IaaS (EC2, GCE, Azure VM)

- Provider: physical hardware, hypervisor, network, hardware refresh
- You: OS patching, app, firewall, monitoring agent, backups (snapshot frequency)

Maximum control; maximum work.

## Container Orchestration

### EKS / GKE / AKS (Managed K8s)
- Provider: control plane (etcd, scheduler, controllers)
- You: nodes (you can use managed node groups, but you still patch the AMI), workloads, RBAC, networking, secrets, ingress

### Fargate / Cloud Run (Serverless Containers)
- Provider: everything except your container
- You: container image, env config, IAM, networking

### ECS on EC2
- Provider: ECS API
- You: nodes, agent, OS, image, networking

## Managed Databases

### RDS
- Provider: OS, engine, patches, HA failover, automated backups
- You: schema, queries, encryption choice, network access, backup retention
- Optional: read replicas (you set up)

### DynamoDB
- Provider: everything operational
- You: data model, capacity (or on-demand), backups (on/off), encryption keys

### ElastiCache
- Provider: Redis/Memcached process, OS, HA
- You: data structure, eviction policy, networking, encryption

## Storage

### S3
- Provider: durability (11 9s), HA, replication within region
- You: bucket policy, IAM, encryption (default SSE-S3 on by default but choose KMS for stronger), versioning, replication

### EBS
- Provider: storage hardware, snapshots availability
- You: volume creation, attachment, encryption, snapshot frequency, snapshot retention

### EFS
- Provider: scalability, HA across AZs
- You: mount targets, IAM, performance mode

## Network

### VPC
- Provider: virtual network infrastructure
- You: CIDR, subnets, route tables, security groups, NACLs

### ALB / NLB
- Provider: load balancer infrastructure
- You: target groups, listeners, certs, health checks

### Route53
- Provider: DNS authoritative service
- You: zones, records, health checks, failover policies

## Serverless

### Lambda
- Provider: runtime, OS, scaling
- You: function code, env vars, IAM, secrets, VPC config (optional), error handling

### API Gateway
- Provider: gateway infrastructure
- You: route configs, integrations, auth, throttle, caching

### Step Functions
- Provider: orchestration engine
- You: state machine definition, IAM, error handling

## Higher-Level Services

### Cognito (Auth)
- Provider: user pool storage, password hashing, MFA, OAuth flows
- You: user pool config, attribute schema, app integration, trigger lambdas

### SES (Email)
- Provider: SMTP, deliverability
- You: domain verification, templates, reputation

### Kinesis / MSK
- Provider: cluster (MSK: brokers; Kinesis: complete service)
- MSK: you manage topics, schema, security
- Kinesis: AWS manages more (Stream is fully managed)

## AI / ML Services

### SageMaker
- Provider: training infrastructure, notebook instances
- You: data, model, hyperparams, endpoints

### Bedrock
- Provider: model serving
- You: prompts, fine-tuning data (optional), guardrails

## Why It Matters

When choosing service, ask:
1. **Control needed**: must I patch the OS? Use my own DB version?
2. **Operational burden**: who's oncall for the DB?
3. **Cost**: more managed = pay for the management
4. **Vendor lock**: managed often = proprietary

## Trade-off Spectrum

```
More control          ← →          Less work
EC2 → ECS on EC2 → EKS → Fargate → Lambda → SaaS
```

Pick farthest right that meets your needs.

## Multi-Service Apps

A typical app uses many:
- ALB (managed)
- Fargate (managed compute)
- RDS (managed DB)
- ElastiCache (managed cache)
- S3 (managed storage)
- SQS (managed queue)
- Cognito (managed auth)
- Lambda (event processing)

Customer: configs, code, security. Provider: operations.

## Vendor Lock Per Service

- IaaS: low (VMs portable)
- CaaS: medium (K8s helps)
- PaaS: high (app uses platform APIs)
- FaaS: highest (functions use cloud events)

## Compliance Per Service

Not all services in scope for every cert. Check:
- AWS Artifact: per-cert service scope
- Azure compliance docs
- GCP compliance docs

For HIPAA, FedRAMP, PCI: stick to in-scope services.

## SLAs Per Service

| Service | SLA |
|---|---|
| EC2 single instance | None |
| EC2 multi-AZ | 99.99% |
| RDS single-AZ | 99.95% |
| RDS Multi-AZ | 99.99% |
| S3 | 99.9% availability; 11 9s durability |
| DynamoDB | 99.99% standard; 99.999% Global Tables |
| Lambda | 99.95% |
| Route53 | 100% |
| CloudFront | 99.9% |

100% means: you get credit if anything missed. Doesn't mean 0 outages.

## Decision Framework

For each component:
1. Build vs buy? (DB: buy. Auth: probably buy. Custom: build.)
2. Managed vs self-host? (Almost always managed in cloud.)
3. Cloud-native (Lambda) vs portable (containers)?
4. Cost / control trade?

## Anti-Pattern: Mixed Stack

App on Lambda + DynamoDB + S3 = highly cloud-native; not portable. Often correct.

App on EC2 + self-hosted Postgres + minio = portable; lots of work. Sometimes correct.

Don't half-do: portable architecture using one cloud's proprietary services = worst of both.

## Interview Prep

**Mid**: "RDS responsibility split."

**Senior**: "When use managed vs self-host."

**Staff**: "Compliance-bounded service selection."

## Next Topic

→ Move to [L07/C04 — Compute Family](../C04/README.md)
