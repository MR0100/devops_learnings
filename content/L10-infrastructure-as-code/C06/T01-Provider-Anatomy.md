# L10/C06/T01 — Provider Anatomy (Go)

## Learning Objectives

- Understand Terraform provider
- Plan custom provider

## Provider

Plugin between Terraform and API.

For each resource type:
- Schema
- Create / Read / Update / Delete (CRUD)
- Import
- Validation

Written in Go using HashiCorp SDK.

## When Custom Provider

- Internal API (no existing provider)
- Specialized SaaS not in registry
- Custom abstractions over multiple APIs
- Modify resource provider behavior

For most: existing providers work.

## Provider Plugin Framework

Two options:
- SDK v2 (mature, legacy)
- Plugin Framework (modern, recommended for new)

For new: Plugin Framework.

## Plugin Framework Structure

```go
// internal/provider/provider.go
type ExampleProvider struct{}

func (p *ExampleProvider) Metadata(ctx, req, resp) {
    resp.TypeName = "example"
    resp.Version = "1.0.0"
}

func (p *ExampleProvider) Schema(ctx, req, resp) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "api_url": schema.StringAttribute{
                Required: true,
            },
            "token": schema.StringAttribute{
                Required: true,
                Sensitive: true,
            },
        },
    }
}

func (p *ExampleProvider) Configure(ctx, req, resp) {
    // Initialize API client
}

func (p *ExampleProvider) Resources(ctx) []func() resource.Resource {
    return []func() resource.Resource{
        NewWidgetResource,
    }
}

func (p *ExampleProvider) DataSources(ctx) []func() datasource.DataSource {
    return []func() datasource.DataSource{}
}
```

## Resource

```go
type WidgetResource struct {
    client *APIClient
}

func (r *WidgetResource) Metadata(ctx, req, resp) {
    resp.TypeName = "example_widget"
}

func (r *WidgetResource) Schema(ctx, req, resp) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "id": schema.StringAttribute{Computed: true},
            "name": schema.StringAttribute{Required: true},
            "color": schema.StringAttribute{
                Optional: true,
                Validators: []validator.String{
                    stringvalidator.OneOf("red", "blue", "green"),
                },
            },
        },
    }
}

func (r *WidgetResource) Create(ctx, req, resp) {
    var plan WidgetModel
    diag := req.Plan.Get(ctx, &plan)
    resp.Diagnostics.Append(diag...)
    
    // Call API to create
    id, err := r.client.CreateWidget(plan.Name, plan.Color)
    if err != nil {
        resp.Diagnostics.AddError("Failed to create", err.Error())
        return
    }
    
    plan.ID = types.StringValue(id)
    resp.State.Set(ctx, &plan)
}

func (r *WidgetResource) Read(ctx, req, resp) {
    var state WidgetModel
    req.State.Get(ctx, &state)
    
    // Re-read from API
    widget, err := r.client.GetWidget(state.ID.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Failed to read", err.Error())
        return
    }
    
    state.Name = types.StringValue(widget.Name)
    state.Color = types.StringValue(widget.Color)
    resp.State.Set(ctx, &state)
}

func (r *WidgetResource) Update(ctx, req, resp) {
    // Apply changes
}

func (r *WidgetResource) Delete(ctx, req, resp) {
    var state WidgetModel
    req.State.Get(ctx, &state)
    
    r.client.DeleteWidget(state.ID.ValueString())
}

func (r *WidgetResource) ImportState(ctx, req, resp) {
    resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}
```

## Resource Model

```go
type WidgetModel struct {
    ID    types.String `tfsdk:"id"`
    Name  types.String `tfsdk:"name"`
    Color types.String `tfsdk:"color"`
}
```

Maps Terraform schema to Go.

## Plan, State, Config

In CRUD:
- Plan: desired (from config)
- State: stored
- Config: HCL parsed

For Update:
- Plan: desired
- State: current
- Diff: what to change

## Schema Attributes

```go
schema.StringAttribute{
    Required: true,    // must be set
    Optional: false,
    Computed: false,
    Sensitive: false,
    Description: "...",
}
```

