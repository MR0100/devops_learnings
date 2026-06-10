# L13/C06/T06 — OPA Gatekeeper & Kyverno

## Learning Objectives

- Enforce policy beyond PSS
- Choose Gatekeeper vs Kyverno

## Why Policy Engines

Pod Security Standards: built-in but limited.

Custom needs:
- Require labels on resources
- Block specific images (not from approved registry)
- Enforce resource limits
- Require liveness/readiness probes
- Restrict namespaces / annotations
- Custom validations

Solution: Policy engines via admission webhooks.

## Architecture

```
kubectl apply
↓
API Server
↓
Validating Admission Webhook → Policy Engine
↓
Accept / Reject
↓
etcd
```

Pod creation can be blocked by policy.

## OPA Gatekeeper

Built on Open Policy Agent (Rego language):
```bash
helm install gatekeeper open-policy-agent/gatekeeper -n gatekeeper-system --create-namespace
```

Two CRDs:
- **ConstraintTemplate**: defines rule (Rego)
- **Constraint**: instance applying rule

## ConstraintTemplate

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      
      violation[{"msg": msg}] {
        required := input.parameters.labels
        provided := input.review.object.metadata.labels
        missing := required[_]
        not provided[missing]
        msg := sprintf("Missing label: %v", [missing])
      }
```

## Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ns-must-have-team
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels: ["team", "env"]
```

Apply: namespaces must have `team` + `env` labels.

## Common Policies

### Disallow Privileged
```rego
violation[{"msg": msg}] {
  c := input.review.object.spec.containers[_]
  c.securityContext.privileged == true
  msg := "Privileged not allowed"
}
```

### Require Image From Approved Registry
```rego
violation[{"msg": msg}] {
  c := input.review.object.spec.containers[_]
  not startswith(c.image, "myregistry.com/")
  msg := sprintf("Image %v not from approved registry", [c.image])
}
```

### Require Resource Limits
```rego
violation[{"msg": msg}] {
  c := input.review.object.spec.containers[_]
  not c.resources.limits.cpu
  msg := "CPU limit required"
}
```

## Kyverno

YAML-based (no Rego):
```bash
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

## Kyverno Policy

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-team-label
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Pod must have team label"
      pattern:
        metadata:
          labels:
            team: "?*"
```

YAML pattern matching. Simpler than Rego for many cases.

## Kyverno Capabilities

Three types of rules:
- **Validate**: block bad config
- **Mutate**: auto-fix (add labels, etc.)
- **Generate**: create related resources

```yaml
# Mutate
rules:
- name: add-default-labels
  match:
    any:
    - resources:
        kinds: [Pod]
  mutate:
    patchStrategicMerge:
      metadata:
        labels:
          managed-by: kyverno
```

```yaml
# Generate
rules:
- name: add-default-networkpolicy
  match:
    any:
    - resources:
        kinds: [Namespace]
  generate:
    kind: NetworkPolicy
    name: default-deny
    namespace: "{{request.object.metadata.name}}"
    data:
      spec:
        podSelector: {}
        policyTypes: [Ingress, Egress]
```

## Gatekeeper vs Kyverno

| | Gatekeeper | Kyverno |
|---|---|---|
| Language | Rego (steep curve) | YAML (familiar) |
| Validate | Yes | Yes |
| Mutate | Limited | Yes |
| Generate | No | Yes |
| OPA ecosystem | Yes | No |
| Maturity | Mature | Mature |
| Performance | Good | Good |
| K8s native feel | Less | More |

For most K8s teams: Kyverno (simpler).
For OPA elsewhere (Envoy, Terraform): Gatekeeper consistency.

## Audit vs Enforce

Both engines support:
- **Audit/Warn**: log violations
- **Enforce**: block

For rollout:
1. Audit mode; collect violations
2. Fix issues
3. Switch to enforce

## Common Policies (Both)

### Block Latest Tag
Reject images with `:latest` (mutability risk).

### Require Probes
Liveness + readiness mandatory.

### Disallow HostPath
Prevent volume mounting host filesystem.

