# L13/C06/T03 — Pod Security Standards (PSS)

## Learning Objectives

- Apply Pod Security Standards
- Enforce per namespace

## Pod Security Standards

Replaces PodSecurityPolicy (PSP, removed 1.25).

Three profiles:
- **Privileged**: unrestricted (root, host access)
- **Baseline**: minimally restrictive; prevents known privilege escalations
- **Restricted**: heavily restricted; current best practices

## Profiles

### Privileged
No restrictions. For:
- System workloads (CNI, CSI agents)
- Cluster components

### Baseline
Prevents:
- Privileged containers
- Most hostPath mounts
- Host namespace sharing (hostNetwork, hostPID, hostIPC)
- Most capabilities (only safe ones)

Allows:
- Some volumes (configMap, secret, emptyDir, PVC)
- Running as any user
- AppArmor / SELinux defaults

For: standard application workloads.

### Restricted
Strict modern practices:
- runAsNonRoot
- runAsUser non-zero
- All capabilities dropped (except NET_BIND_SERVICE)
- seccompProfile: RuntimeDefault
- No allowPrivilegeEscalation
- ReadOnlyRootFilesystem (often)

For: hardened security workloads.

## Pod Security Admission

Built-in admission controller; no install:
- Per-namespace labels
- Three modes: enforce, audit, warn

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Modes

### enforce
Block pods violating profile. Hard rejection.

### audit
Allow but log violation in audit log.

### warn
Allow but return warning to user on apply.

Combined: enforce blocks; audit/warn at higher profile reveal future issues.

## Per-Namespace Defaults

Cluster-wide default via admission config:
```yaml
apiVersion: pod-security.admission.config.k8s.io/v1
kind: PodSecurityConfiguration
defaults:
  enforce: "baseline"
  audit: "restricted"
  warn: "restricted"
exemptions:
  namespaces: ["kube-system"]
```

Per-namespace label overrides default.

## Privileged Example (Don't Do)

```yaml
spec:
  containers:
  - name: bad
    image: nginx
    securityContext:
      privileged: true            # privileged = NO baseline
      capabilities:
        add: ["SYS_ADMIN"]          # NO baseline
      runAsUser: 0                  # baseline OK; restricted NO
```

Baseline: rejects.
Restricted: rejects.

## Baseline-Compliant

```yaml
spec:
  containers:
  - name: app
    image: nginx
    securityContext:
      privileged: false           # OK
      allowPrivilegeEscalation: true   # baseline OK
      runAsUser: 0                # baseline OK
```

## Restricted-Compliant

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]   # only if needed
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: pid
      mountPath: /var/run
  volumes:
  - name: cache
    emptyDir: {}
  - name: pid
    emptyDir: {}
```

ReadOnlyRootFS + writable mounts for required write paths.

## Rolling Out PSS

Phased:
1. Audit/warn baseline cluster-wide
2. Fix violations
3. Enforce baseline default
4. Audit/warn restricted
5. Fix violations
6. Enforce restricted (for new ns)

## Exempt Namespaces

Some need privileged:
- kube-system
- ingress-nginx
- monitoring (some agents)

Exempt or use privileged profile.

## Per-Workload Override (Not Possible)

PSS is per-namespace. Can't override per pod.

For mixed needs: separate namespaces.

## Migration from PSP

PSP (removed):
```yaml
kind: PodSecurityPolicy
spec:
  privileged: false
  ...
```

PSS is simpler; per-namespace label.

Migration tools:
- `kube-psp-advisor`: convert PSP to PSS
- Manual: audit; pick profile per namespace

## OPA/Kyverno for Complex

PSS is built-in but limited.

For custom rules:
- Block specific images
- Force specific labels
- Custom validations

Use OPA Gatekeeper or Kyverno (covered T06).

## Testing

Dry-run apply:
```bash
kubectl apply -f pod.yaml --dry-run=server
# Warning: pod violates Pod Security restricted:0.0
```

For: catch before deploy.

## SecurityContext

Pod and container levels:

### Pod Level
```yaml
spec:
  securityContext:
    runAsUser: 1000
    runAsNonRoot: true
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
    sysctls:
    - name: net.core.somaxconn
      value: "1024"
```

### Container Level
```yaml
containers:
- name: app
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    runAsUser: 1000
    capabilities:
      drop: ["ALL"]
      add: ["NET_BIND_SERVICE"]
```

Container overrides pod where both set.

## Capabilities

Linux capabilities:
- NET_ADMIN: network
- SYS_ADMIN: many; powerful (avoid)
- NET_BIND_SERVICE: bind to ports <1024
- CHOWN: change file ownership
- SETUID, SETGID

Best: drop ALL, add only needed.

## seccompProfile

Restricts syscalls:
- RuntimeDefault: container runtime default
- Localhost: custom seccomp profile on node
- Unconfined: no restriction (NOT recommended)

```yaml
seccompProfile:
  type: RuntimeDefault
```

Restricted profile requires this.

## AppArmor / SELinux

Mandatory access control:
```yaml
annotations:
  container.apparmor.security.beta.kubernetes.io/app: runtime/default
```

Or SELinux:
```yaml
seLinuxOptions:
  level: "s0:c123,c456"
```

For: defense in depth.

## ReadOnly Root FS

```yaml
readOnlyRootFilesystem: true
```

Container can't write to /. Need writable mounts for:
- /tmp
- App cache dirs
- Logs (if not stdout)

For: limit malware persistence.

## runAsNonRoot

```yaml
runAsNonRoot: true
runAsUser: 1000
```

Container fails if image runs as root.

For: avoid root processes.

## Image Without Root

In Dockerfile:
```dockerfile
RUN useradd -u 1000 appuser
USER 1000
```

Or use distroless:
```dockerfile
FROM gcr.io/distroless/static:nonroot
```

## Privileged vs Capabilities

Privileged: everything (full root).
Capabilities: specific powers.

Always prefer specific capabilities.

## Common Workloads Needing Privileged

- CSI node plugin (mounts)
- CNI agent (iptables)
- Monitoring agents (sometimes)
- Security tools (Falco)

Restrict to specific namespaces with privileged profile.

## PSS Violations

```
Error: pod "my-pod" was rejected:
  violates PodSecurity "restricted:latest":
  privileged (container "app" must not set securityContext.privileged=true),
  allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false)
```

Adjust pod spec or namespace profile.

## Best Practices

- Baseline minimum for all namespaces
- Restricted for new workloads
- Exempt only what's necessary
- Use distroless / non-root images
- Drop ALL capabilities; add specific
- ReadOnlyRootFS
- runAsNonRoot

## Anti-Patterns

- Privileged everywhere (no defense)
- Running as root for "convenience"
- All capabilities granted
- No seccomp
- No PSS labels

## Common Mistakes

- Profile too strict (legitimate apps fail)
- No phased rollout (sudden chaos)
- Missing version label (apply default)
- Forgetting volumes for ReadOnlyRootFS

## Quick Refs

```bash
# Label namespace
kubectl label namespace prod \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest

# Test pod (server dry-run)
kubectl apply -f pod.yaml --dry-run=server

# Check namespace profile
kubectl get ns prod -o jsonpath='{.metadata.labels}'
```

## Interview Prep

**Junior**: "Why not run as root."

**Mid**: "PSS profiles."

**Senior**: "PSP → PSS migration."

**Staff**: "Cluster-wide hardening rollout."

## Next Topic

→ [T04 — NetworkPolicies (Security Focus)](T04-NetworkPolicies-Security.md)
