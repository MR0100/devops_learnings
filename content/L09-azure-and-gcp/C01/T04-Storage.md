# L09/C01/T04 — Storage (Blob, Files, Disks)

## Learning Objectives

- Choose Azure storage
- Compare to AWS

## Storage Account

Container for storage services:
```bash
az storage account create \
  --name mystorageacct \
  --resource-group myrg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2
```

Provides: Blob, Files, Queues, Tables, Disks.

## SKUs (Replication)

- **LRS**: Local (3 copies in 1 DC)
- **ZRS**: Zone (across AZs)
- **GRS**: Geo (paired region; async)
- **RA-GRS**: Geo + read access on secondary
- **GZRS**: Geo + Zone
- **RA-GZRS**: Geo + Zone + read on secondary

For prod: ZRS or GRS.

## Blob Storage

= S3:
```bash
az storage blob upload --account-name X --container Y --name file --file ./file.txt
az storage blob download --account-name X --container Y --name file --file ./out.txt
```

Containers ≈ buckets.

## Blob Tiers

- **Hot**: frequent
- **Cool**: 30+ days
- **Cold**: 90+ days
- **Archive**: 180+ days; hours-to-days retrieval

Lifecycle policy auto-tier:
```json
{
  "rules": [{
    "name": "tier-cool",
    "type": "Lifecycle",
    "definition": {
      "actions": {"baseBlob": {"tierToCool": {"daysAfterModificationGreaterThan": 30}}},
      "filters": {"blobTypes": ["blockBlob"]}
    }
  }]
}
```

## Blob Types

- **Block**: standard (default)
- **Append**: log files
- **Page**: VHDs (disks)

## Access

```bash
# Public (anonymous)
az storage container set-permission --name mycontainer --public-access blob

# SAS (shared access signature)
az storage blob generate-sas --account-name X --container Y --name file --permissions r --expiry 2026-12-31
```

For private: SAS tokens; RBAC.

## Azure Files

= EFS / SMB:
```bash
az storage share create --name myshare --account-name X
```

Mount:
```bash
sudo mount -t cifs //X.file.core.windows.net/myshare /mnt \
  -o vers=3.0,credentials=/etc/smbcreds
```

NFS available (premium tier).

For: shared files across VMs.

## Managed Disks

VM disks:
- **Premium SSD**: low latency, IOPS
- **Standard SSD**: cost-effective
- **Standard HDD**: cheapest
- **Ultra Disk**: highest perf
- **Premium SSD v2**: customizable

```bash
az disk create --resource-group myrg --name mydisk --size-gb 100 --sku Premium_LRS
```

## Disk Snapshots

```bash
az snapshot create --resource-group myrg --name mysnap --source mydisk
```

For: backup; clone.

## Queues

= SQS:
```bash
az storage queue create --name myqueue --account-name X
```

Lightweight; up to 64 KB messages.

For heavier: Service Bus.

## Tables

= DynamoDB (basic):
NoSQL key-value.

Legacy; Cosmos DB recommended for new.

## Data Lake Storage Gen2

= S3 + hierarchical namespace:
- HDFS-compatible
- For: big data analytics
- Spark, Hadoop

```bash
az storage account create --hierarchical-namespace true ...
```

## Encryption

At rest: AES-256 by default.
Keys:
- **Microsoft-managed**: default
- **Customer-managed (CMK)**: Key Vault
- **Customer-provided**: BYOK

In transit: HTTPS.

## RBAC + ACL

- Account-level: RBAC
- Blob-level (DLS gen2): ACLs (POSIX-style)

Combination = fine-grained.

## CDN

Azure CDN + Front Door:
- Static content
- Edge cached
- HTTPS termination

For global delivery.

## CORS

```bash
az storage cors add --services b \
  --methods GET POST --origins '*' --allowed-headers '*' --account-name X
```

For web apps.

## Object Replication

```bash
az storage account or-policy create ...
```

Cross-account, cross-region replication for blobs.

For: DR, compliance.

## Soft Delete

Recover deleted blobs/files:
```bash
az storage blob service-properties update --enable-delete-retention true --delete-retention-days 7
```

For: accidental delete protection.

## Versioning

```bash
az storage account blob-service-properties update --enable-versioning true
```

Every write creates version. Like S3 versioning.

## Immutable Blobs

```bash
az storage container immutability-policy create --account-name X --container Y --period 365
```

WORM (Write Once Read Many). For compliance.

## Performance Tiers

- **Standard**: HDD-backed
- **Premium**: SSD-backed (low latency)

For: latency-sensitive use cases.

## AWS Comparison

| Azure | AWS |
|---|---|
| Blob | S3 |
| Files | EFS / FSx |
| Disks | EBS |
| Queue | SQS |
| Table | DynamoDB |
| Data Lake | S3 + Lake Formation |
| CDN | CloudFront |

## Cost

- Hot: $0.02/GB/mo
- Cool: $0.01/GB
- Archive: $0.001/GB
- Egress: per GB out

For analytics: DLS Gen2 + Hot.
For backup: Cool / Archive.

## Lifecycle Examples

```
Hot:    Day 0
Cool:   Day 30
Archive: Day 90
Delete:  Day 365
```

For: backup data.

## Best Practices

- Tier with lifecycle policies
- SAS for temp access; RBAC for users
- Soft delete on (recovery)
- Versioning critical data
- CMK if compliance requires
- Network rules (firewall)
- Private endpoints (VNet integration)

## Common Mistakes

- Premium tier when not needed (cost)
- Public access (data leak)
- No lifecycle (cost grows)
- LRS for critical (no DR)
- No soft delete (lost on accident)

## Private Endpoints

```bash
az network private-endpoint create \
  --resource-group myrg --name mype \
  --vnet-name myvnet --subnet mysubnet \
  --private-connection-resource-id /subscriptions/.../storageAccounts/X \
  --group-id blob
```

For: VNet-only access; bypass Internet.

## Quick Refs

```bash
# Storage account
az storage account create / list / show

# Blob
az storage blob upload / download / list
az storage blob generate-sas

# File share
az storage share create

# Disk
az disk create / snapshot

# Queue / Table
az storage queue / table
```

## Interview Prep

**Junior**: "Azure storage types."

**Mid**: "Replication SKUs."

**Senior**: "Lifecycle + cost optimization."

**Staff**: "Multi-region data architecture."

## Next Topic

→ [T05 — Networking (VNets, NSGs, Application Gateway, Front Door)](T05-Networking.md)
