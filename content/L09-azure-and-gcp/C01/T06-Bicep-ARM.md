# L09/C01/T06 — Bicep & ARM Templates

## Learning Objectives

- Use Bicep for IaC
- Compare to Terraform / ARM

## ARM Templates

JSON-based, Azure-native:
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [{
    "type": "Microsoft.Storage/storageAccounts",
    "apiVersion": "2023-01-01",
    "name": "mystorage",
    "location": "eastus",
    "sku": {"name": "Standard_LRS"},
    "kind": "StorageV2"
  }]
}
```

Verbose; hard to read.

## Bicep

DSL → compiles to ARM:
```bicep
resource sa 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'mystorage'
  location: 'eastus'
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}
```

Much cleaner.

## Install

```bash
az bicep install
```

Or via Az CLI.

## Deploy

```bash
az deployment group create \
  --resource-group myrg \
  --template-file main.bicep \
  --parameters env=prod
```

## Parameters

```bicep
param env string
param location string = 'eastus'
param vmSize string = 'Standard_D2s_v5'

resource vm 'Microsoft.Compute/virtualMachines@2024-03-01' = {
  name: 'vm-${env}'
  location: location
  properties: {
    hardwareProfile: { vmSize: vmSize }
    ...
  }
}
```

## Variables

```bicep
var prefix = 'myapp-${env}'
var storageName = '${prefix}-storage'

resource sa '...' = {
  name: storageName
  ...
}
```

## Outputs

```bicep
output storageName string = sa.name
output storageId string = sa.id
```

For downstream / composition.

## Modules

```bicep
// modules/vnet.bicep
param vnetName string
param addressSpace string

resource vnet '...' = {
  name: vnetName
  properties: { addressSpace: { addressPrefixes: [ addressSpace ] } }
}

output vnetId string = vnet.id
```

```bicep
// main.bicep
module vnet 'modules/vnet.bicep' = {
  name: 'vnetDeploy'
  params: {
    vnetName: 'myvnet'
    addressSpace: '10.0.0.0/16'
  }
}
```

= Terraform module.

## Loops

```bicep
param subnets array = [
  { name: 'web', prefix: '10.0.1.0/24' }
  { name: 'app', prefix: '10.0.2.0/24' }
]

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' = [for s in subnets: {
  parent: vnet
  name: s.name
  properties: { addressPrefix: s.prefix }
}]
```

## Conditions

```bicep
param createBastion bool = false

resource bastion '...' = if (createBastion) {
  name: 'mybastion'
  ...
}
```

## Existing Resources

```bicep
resource existingVnet 'Microsoft.Network/virtualNetworks@2023-09-01' existing = {
  name: 'shared-vnet'
  scope: resourceGroup('shared-rg')
}

// Reference
existingVnet.id
```

For: cross-RG references.

## What-If

```bash
az deployment group what-if \
  --resource-group myrg \
  --template-file main.bicep
```

= terraform plan.

## Decompile

```bash
az bicep decompile --file template.json
```

ARM → Bicep. For migration.

## State

Bicep / ARM: **stateless** unlike Terraform.

Azure tracks deployments:
```bash
az deployment group list --resource-group myrg
```

Idempotent; converges to desired state.

## Vs Terraform

| | Bicep | Terraform |
|---|---|---|
| Multi-cloud | Azure-only | Multi-cloud |
| State | Azure-managed | Local/remote backend |
| Language | DSL | HCL |
| Maturity | Newer | Mature |
| Community | Smaller | Huge |
| Drift | Limited | Plan detects |

For Azure-only: Bicep convenient.
For multi-cloud / cross-team: Terraform.

## Scope

Deployment scope:
- **resourceGroup**: default
- **subscription**: sub-level resources (RGs themselves)
- **managementGroup**: MG-level (policies)
- **tenant**: tenant-level

```bicep
targetScope = 'subscription'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'myrg'
  location: 'eastus'
}
```

## Deployment Stacks (Newer)

```bash
az stack group create --name mystack --resource-group myrg --template-file main.bicep
```

Manages resources as unit; can deny-delete via stack.

Closer to Terraform behavior.

## Functions

```bicep
var hash = uniqueString(resourceGroup().id)
var name = 'sa${take(hash, 8)}'
```

Built-in: uniqueString, format, take, etc.

## Best Practices

- Modules for reuse
- Parameters for config
- Outputs for composition
- Lint (`az bicep build`)
- What-If before deploy
- Version control templates
- Use Stacks for atomic lifecycle

## Common Mistakes

- Hardcoded values (use params)
- No what-if (surprises)
- One huge file (no modules)
- Missing tags
- Wrong scope

## CI/CD

```yaml
- uses: azure/bicep-deploy@v2
  with:
    resourceGroupName: myrg
    templateFile: main.bicep
    parameters: 'env=prod'
```

## Linting

```bash
az bicep build --file main.bicep
# Errors / warnings
```

For: catch issues pre-deploy.

## VS Code

Bicep extension: syntax, validation, completion.

For: dev experience.

## Comparison Example

Terraform:
```hcl
resource "azurerm_storage_account" "sa" {
  name                = "mystorage"
  resource_group_name = "myrg"
  location            = "eastus"
  account_tier        = "Standard"
  account_replication_type = "LRS"
}
```

Bicep:
```bicep
resource sa 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'mystorage'
  location: 'eastus'
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}
```

Similar verbosity.

## Quick Refs

```bash
# Install
az bicep install

# Deploy
az deployment group create --resource-group RG --template-file FILE.bicep

# What-If
az deployment group what-if --resource-group RG --template-file FILE.bicep

# Build
az bicep build --file FILE.bicep
```

## Interview Prep

**Junior**: "What's Bicep."

**Mid**: "Bicep vs ARM."

**Senior**: "Bicep vs Terraform."

**Staff**: "IaC strategy for Azure-heavy org."

## Next Topic

→ Move to [L09/C02 — GCP Core](../C02/README.md)
