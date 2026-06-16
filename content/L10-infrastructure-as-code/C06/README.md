# L10/C06 — Writing Custom Providers

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Provider-Anatomy.md) | Provider Anatomy (Go) | 1.5 hr |
| [T02](T02-Plugin-Framework-SDK.md) | Plugin Framework vs SDK v2 | 1 hr |

## When to Build a Provider

Build when:
- An API you depend on isn't covered by an existing provider
- You have an internal platform with REST API
- You want Terraform to manage your SaaS resources

Examples: GitHub provider, Cloudflare, Datadog, internal IDP APIs, custom platform.

## Provider Anatomy (Plugin Framework, modern)

Provider = Go binary that Terraform talks to over RPC.

```go
package main

import (
    "context"
    "github.com/hashicorp/terraform-plugin-framework/providerserver"
    "yourorg/internal/provider"
)

func main() {
    providerserver.Serve(context.Background(), provider.New("dev"), providerserver.ServeOpts{
        Address: "registry.terraform.io/yourorg/myprovider",
    })
}
```

### Provider Struct
```go
type myProvider struct {
    version string
}

func (p *myProvider) Metadata(_ context.Context, _ MetadataRequest, resp *MetadataResponse) {
    resp.TypeName = "myprovider"
    resp.Version = p.version
}

func (p *myProvider) Schema(_ context.Context, _ SchemaRequest, resp *SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "endpoint": schema.StringAttribute{Required: true},
            "token":    schema.StringAttribute{Required: true, Sensitive: true},
        },
    }
}

func (p *myProvider) Configure(ctx context.Context, req ConfigureRequest, resp *ConfigureResponse) {
    var cfg ProviderModel
    diags := req.Config.Get(ctx, &cfg)
    resp.Diagnostics.Append(diags...)
    if resp.Diagnostics.HasError() {
        return
    }
    client := newAPIClient(cfg.Endpoint, cfg.Token)
    resp.DataSourceData = client
    resp.ResourceData = client
}

func (p *myProvider) Resources(_ context.Context) []func() resource.Resource {
    return []func() resource.Resource{
        NewWidgetResource,
    }
}

func (p *myProvider) DataSources(_ context.Context) []func() datasource.DataSource {
    return []func() datasource.DataSource{
        NewWidgetDataSource,
    }
}
```

### Resource Implementation
```go
type widgetResource struct {
    client *APIClient
}

func (r *widgetResource) Metadata(_ context.Context, req MetadataRequest, resp *MetadataResponse) {
    resp.TypeName = req.ProviderTypeName + "_widget"
}

func (r *widgetResource) Schema(_ context.Context, _ SchemaRequest, resp *SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "id":   schema.StringAttribute{Computed: true},
            "name": schema.StringAttribute{Required: true},
            "size": schema.Int64Attribute{Optional: true},
        },
    }
}

// Create, Read, Update, Delete methods...
func (r *widgetResource) Create(ctx context.Context, req CreateRequest, resp *CreateResponse) {
    var plan WidgetModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    if resp.Diagnostics.HasError() { return }

    w, err := r.client.CreateWidget(ctx, plan.Name.ValueString())
    if err != nil { resp.Diagnostics.AddError("create failed", err.Error()); return }

    plan.ID = types.StringValue(w.ID)
    resp.Diagnostics.Append(resp.State.Set(ctx, plan)...)
}
```

## Plugin Framework vs SDK v2

### SDK v2 (legacy but widely used)
- Imperative struct definitions
- helper/schema package
- Supports map[string]*Schema
- Mature, lots of examples

### Plugin Framework (modern, recommended for new)
- More type-safe
- Better diagnostics
- Better Plan/State separation
- Supports nested types properly
- Required for many newer features

```
SDK v2:                 Plugin Framework:
Resource{               type widgetResource struct{}
  Schema: map[string]*Schema{
    "name": &Schema{    type WidgetModel struct {
      Type: TypeString,   Name types.String `tfsdk:"name"`
      Required: true,   }
    },
  },
  Create: func...,      func (r *widgetResource) Create(ctx, req, resp)
  Read: func...,        func (r *widgetResource) Read(ctx, req, resp)
  Update: func...,      func (r *widgetResource) Update(ctx, req, resp)
  Delete: func...,      func (r *widgetResource) Delete(ctx, req, resp)
}
```

Both can coexist in one provider (use `muxserver`).

## Testing Providers

Acceptance tests run real Terraform against real APIs:

```go
func TestAccWidgetResource(t *testing.T) {
    resource.Test(t, resource.TestCase{
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        Steps: []resource.TestStep{
            {
                Config: `
                    provider "myprovider" {
                      endpoint = "http://localhost:8080"
                      token    = "test"
                    }
                    resource "myprovider_widget" "test" {
                      name = "test"
                    }
                `,
                Check: resource.ComposeTestCheckFunc(
                    resource.TestCheckResourceAttr("myprovider_widget.test", "name", "test"),
                ),
            },
        },
    })
}
```

Run with `TF_ACC=1 go test ./...`.

## Publishing

### Public (Terraform Registry)
1. Build with GoReleaser
2. Sign with GPG
3. Tag (semver)
4. Registry pulls from GitHub releases

### Private
- Terraform Cloud / Enterprise private registry
- Or, serve provider via private S3 + custom protocol response

## Interview Themes

- "When would you build a Terraform provider?"
- "Plugin Framework vs SDK v2 — what changed?"
- "How do acceptance tests work?"
- "Walk me through a Create method"
- "How do providers handle imports?"
