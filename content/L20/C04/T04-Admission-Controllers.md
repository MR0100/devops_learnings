# L20/C04/T04 — Admission Controllers

## Learning Objectives

- Use admission controllers
- Enforce policy

## Admission Controller

K8s component intercepts API requests:
- Before write to etcd
- Validate (allow/deny)
- Mutate (modify)

For: policy enforcement.

## Built-in

K8s has ~30:
- NamespaceLifecycle
- LimitRanger
- ServiceAccount
- PodSecurity
- ResourceQuota

Enabled in apiserver config.

## Dynamic (Webhooks)

Custom logic:
- ValidatingWebhookConfiguration
- MutatingWebhookConfiguration

External service called.

## Tools

### OPA Gatekeeper
- Rego policy
- CNCF

### Kyverno
- YAML policy
- K8s-native

### Connaisseur
- Image signature verify

### Polaris
- Best-practice checker

## Kyverno Example

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-labels
    match:
      any:
      - resources:
          kinds: [Deployment]
    validate:
      message: "Deployment must have 'app' and 'env' labels"
      pattern:
        metadata:
          labels:
            app: "?*"
            env: "?*"
```

Block deployments without labels.

## OPA Gatekeeper Example

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-labels
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels: ["app", "env"]
```

```rego
package k8srequiredlabels

violation[{"msg": msg}] {
  required := input.parameters.labels
  missing := required[_]
  not input.review.object.metadata.labels[missing]
  msg := sprintf("Missing label: %v", [missing])
}
```

## Image Signature

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-image-signature
spec:
  validationFailureAction: Enforce
  rules:
  - name: verify-image
    match:
      any:
      - resources:
          kinds: [Pod]
    verifyImages:
    - imageReferences:
      - "registry/*"
      attestors:
      - entries:
        - keyless:
            issuer: "https://token.actions.githubusercontent.com"
            subject: "https://github.com/myorg/*"
```

Only signed images.

## Network Policy

Per-namespace:
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-all-default
spec:
  rules:
  - name: deny-all
    match:
      any:
      - resources:
          kinds: [Namespace]
    generate:
      kind: NetworkPolicy
      data:
        spec:
          podSelector: {}
          policyTypes: [Ingress, Egress]
```

Auto-generate.

## Resource Limits

```yaml
- name: require-resources
  validate:
    message: "Resources required"
    pattern:
      spec:
        containers:
        - resources:
            requests:
              cpu: "?*"
              memory: "?*"
            limits:
              cpu: "?*"
              memory: "?*"
```

## Privileged Container Block

```yaml
- name: no-privileged
  validate:
    message: "Privileged containers not allowed"
    pattern:
      spec:
        =(containers):
        - =(securityContext):
            =(privileged): false
```

## RunAsNonRoot

```yaml
- name: run-as-non-root
  validate:
    message: "Must run as non-root"
    pattern:
      spec:
        containers:
        - securityContext:
            runAsNonRoot: true
```

## Pod Security Standards

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

Built-in:
- privileged (none)
- baseline (minimal)
- restricted (most secure)

## Audit Mode

```yaml
validationFailureAction: Audit   # log only
```

Pilot before Enforce.

## Mutating

Auto-modify:
- Add labels
- Add sidecars
- Set defaults

Use carefully (changes behavior).

## Performance

Webhooks add latency:
- < 100 ms per request
- Could block API if slow

For: ensure HA.

## OPA vs Kyverno

| | OPA Gatekeeper | Kyverno |
|---|---|---|
| Language | Rego | YAML |
| Learning | steep | easier |
| Power | very high | high |
| Mutating | limited | yes |
| Generate | no | yes |

For: Kyverno often easier.

## Best Practices

- Audit mode first
- Per-namespace policies
- Test policy in non-prod
- Document each policy
- HA webhook
- Performance test

## Common Mistakes

- Enforce immediately (breaks)
- Single-replica webhook
- Heavy logic (slow)
- No audit (silent failure)

## Quick Refs

```yaml
# Kyverno
kind: ClusterPolicy
spec:
  validationFailureAction: Enforce | Audit
  rules:
    - validate: { pattern: ... }
    - mutate: { patchStrategicMerge: ... }
    - generate: { kind: ..., data: ... }
    - verifyImages: { ... }
```

```bash
# Install Kyverno
helm install kyverno kyverno/kyverno

# Install OPA Gatekeeper
helm install gatekeeper gatekeeper/gatekeeper
```

## Interview Prep

**Junior**: "What is a Kubernetes admission controller?" — A hook that intercepts API requests after authN/authZ but before persistence, so it can validate or mutate objects (e.g. reject privileged pods, inject sidecars) as they're created.

**Mid**: "Validating vs mutating admission — what's the difference?" — Mutating webhooks change the object (add defaults, sidecars, labels) and run first; validating webhooks only accept or reject it, and run last so they see the final mutated object.

**Senior**: "Kyverno vs OPA/Gatekeeper — how do you choose?" — Kyverno writes policies as native YAML (lower learning curve, K8s-native), while OPA/Gatekeeper uses Rego (more expressive, reusable across non-K8s systems); choose Kyverno for simplicity and Gatekeeper when you need Rego's power or already standardize on OPA.

**Staff**: "How do you roll out admission policy at scale safely?" — Start in audit/warn mode to measure impact, fail-open vs fail-closed deliberately (a down webhook shouldn't block all deploys unless intended), use exclusions for system namespaces, and ship policies as code with the same review/test/canary discipline as application changes — and prefer in-tree ValidatingAdmissionPolicy (CEL) for simple rules to avoid an extra webhook dependency.

## Next Topic

→ Move to [L20/C05 — Secrets Management](../C05/README.md)
