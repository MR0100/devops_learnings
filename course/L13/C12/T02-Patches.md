# L13/C12/T02 — Patches (Strategic Merge, JSON Patch)

## Learning Objectives

- Apply Kustomize patches
- Pick patch type

## Patches

Modify resources in overlays.

Two types:
- **Strategic merge** (default): patch by key; respects K8s semantics
- **JSON Patch** (RFC 6902): explicit operations (add/remove/replace)

## Strategic Merge

Looks like the resource; sets fields:
```yaml
# overlay/prod/replicas-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 10
```

kustomization.yaml:
```yaml
patches:
- path: replicas-patch.yaml
```

Merge sets `spec.replicas` to 10; preserves other fields.

## Identity

Patch must match resource by:
- apiVersion
- kind
- metadata.name (+ namespace if specified)

For: target specific resource.

## Strategic Merge Semantics

K8s-aware:
- List of containers: matched by `name`
- Volumes: by `name`
- Replace vs merge: depends on field

Example:
```yaml
spec:
  template:
    spec:
      containers:
      - name: app           # matches container "app"
        image: my-app:v2    # updates image
        # other fields preserved
```

## Multiple Patches

```yaml
patches:
- path: replicas-patch.yaml
- path: image-patch.yaml
- path: env-patch.yaml
```

Applied in order; cumulative.

## Inline Patch

```yaml
patches:
- target:
    kind: Deployment
    name: my-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
```

JSON Patch inline.

## Target

```yaml
patches:
- target:
    kind: Deployment
    name: my-app
    namespace: prod
    labelSelector: app=web
  path: patch.yaml
```

Match by various.

## JSON Patch (RFC 6902)

Operations:
- `add`: add path
- `remove`: remove path
- `replace`: replace path
- `move`: move path
- `copy`: copy path
- `test`: assert value

```yaml
patches:
- target:
    kind: Deployment
    name: my-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
    - op: add
      path: /spec/template/spec/containers/0/env/-
      value:
        name: NEW_VAR
        value: hello
    - op: remove
      path: /spec/template/spec/containers/0/livenessProbe
```

## When JSON Patch

- Add/remove list items
- Conditional changes
- Precise targeting
- Path-based operations

Example: add env var to first container:
```yaml
- op: add
  path: /spec/template/spec/containers/0/env/-
  value: {name: X, value: y}
```

(`-` means append to list)

## When Strategic Merge

- Most cases
- Simpler syntax
- K8s-aware merging
- Match containers by name (not index)

## Comparing

```yaml
# Strategic Merge
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            cpu: 2
```

Updates app container's CPU limit.

```yaml
# JSON Patch
- op: replace
  path: /spec/template/spec/containers/0/resources/limits/cpu
  value: "2"
```

Same result; positional.

If container order changes: JSON Patch breaks.

## Patch Multiple Resources

```yaml
patches:
- target:
    kind: Deployment
    labelSelector: app=web
  patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: ignored
    spec:
      replicas: 5
```

LabelSelector matches multiple.

## Patches vs configMapGenerator

For ConfigMap changes:
- Patch: edit existing ConfigMap
- Generator: create new one with hashed name

Generator preferred for ConfigMap content changes (auto-triggers rollout).

## Common Patches

### Add Annotations
```yaml
patches:
- path: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
      annotations:
        team: platform
```

### Increase Resources
```yaml
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      template:
        spec:
          containers:
          - name: app
            resources:
              limits:
                memory: 1Gi
```

### Add Volume
```yaml
patches:
- patch: |-
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      template:
        spec:
          volumes:
          - name: extra
            emptyDir: {}
          containers:
          - name: app
            volumeMounts:
            - name: extra
              mountPath: /extra
```

### Disable Liveness (Dev)
```yaml
patches:
- target:
    kind: Deployment
    name: my-app
  patch: |-
    - op: remove
      path: /spec/template/spec/containers/0/livenessProbe
```

## Delete Resource

```yaml
patches:
- target:
    kind: Service
    name: unwanted
  patch: |-
    $patch: delete
```

Removes from output.

## Replace List

Strategic merge usually merges lists. To replace:
```yaml
spec:
  template:
    spec:
      containers:
      - $patch: replace
      - name: app
        image: ...
```

Whole list replaced.

## Strategic Merge Deep Dive

Specific behaviors:
- env: merge by name (you can add/update; original preserved)
- ports: merge by containerPort
- volumes: merge by name

Test patches; check output:
```bash
kustomize build ./overlays/prod
```

## Patches vs Replacement

Replacement (newer):
```yaml
replacements:
- source:
    kind: ConfigMap
    name: app-config
    fieldPath: data.replicas
  targets:
  - select:
      kind: Deployment
      name: my-app
    fieldPaths:
    - spec.replicas
```

Set Deployment.replicas from ConfigMap.data.replicas.

For: linking related fields.

## Anti-Patterns

- Inline JSON Patch when strategic merge works
- Patching things that should be values
- Many tiny patches (consolidate)

## Best Practices

- Strategic merge by default
- JSON Patch for list operations
- Group related changes
- Keep patches focused
- Test with kustomize build

## Patches Path

Relative to kustomization.yaml.

For: organized files.

## Common Mistakes

- Wrong path in JSON Patch
- Container name mismatch (strategic merge can't find)
- Forgot apiVersion/kind in strategic merge patch
- Patches that don't apply (silent failure)

## Inspection

```bash
# Show output
kustomize build ./overlays/prod

# Diff vs cluster
kubectl diff -k ./overlays/prod

# Render specific resource
kustomize build ./overlays/prod | yq 'select(.metadata.name == "my-app")'
```

## Tools

- yq: query rendered YAML
- diff: vs base
- ArgoCD: visualize patches

## Quick Refs

```yaml
# Strategic Merge
patches:
- path: patch.yaml

# Inline JSON Patch
patches:
- target:
    kind: Deployment
    name: my-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 5
```

## Interview Prep

**Mid**: "Strategic merge vs JSON Patch."

**Senior**: "Patch design pattern."

**Staff**: "Multi-env patches at scale."

## Next Topic

→ [T03 — Generators](T03-Generators.md)