### Approved Registries
Images only from allowed registries.

### Label Requirements
Owner, team, env labels mandatory.

### Resource Limits
CPU/memory limits required.

### Replicas > 1
For prod: prevent single-replica deployments.

### NetworkPolicy Per Namespace
Auto-generate default-deny.

## Background Scanning

Both engines can scan existing resources:
- Identify violations (without blocking new)
- Reports
- Compliance dashboards

## Policy Reports

```bash
kubectl get policyreport -A
kubectl get clusterpolicyreport
```

Per-policy violations.

## Exclusions

Some resources exempt:
```yaml
match:
  excludedNamespaces:
  - kube-system
  - gatekeeper-system
```

System workloads often need privileges.

## Real-World Examples

### CIS Kubernetes Benchmark
Policies mapping CIS items:
- No privileged containers
- No host namespaces
- No allowPrivilegeEscalation
- etc.

Pre-built policies available.

### NSA Hardening Guide
NSA + CISA published K8s hardening. Map to policies.

## Performance Impact

Each API request: webhook call → policy eval.
- Latency: ms (cached)
- Throughput: thousands/sec

For huge clusters: monitor webhook latency.

Gatekeeper / Kyverno scale horizontally.

## Failure Modes

Webhook down:
- Default: fail-open (allow everything; security risk)
- Configurable: fail-closed (block everything; availability risk)

Best practice: fail-closed for security, audit before enforce.

## Webhook Timeout

```yaml
failurePolicy: Fail   # block if webhook timeout
timeoutSeconds: 5
```

Tune carefully.

## Image Signing Verification

Both engines can verify image signatures:
- Cosign-signed images
- Sigstore verification

```yaml
# Kyverno
rules:
- name: verify-signature
  match: ...
  verifyImages:
  - imageReferences:
    - "ghcr.io/myorg/*"
    attestors:
    - entries:
      - keys:
          publicKeys: |
            -----BEGIN PUBLIC KEY-----
            ...
```

For: supply chain security.

## Best Practices

- Start with audit mode
- Gradual rollout
- Document each policy's why
- Test in staging
- Exempt system namespaces
- Monitor webhook latency
- Backup policies (Git)
- CI policy testing

## Common Mistakes

- Enforce mode without audit
- Policy too strict (legitimate apps fail)
- No exemptions (kube-system fails)
- Webhook fail-open (security gap)
- Policies in cluster only (no Git)

## When PSS Suffices

PSS for basic pod-level. Engine for:
- Custom labels
- Image registries
- Resource standards
- Cross-resource rules

Combine: PSS + engine.

## Tooling

- **Konstraint**: validate Rego policies
- **Polaris**: best practices linter
- **Kubescape**: security scanner
- **Datree**: CLI policy check
- **kube-score**: pre-deploy scoring

## CI Integration

```yaml
# Pre-merge: validate manifests against policy
- name: Validate
  run: |
    kyverno test ./policies
    conftest test --policy ./policies ./manifests
```

Catch violations before deploy.

## Policy Catalog

Both engines have catalogs:
- Gatekeeper Library: github.com/open-policy-agent/gatekeeper-library
- Kyverno Policies: github.com/kyverno/policies

Battle-tested; start with these.

## Multi-Cluster

Policy applied per cluster. For consistency:
- Argo CD syncs policies from Git
- Per-cluster overrides if needed

## Auditing

Run periodically:
- Generate compliance report
- Track violations over time
- Fix to clean state

For SOC / compliance audits.

## Quick Refs

```bash
# Gatekeeper
kubectl get constrainttemplate
kubectl get constraints.constraints.gatekeeper.sh -A

# Kyverno
kubectl get clusterpolicy
kubectl get policyreport -A
kubectl get cpolr   # short for clusterpolicyreport

# Test
kyverno test ./policies
```

## Interview Prep

**Mid**: "Why policy engine in K8s."

**Senior**: "OPA Gatekeeper vs Kyverno."

**Staff**: "Cluster policy program design."

## Next Topic

→ [T07 — Image Pull Secrets, Image Policy](T07-Image-Policy.md)
