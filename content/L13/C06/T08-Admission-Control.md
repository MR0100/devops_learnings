# L13/C06/T08 — Admission Control (Webhooks & ValidatingAdmissionPolicy / CEL)

## Learning Objectives

- Place admission control in the apiserver request pipeline
- Distinguish mutating vs validating admission, and webhooks vs in-process plugins
- Write and reason about MutatingWebhookConfiguration / ValidatingWebhookConfiguration
- Use ValidatingAdmissionPolicy with CEL (GA 1.30) as a webhook-free alternative
- Configure failure policy, scope, and ordering safely

## Where Admission Control Sits

Admission control runs **inside the apiserver**, after authentication and authorization but **before the object is persisted to etcd**:

```
request → authentication → authorization (RBAC) → ADMISSION → schema validate/default → etcd
                                                     │
                                  ┌──────────────────┴──────────────────┐
                                  ▼                                      ▼
                          1. Mutating admission              2. Validating admission
                          (may change the object)            (accept / reject only)
```

- **Mutating** runs first and may rewrite the object (inject a sidecar, add defaults, set labels).
- **Validating** runs second and can only **accept or reject** — it never mutates.
- Authn/authz answer *"who are you and may you do this?"*; admission answers *"is this specific object allowed, and should we adjust it?"*

This is the enforcement point for almost every cluster guardrail: Pod Security Standards (T03), OPA Gatekeeper / Kyverno (T06), image-policy controllers (T07), and Istio's sidecar injection all plug in here.

## Two Kinds of Admission Plugins

**1. In-process (compiled-in) plugins** — built into the apiserver, toggled with `--enable-admission-plugins` / `--disable-admission-plugins`. Examples: `NamespaceLifecycle`, `LimitRanger`, `ResourceQuota`, `ServiceAccount`, `DefaultStorageClass`, `PodSecurity` (which enforces Pod Security Standards), `MutatingAdmissionWebhook`, `ValidatingAdmissionWebhook`. You can't add your own logic here — but two of these plugins are the gateways to *your* logic (the webhook plugins).

**2. Dynamic admission** — your own logic, added at runtime without recompiling the apiserver:
- **Admission webhooks** (mutating + validating) — the apiserver calls out to an HTTP service you run.
- **ValidatingAdmissionPolicy** — CEL expressions evaluated **in-process** by the apiserver, no external service (GA 1.30).
- **MutatingAdmissionPolicy** — CEL-based mutation, in-process (newer; alpha/beta — confirm the gate for your version).

## Admission Webhooks

The apiserver POSTs an `AdmissionReview` to your webhook service and applies the `AdmissionResponse` it gets back.

### ValidatingWebhookConfiguration

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: require-resource-limits
webhooks:
- name: limits.example.com
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Fail              # Fail = closed; Ignore = open (see below)
  timeoutSeconds: 5
  matchPolicy: Equivalent
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
    scope: "Namespaced"
  namespaceSelector:               # skip system namespaces
    matchExpressions:
    - key: kubernetes.io/metadata.name
      operator: NotIn
      values: ["kube-system"]
  clientConfig:
    service:
      name: limits-webhook
      namespace: policy
      path: /validate
    caBundle: <base64 CA cert>
```

### MutatingWebhookConfiguration

Same shape, but the response carries a base64 JSON Patch in `patch`/`patchType: JSONPatch`. This is how Istio injects an Envoy sidecar and how Vault Agent injection works.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
- name: inject.example.com
  admissionReviewVersions: ["v1"]
  sideEffects: None
  reinvocationPolicy: IfNeeded     # re-run if a later webhook changes the object
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  clientConfig:
    service: { name: injector, namespace: mesh, path: /mutate }
    caBundle: <base64 CA cert>
```

### failurePolicy — the most important knob

- **`Fail` (fail-closed)**: if the webhook is down/slow, the request is **rejected**. Safer for security policy, but if the webhook backing *Pod* admission goes down with `Fail`, you can't create Pods anywhere it matches — a cluster-wide outage.
- **`Ignore` (fail-open)**: if the webhook is unreachable, the request is **allowed**. Safer for availability, but a down security webhook silently stops enforcing.

