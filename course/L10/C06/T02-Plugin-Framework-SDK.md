# L10/C06/T02 — Plugin Framework vs SDK v2

## Learning Objectives

- Choose Plugin Framework or SDK v2
- Migrate between

## SDK v2 (Legacy)

Older provider SDK:
- Mature
- Most existing providers
- Less type-safe

## Plugin Framework

Newer (recommended for new):
- Type-safe (uses Go generics)
- Better validation
- Modern API
- Plan modifiers
- Easier testing

For new providers: use Plugin Framework.

## SDK v2 Resource

```go
package widget

import "github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"

func ResourceWidget() *schema.Resource {
    return &schema.Resource{
        CreateContext: resourceWidgetCreate,
        ReadContext:   resourceWidgetRead,
        UpdateContext: resourceWidgetUpdate,
        DeleteContext: resourceWidgetDelete,
        
        Schema: map[string]*schema.Schema{
            "name": {
                Type:     schema.TypeString,
                Required: true,
            },
            "color": {
                Type:     schema.TypeString,
                Optional: true,
                ValidateFunc: validation.StringInSlice([]string{"red", "blue", "green"}, false),
            },
        },
    }
}

func resourceWidgetCreate(ctx context.Context, d *schema.ResourceData, m interface{}) diag.Diagnostics {
    client := m.(*APIClient)
    
    name := d.Get("name").(string)
    color := d.Get("color").(string)
    
    id, err := client.CreateWidget(name, color)
    if err != nil {
        return diag.FromErr(err)
    }
    
    d.SetId(id)
    return resourceWidgetRead(ctx, d, m)
}
```

`d.Get` returns interface{}; cast yourself.

## Plugin Framework Resource

```go
type WidgetResource struct {
    client *APIClient
}

type WidgetModel struct {
    ID    types.String `tfsdk:"id"`
    Name  types.String `tfsdk:"name"`
    Color types.String `tfsdk:"color"`
}

func (r *WidgetResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
    var plan WidgetModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    if resp.Diagnostics.HasError() {
        return
    }
    
    id, err := r.client.CreateWidget(plan.Name.ValueString(), plan.Color.ValueString())
    if err != nil {
        resp.Diagnostics.AddError("Create failed", err.Error())
        return
    }
    
    plan.ID = types.StringValue(id)
    resp.Diagnostics.Append(resp.State.Set(ctx, &plan)...)
}
```

Strongly typed; no casts.

## Differences

| | SDK v2 | Plugin Framework |
|---|---|---|
| API | `schema.Resource` struct | `resource.Resource` interface |
| Data access | `d.Get("x").(type)` | `plan.X.ValueString()` |
| Type safety | Cast | Generic |
| Validation | ValidateFunc | Validators[] |
| Plan modifiers | CustomizeDiff | PlanModifiers |
| Schemas | map[string]*Schema | schema.Schema struct |

## When SDK v2

- Maintaining existing provider
- Some third-party libs only SDK v2
- Team familiar

For new code: try Plugin Framework.

## When Plugin Framework

- New providers
- Modern features
- Better validation
- Future-proof

HashiCorp recommends Plugin Framework for new.

## Mixed Provider

Can mix:
- Provider in Plugin Framework
- Some resources SDK v2 (via mux)
- Migrate incrementally

```go
import "github.com/hashicorp/terraform-plugin-mux/tf6muxserver"

muxServer, _ := tf6muxserver.NewMuxServer(ctx, providers...)
```

## Migrate SDK v2 → Plugin Framework

1. Set up muxed provider (both work)
2. Migrate one resource at a time
3. Test
4. Remove SDK v2 dep

For: existing providers without big-bang rewrite.

## Plan Modifiers (Framework)

Powerful behaviors:
```go
PlanModifiers: []planmodifier.String{
    stringplanmodifier.UseStateForUnknown(),
    stringplanmodifier.RequiresReplaceIfConfigured(),
}
```

For: complex update / replace logic.

SDK v2 equivalent: CustomizeDiff (less elegant).