Types: String, Int64, Float64, Bool, List, Set, Map, Object, Single Nested.

## Validators

```go
Validators: []validator.String{
    stringvalidator.LengthBetween(1, 64),
    stringvalidator.RegexMatches(regexp.MustCompile("^[a-z]+$"), "lowercase only"),
}
```

Built-in + custom.

## Plan Modifiers

```go
PlanModifiers: []planmodifier.String{
    stringplanmodifier.UseStateForUnknown(),    // keep state if not in plan
    stringplanmodifier.RequiresReplace(),        // force replace if changed
}
```

For: complex behaviors.

## Provider Configuration

User sets:
```hcl
provider "example" {
  api_url = "https://api.example.com"
  token   = var.token
}
```

Provider Configure() reads; initializes client.

## Main

```go
// main.go
package main

import (
    "context"
    "github.com/hashicorp/terraform-plugin-framework/providerserver"
)

func main() {
    providerserver.Serve(context.Background(), New, providerserver.ServeOpts{
        Address: "registry.terraform.io/me/example",
    })
}

func New() provider.Provider {
    return &ExampleProvider{}
}
```

## Build + Install

```bash
go build -o terraform-provider-example
mv terraform-provider-example ~/.terraform.d/plugins/registry.terraform.io/me/example/1.0.0/darwin_amd64/
```

For local testing.

## Use

```hcl
terraform {
  required_providers {
    example = {
      source  = "me/example"
      version = "1.0.0"
    }
  }
}

provider "example" {
  api_url = "..."
  token   = var.token
}

resource "example_widget" "my" {
  name  = "thing"
  color = "blue"
}
```

## Testing

```go
func TestWidget(t *testing.T) {
    resource.Test(t, resource.TestCase{
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: `
                  resource "example_widget" "test" {
                    name = "test"
                    color = "blue"
                  }
                `,
                Check: resource.ComposeAggregateTestCheckFunc(
                    resource.TestCheckResourceAttr("example_widget.test", "color", "blue"),
                ),
            },
        },
    })
}
```

Acceptance tests; real API.

## Documentation

Each resource: docs in `docs/` for registry.

Generated via:
```bash
go generate ./...
# Uses tfplugindocs
```

For: registry display.

## Publishing

For Terraform Registry:
- Tag release in GitHub
- GoReleaser builds binaries
- Sign with GPG
- Registry indexes

```yaml
# .goreleaser.yml
builds:
- env: [CGO_ENABLED=0]
  flags: [-trimpath]
  ldflags:
  - '-s -w -X main.version={{.Version}}'
  goos: [linux, darwin, windows]
  goarch: [amd64, arm64]
  binary: '{{ .ProjectName }}_v{{ .Version }}'
```

## Best Practices

- Use Plugin Framework (new)
- Strong typing
- Validators for input
- Plan modifiers for special behavior
- Acceptance tests
- Documentation
- Semver
- GoReleaser

## Common Mistakes

- Schema mismatch with API
- Missing import
- Update doesn't handle all fields
- No tests
- Sensitive fields not marked

## When NOT Build

- Existing provider works (override behavior with locals)
- Use external data source / null_resource instead
- Wait for community provider

For: build only if necessary.

## Alternative: Local-exec

For simple needs:
```hcl
resource "null_resource" "x" {
  provisioner "local-exec" {
    command = "my-cli create ..."
  }
}
```

Hacky; no state management. Avoid for production.

## Quick Refs

```bash
# Local dev
mkdir -p ~/.terraform.d/plugins/me/example/1.0.0/$(go env GOOS)_$(go env GOARCH)
go build -o ~/.terraform.d/plugins/me/example/1.0.0/$(go env GOOS)_$(go env GOARCH)/terraform-provider-example

# Test
TF_ACC=1 go test -v ./...

# Generate docs
go generate ./...
```

## Interview Prep

**Senior**: "Custom provider use case."

**Staff**: "Internal platform via provider."

## Next Topic

→ [T02 — Plugin Framework vs SDK v2](T02-Plugin-Framework-SDK.md)
