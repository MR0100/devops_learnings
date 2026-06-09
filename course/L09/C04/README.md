# L09/C04 — Service-by-Service Comparison

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Compute-Equivalents.md) | Compute Equivalents | 0.5 hr |
| [T02](T02-Storage-Equivalents.md) | Storage Equivalents | 0.5 hr |
| [T03](T03-Database-Equivalents.md) | Database Equivalents | 0.5 hr |
| [T04](T04-Networking-Equivalents.md) | Networking Equivalents | 0.5 hr |

## Compute

| AWS | Azure | GCP |
|---|---|---|
| EC2 | VM | Compute Engine |
| ASG | VM Scale Set | Managed Instance Group |
| ECS | Container Apps / ACI | (Cloud Run for similar) |
| EKS | AKS | GKE |
| Fargate | Container Apps / ACI | Cloud Run / GKE Autopilot |
| Lambda | Functions | Cloud Functions |
| App Runner | App Service | Cloud Run |
| Beanstalk | App Service | App Engine |
| Batch | Batch | Batch / Dataflow |

## Storage

| AWS | Azure | GCP |
|---|---|---|
| S3 | Blob Storage | Cloud Storage (GCS) |
| EBS | Managed Disks | Persistent Disk |
| EFS | Files (NFS/SMB) | Filestore |
| FSx for NetApp | NetApp Files | NetApp Volumes |
| Glacier | Archive (Blob tier) | Archive (GCS tier) |
| Storage Gateway | StorSimple | Transfer Service |
| Snowball | Data Box | Transfer Appliance |
| DataSync | AzCopy / Data Box | Storage Transfer Service |

## Databases

| AWS | Azure | GCP |
|---|---|---|
| RDS | SQL Database / MI / Postgres / MySQL | Cloud SQL |
| Aurora | (Hyperscale tier of SQL DB) | AlloyDB (PG), Spanner (global) |
| DynamoDB | Cosmos DB | Firestore / Bigtable |
| DocumentDB | Cosmos DB (MongoDB API) | (use MongoDB Atlas) |
| ElastiCache (Redis) | Cache for Redis | Memorystore (Redis) |
| Neptune (graph) | Cosmos DB (Gremlin API) | (use Neo4j Aura) |
| Keyspaces (Cassandra) | Cosmos DB (Cassandra API) | (use DataStax Astra) |
| Timestream | Time Series Insights (deprecated) | Bigtable / BigQuery |
| Redshift | Synapse Analytics | BigQuery |
| Athena | Synapse Serverless SQL | BigQuery |
| Glue | Data Factory | Dataflow / Dataproc |
| Kinesis | Event Hubs | Pub/Sub |

## Messaging & Streaming

| AWS | Azure | GCP |
|---|---|---|
| SQS | Service Bus Queues | Pub/Sub (kind of), Tasks |
| SNS | Service Bus Topics / Event Grid | Pub/Sub |
| EventBridge | Event Grid | Eventarc / Pub/Sub |
| Kinesis Data Streams | Event Hubs | Pub/Sub (sustained) |
| Kinesis Firehose | Stream Analytics | Dataflow |
| MSK | HDInsight Kafka | (Confluent Cloud) |

## Networking

| AWS | Azure | GCP |
|---|---|---|
| VPC | VNet | VPC |
| Subnet | Subnet | Subnet (regional) |
| Security Group | NSG | Firewall Rules |
| Route Table | Route Table | Route |
| IGW | (implicit) | Default route to Internet |
| NAT Gateway | NAT Gateway | Cloud NAT |
| VPC Peering | VNet Peering | VPC Peering / Network Connectivity Center |
| Transit Gateway | Virtual WAN | NCC Hub |
| PrivateLink | Private Endpoint / Private Link Service | Private Service Connect |
| Direct Connect | ExpressRoute | Cloud Interconnect |
| Site-to-Site VPN | VPN Gateway | Cloud VPN |
| Route 53 | DNS | Cloud DNS |
| ALB | Application Gateway | HTTP(S) LB |
| NLB | Load Balancer | TCP/UDP LB |
| Global Accelerator | Front Door (partial) | Cloud LB (global) |
| CloudFront | CDN / Front Door | Cloud CDN |
| WAF | Front Door WAF / App Gateway WAF | Cloud Armor |
| Shield | DDoS Protection | Cloud Armor + (auto) |

## Identity & Security

| AWS | Azure | GCP |
|---|---|---|
| IAM | Entra ID + Azure RBAC | IAM |
| IAM Identity Center (SSO) | Entra ID (built-in) | Cloud Identity / Workforce ID |
| KMS | Key Vault | KMS |
| Secrets Manager | Key Vault | Secret Manager |
| Certificate Manager | App Service Certs / Key Vault | Certificate Manager |
| GuardDuty | Defender for Cloud | Security Command Center |
| WAF | Front Door WAF | Cloud Armor |
| Inspector | Defender for Cloud | Security Command Center |
| Config | Policy + Resource Graph | Asset Inventory + Policy Intelligence |
| CloudTrail | Activity Log + Diagnostic Settings | Cloud Audit Logs |
| Macie | Defender for Information Protection | Cloud DLP |
| Detective | Sentinel | Chronicle |
| Audit Manager | Compliance Manager | (use SCC) |

## Observability

| AWS | Azure | GCP |
|---|---|---|
| CloudWatch Metrics | Azure Monitor Metrics | Cloud Monitoring |
| CloudWatch Logs | Azure Monitor Logs / Log Analytics | Cloud Logging |
| X-Ray | Application Insights | Cloud Trace |
| Managed Prometheus | Azure Monitor Managed Prometheus | Managed Service for Prometheus |
| Managed Grafana | Managed Grafana | Managed Service for Grafana |

## Choosing a Cloud for a Workload

| Need | Lean toward |
|---|---|
| Cheapest at small scale | AWS / GCP free tier |
| Already on Microsoft stack | Azure |
| Want best K8s experience | GCP (GKE Autopilot) |
| Need BigQuery scale analytics | GCP |
| Need Spanner global ACID | GCP |
| Need broadest service catalog | AWS |
| Need most mature 3rd-party ecosystem | AWS |
| Need clean global networking | GCP |
| Enterprise hybrid (with Azure Arc) | Azure |

## Interview Themes

- "What's the GCP equivalent of DynamoDB?"
- "Walk me through equivalents you've used"
- "When is each cloud's offering meaningfully different?"
- "Map a system from AWS to Azure"
