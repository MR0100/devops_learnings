# L08 — AWS Deep Dive

## Overview

AWS is the dominant cloud (35%+ market share, 2025). For FAANGM interviews — especially Amazon — deep AWS knowledge is non-negotiable. This lecture covers 50+ services across 14 chapters.

**14 chapters, 75 topics. Expect ~80 hours.**

## Learning Outcomes

- Design VPCs that scale to thousands of services
- Master IAM (the source of most cloud security incidents)
- Operate EC2, EKS, Lambda, RDS, DynamoDB at production scale
- Use CloudFormation/CDK/Terraform fluently
- Apply the AWS Well-Architected Framework

## Chapter Map

### [C01](C01/) — Account Setup & Organizations
- T01 Root Account, MFA, Billing Alarms
- T02 AWS Organizations, SCPs, OUs
- T03 Control Tower & Landing Zones

### [C02](C02/) — IAM Mastery
- T01 Users, Groups, Roles, Policies
- T02 Trust Policies vs Permission Policies
- T03 Resource-Based Policies
- T04 Conditions, IAM Access Analyzer
- T05 IAM Roles for Service Accounts (IRSA)
- T06 Permission Boundaries & SCPs
- T07 Assume Role, STS, External ID

### [C03](C03/) — EC2 & Compute
- T01 Instance Types & Families
- T02 AMIs, Launch Templates, Auto Scaling Groups
- T03 Placement Groups (Cluster, Spread, Partition)
- T04 EBS Types (gp3, io2, st1, sc1) and Performance
- T05 Spot, Savings Plans, Reserved Instances
- T06 Nitro System Architecture
- T07 EC2 Metadata Service (IMDSv1 vs IMDSv2)

### [C04](C04/) — VPC & Networking
- T01 VPC Architecture (CIDR, Subnets, AZs)
- T02 Internet Gateway, NAT Gateway, NAT Instance
- T03 Route Tables, Network ACLs, Security Groups
- T04 VPC Peering vs Transit Gateway
- T05 PrivateLink & VPC Endpoints (Interface, Gateway)
- T06 Direct Connect & Site-to-Site VPN
- T07 Egress Controls & Centralized Egress
- T08 Elastic Load Balancing (ALB, NLB, GWLB)

### [C05](C05/) — S3 Deep Dive
- T01 Buckets, Objects, Keys, Prefixes
- T02 Storage Classes & Lifecycle Policies
- T03 Versioning, Object Lock, MFA Delete
- T04 S3 Performance & Request Patterns
- T05 S3 Security (Block Public Access, Bucket Policies, KMS)
- T06 Multipart Upload, Transfer Acceleration
- T07 S3 Event Notifications & Triggers
- T08 EFS & FSx (File Storage)

### [C06](C06/) — Databases on AWS
- T01 RDS (MySQL, PostgreSQL, Oracle, SQL Server)
- T02 Aurora Architecture (Storage Layer, Global DB)
- T03 DynamoDB Deep Dive (Partition Keys, GSI, LSI)
- T04 DynamoDB Streams & Single-Table Design
- T05 ElastiCache (Redis & Memcached)
- T06 Redshift, Athena, Glue

### [C07](C07/) — Serverless on AWS
- T01 Lambda Architecture & Execution Model
- T02 Concurrency, Reserved & Provisioned Concurrency
- T03 Lambda Layers, Extensions
- T04 Cold Starts & Mitigations
- T05 Step Functions (Standard vs Express)
- T06 EventBridge, SQS, SNS
- T07 API Gateway (REST, HTTP, WebSocket)

### [C08](C08/) — Container Services
- T01 ECS (EC2 vs Fargate)
- T02 EKS Architecture & Control Plane
- T03 Fargate Pricing & Limits
- T04 ECR (Image Scanning, Replication)
- T05 App Mesh

### [C09](C09/) — Edge Services
- T01 CloudFront (Distributions, Behaviors, Functions, Lambda@Edge)
- T02 Route 53 (Routing Policies)
- T03 Global Accelerator
- T04 WAF & Shield

### [C10](C10/) — Messaging & Streaming
- T01 SQS (Standard, FIFO, DLQ)
- T02 SNS & Fanout Patterns
- T03 EventBridge (Buses, Rules, Schemas)
- T04 Kinesis Data Streams, Firehose, Analytics
- T05 MSK (Managed Kafka)

### [C11](C11/) — Observability on AWS
- T01 CloudWatch Metrics, Logs, Alarms
- T02 CloudWatch Insights & Contributor Insights
- T03 X-Ray Tracing
- T04 Managed Prometheus & Grafana
- T05 CloudTrail for Audit

### [C12](C12/) — IaC on AWS
- T01 CloudFormation (Templates, Stacks, StackSets)
- T02 CDK (TypeScript, Python)
- T03 SAM for Serverless

### [C13](C13/) — Security & Compliance
- T01 KMS (Customer-Managed Keys, Envelope Encryption)
- T02 Secrets Manager vs Parameter Store
- T03 GuardDuty, Security Hub, Inspector, Macie
- T04 Config & Conformance Packs
- T05 Detective, Audit Manager

### [C14](C14/) — Well-Architected Framework
- T01 Six Pillars (Operational Excellence, Security, Reliability, Performance, Cost, Sustainability)
- T02 Running a WAR (Well-Architected Review)

## Critical Concepts

### IAM Policy Evaluation

```
1. Explicit DENY anywhere → DENY (final)
2. Org SCP missing ALLOW → DENY
3. Permission boundary missing ALLOW → DENY
4. Identity-based or resource-based ALLOW → ALLOW
5. Otherwise → DENY (default)
```

### VPC Design Pattern

```
Region: us-east-1
├── VPC 10.0.0.0/16
│   ├── AZ a
│   │   ├── public subnet  10.0.1.0/24  (IGW route)
│   │   ├── private subnet 10.0.11.0/24 (NAT route)
│   │   └── isolated       10.0.21.0/24 (no internet)
│   ├── AZ b
│   │   └── ...
│   └── AZ c
│       └── ...
```

### Aurora Architecture

Shared storage volume (replicated 6 ways across 3 AZs). Compute layer (writers + readers) reads/writes to the storage layer. Failover swaps which compute is the writer; storage doesn't move.

### DynamoDB Partition Key Math

- Each partition: ~3000 RCU + 1000 WCU
- Hot partition = throttling
- Design for uniform distribution (good keys: userId+timestamp; bad: status which is "active" or "inactive")

## Recommended Reading

- AWS Documentation (the only one to read end-to-end for your area)
- *AWS Cookbook* — O'Reilly
- *The DynamoDB Book* — Alex DeBrie
- Last Week in AWS newsletter
- AWS re:Invent talks (especially 300/400-level)

## Interview Relevance

- Amazon SDE/Sysops: deep AWS questions are standard
- All clouds: AWS is the lingua franca
- Senior+ roles: WAR / multi-account / org-level design
- "Design X on AWS" is a standard system design prompt

## Next

→ [L09 — Azure & GCP Comparative Mastery](../L09/README.md)