Rule of thumb: scope webhooks tightly (`namespaceSelector`/`objectSelector`), exclude `kube-system`, set a short `timeoutSeconds`, and **never** let a `Fail`-policy webhook match its own namespace or core control-plane objects.

## ValidatingAdmissionPolicy (CEL, GA 1.30)

A webhook-free way to validate. You write **CEL expressions** evaluated in-process by the apiserver — no service to run, no certs to rotate, no extra network hop, no fail-open/closed availability cliff.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-cpu-limits
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
    - apiGroups: ["apps"]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["deployments"]
  validations:
  - expression: >
      object.spec.template.spec.containers.all(c,
        has(c.resources.limits) && has(c.resources.limits.cpu))
    message: "every container must set a CPU limit"
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: require-cpu-limits-binding
spec:
  policyName: require-cpu-limits
  validationActions: ["Deny"]      # Deny | Warn | Audit
  matchResources:
    namespaceSelector:
      matchExpressions:
      - key: environment
        operator: In
        values: ["prod"]
```

The **Policy** defines the rule; the **Binding** says where it applies and how strictly (`Deny`, `Warn`, or `Audit`). One policy can be bound many times with different scopes — useful for rolling out as `Audit`/`Warn` first, then flipping to `Deny`.

CEL also powers `validations` with `oldObject` (for UPDATE transition rules), `variables`, and `messageExpression`. For *mutation* in CEL there is MutatingAdmissionPolicy (newer; check its feature-gate status for your cluster).

### Webhook vs ValidatingAdmissionPolicy

| | Validating webhook | ValidatingAdmissionPolicy (CEL) |
|---|---|---|
| Where it runs | External service you operate | In-process in the apiserver |
| Availability risk | Down webhook ⇒ fail-open/closed cliff | None (no external dependency) |
| Certs / network hop | Yes (caBundle, mTLS, latency) | No |
| Expressiveness | Arbitrary code (any language) | CEL only (no I/O, no external lookups) |
| Mutation | Yes (mutating webhook) | Validation only (mutation policy is newer) |
| Best for | Complex logic, external data, injection | Simple-to-moderate guardrails, defense in depth |

Guidance: prefer **ValidatingAdmissionPolicy** for straightforward "must have X / must not have Y" rules; reach for a **webhook** when you need arbitrary code, external data, or mutation/injection.

## Ordering & Idempotency

1. All **mutating** webhooks/plugins run (in no guaranteed order across configs). `reinvocationPolicy: IfNeeded` re-invokes a mutating webhook if a *later* one changed the object — so your mutation must be **idempotent** (don't inject the sidecar twice).
2. Then all **validating** webhooks + ValidatingAdmissionPolicies run; any single rejection fails the whole request.

Because mutating order isn't guaranteed, never assume another webhook ran first.

## Failure Modes

| Symptom | Likely cause |
|---|---|
| `failed calling webhook ... context deadline exceeded` | Webhook service down/slow; `failurePolicy: Fail` blocking | 
| Cluster can't create *any* pods after a deploy | A `Fail` webhook matching pods is unreachable (often it matched its own namespace) |
| Policy silently not enforced | `failurePolicy: Ignore` and the webhook is down, or `validationActions: [Audit]` only |
| `x509: certificate signed by unknown authority` | `caBundle` doesn't match the webhook's serving cert (rotation drift) |
| Sidecar injected twice | Non-idempotent mutating webhook + reinvocation |

## Common Mistakes

- **Fail-closed webhook with no exclusions** that matches `kube-system`/its own namespace — bricks the cluster when the webhook pod can't start.
- Long `timeoutSeconds` (default up to 30s) on a pod-admission webhook — every pod create now waits on it; keep it ≤ 5s.
- Forgetting to rotate/update `caBundle` when the webhook serving cert rotates → all calls fail x509.
- Mutating webhook that isn't idempotent under `reinvocationPolicy`.
- Assuming admission webhooks see *every* change — they fire on the operations/resources you match; `DELETE` and subresources need explicit rules.
- Reaching for a webhook for a rule a one-line CEL `ValidatingAdmissionPolicy` would cover (extra service, certs, and an availability dependency for nothing).
- Confusing authorization with admission — RBAC says *whether you may act on the resource*; admission inspects *the object's contents*.

## Best Practices

- Default to **ValidatingAdmissionPolicy (CEL)** for simple/moderate guardrails; use webhooks for complex logic, external data, or mutation.
- Scope tightly: `namespaceSelector` + `objectSelector`, exclude system namespaces.
- Short timeouts (≤ 5s) and an explicit, deliberate `failurePolicy` per webhook.
- Run policy webhooks **HA** (multiple replicas, PDB) so `Fail` doesn't equal "outage."
- Roll out new policies as `Warn`/`Audit` first, observe, then flip to `Deny`/`Fail`.
- Keep `caBundle` automated (cert-manager CA injection / operator) to avoid rotation drift.
- Treat layers as defense in depth: PSA (built-in) + a policy engine/CEL policy + image policy.

## When NOT a Webhook

- Pure "is this config allowed" checks → ValidatingAdmissionPolicy (CEL).
- Enforcing pod hardening baselines → Pod Security Standards (built-in `PodSecurity` plugin, T03).
- Quotas / default limits → built-in `ResourceQuota` / `LimitRanger` plugins.
- Cluster-wide must/never-have catalogs → Gatekeeper / Kyverno (T06), which are themselves admission webhooks with a policy UX.

## Quick Refs

```bash
# What admission webhooks exist?
kubectl get validatingwebhookconfigurations
kubectl get mutatingwebhookconfigurations
kubectl get validatingadmissionpolicies
kubectl get validatingadmissionpolicybindings