## Custom Validators

Framework:
```go
type RegexValidator struct{}

func (v RegexValidator) Description(ctx) string { return "..." }
func (v RegexValidator) MarkdownDescription(ctx) string { return "..." }
func (v RegexValidator) ValidateString(ctx, req, resp) {
    if !regex.MatchString(req.ConfigValue.ValueString()) {
        resp.Diagnostics.AddAttributeError(req.Path, "Invalid", "must match regex")
    }
}
```

Implement validator interface.

## Custom Plan Modifier

```go
type MyModifier struct{}

func (m MyModifier) PlanModifyString(ctx, req, resp) {
    if req.PlanValue.IsUnknown() {
        resp.PlanValue = types.StringValue("default")
    }
}
```

For: complex logic.

## Testing

Both support same testing:
```go
resource.Test(t, resource.TestCase{
    Steps: []resource.TestStep{...},
})
```

Plugin Framework: stronger types in tests.

## Provider Lifecycle

```
ConfigValidators / ValidateConfig
   ↓
Configure
   ↓
For each resource:
  Read (refresh)
  Plan modifiers
  Create / Update / Delete
```

Plugin Framework: cleaner separation.

## Examples

### AWS Provider
Migrated from SDK v2 → Plugin Framework gradually.

Hybrid currently.

### Newer Providers
Most new ones: Plugin Framework only.

## Documentation Generation

Both work with tfplugindocs:
```bash
go install github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs@latest
tfplugindocs
```

Generates from schema + examples.

## Performance

Both similar performance. Framework: slightly better (less reflection).

For: not a deciding factor.

## Resource Naming

Framework:
```go
func (r *WidgetResource) Metadata(ctx, req, resp) {
    resp.TypeName = req.ProviderTypeName + "_widget"
    // example_widget
}
```

SDK v2: implicit via map key.

## Schema Description

Framework: per-attribute:
```go
schema.StringAttribute{
    Description: "Widget name",
    MarkdownDescription: "Widget **name**",
}
```

For docs generation.

## Computed Fields

```go
schema.StringAttribute{
    Computed: true,
    PlanModifiers: []planmodifier.String{
        stringplanmodifier.UseStateForUnknown(),
    },
}
```

Computed = set by provider; not by user.

## Block Types

For nested:
```go
schema.SingleNestedAttribute{
    Optional: true,
    Attributes: map[string]schema.Attribute{...},
}

// or
schema.ListNestedAttribute{
    Optional: true,
    NestedObject: schema.NestedAttributeObject{
        Attributes: map[string]schema.Attribute{...},
    },
}
```

For: complex nested.

## Error Handling

Framework:
```go
resp.Diagnostics.AddError("Title", "Detail")
resp.Diagnostics.AddWarning(...)
resp.Diagnostics.AddAttributeError(path, "Title", "Detail")
```

Multiple errors accumulated.

## Best Practices

- New: Plugin Framework
- Existing: migrate incrementally via mux
- Strong typing throughout
- Acceptance tests
- Documentation
- Semver

## Common Mistakes

- Mix without mux
- Schema mismatches
- Missing plan modifiers (replace not triggered)
- No validators (bad input)
- Sensitive fields not flagged

## Sample Repo

```
provider/
├── main.go
├── internal/
│   └── provider/
│       ├── provider.go
│       ├── widget_resource.go
│       └── widget_data_source.go
├── examples/
├── docs/
├── go.mod
└── Makefile
```

Standard layout.

## Quick Refs

```go
// Plugin Framework imports
"github.com/hashicorp/terraform-plugin-framework/resource"
"github.com/hashicorp/terraform-plugin-framework/resource/schema"
"github.com/hashicorp/terraform-plugin-framework/types"

// SDK v2 imports
"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
```

## Interview Prep

**Senior**: "SDK v2 vs Plugin Framework."

**Staff**: "Custom provider migration strategy."

## Next Topic

→ Move to [L10/C07 — Pulumi & CDK](../C07/README.md)