# Inspect a webhook's scope + failure policy
kubectl get validatingwebhookconfiguration <name> -o yaml \
  | grep -E 'failurePolicy|timeoutSeconds|name:|namespace:|operations'

# Which in-process plugins are enabled?
kube-apiserver -h | grep enable-admission-plugins   # on a control-plane node
#   --enable-admission-plugins / --disable-admission-plugins

# Test a policy without enforcing it: bind with validationActions: [Audit, Warn]
```

| Concept | One-liner |
|---|---|
| Mutating admission | Rewrites the object (defaults, injection); runs first |
| Validating admission | Accept/reject only; runs second |
| failurePolicy: Fail | Reject if webhook unreachable (fail-closed) |
| failurePolicy: Ignore | Allow if webhook unreachable (fail-open) |
| ValidatingAdmissionPolicy | In-process CEL validation, no external service (GA 1.30) |
| reinvocationPolicy: IfNeeded | Re-run a mutating webhook if a later one mutated |

## Interview Prep

**Junior**: "What is admission control and where does it run?"
- A stage inside the apiserver, after authn/authz and before the object is written to etcd. It can mutate the object (mutating) and then accept or reject it (validating).

**Mid**: "Mutating vs validating admission — order and difference?"
- Mutating runs first and may change the object (defaults, sidecar injection); validating runs second and can only accept/reject, never change. Any single validating rejection fails the whole request.

**Senior**: "A webhook with `failurePolicy: Fail` is down and now nobody can create pods. What happened, and how do you prevent it?"
- Fail-closed means an unreachable webhook rejects matching requests; if it matched pods cluster-wide (and especially its own namespace), pod creation is blocked everywhere — including the webhook's own pods, so it can't recover. Prevent it: exclude system namespaces, scope with selectors, short timeout, run the webhook HA, and consider `Ignore` for non-security policies. Recover: delete/patch the webhook configuration to unblock.

**Senior**: "Why use ValidatingAdmissionPolicy instead of a webhook?"
- It runs in-process as CEL, so there's no external service to operate, no certs to rotate, no extra latency hop, and no fail-open/closed availability cliff. Great for simple/moderate guardrails. You still need a webhook for arbitrary code, external data lookups, or mutation/injection. It went GA in 1.30.

**Staff**: "Design org-wide guardrails for a multi-tenant cluster."
- Layer them: built-in `PodSecurity` (PSA `restricted` per namespace) + `ResourceQuota`/`LimitRanger`; ValidatingAdmissionPolicy (CEL) bound per-environment for cheap, dependency-free rules (require limits, block `:latest`, enforce labels); a policy engine (Kyverno/Gatekeeper) or custom webhook only where you need mutation, generation, or external data. Roll out as Audit→Warn→Deny, scope tightly, exclude system namespaces, run webhooks HA, and automate CA bundle injection.

## Next Topic

→ Move to [L13/C07 — Scheduling & Resources](../C07/README.md)
