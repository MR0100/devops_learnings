# L13/C20/T01 — Cluster Hardening (CIS)

## Learning Objectives

- Apply CIS Benchmark
- Use kube-bench

## CIS Kubernetes Benchmark

Center for Internet Security; security baseline for K8s.

Tests:
- Control plane components
- Node configurations
- Policies
- Network
- etc.

Levels:
- Level 1: minimum baseline
- Level 2: defense in depth

## kube-bench

```bash
docker run --rm -v "$(pwd):/host" aquasec/kube-bench:latest run --targets=master,node,etcd,policies
```

Or as Job in cluster:
```bash
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench
```

Output:
```
[INFO] 1 Control Plane Security Configuration
[PASS] 1.1.1 Ensure that the API server pod specification file permissions are 644 or more restrictive
[FAIL] 1.1.2 Ensure that the API server pod specification file ownership is set to root:root
[WARN] 1.2.1 Ensure that the --anonymous-auth argument is set to false (Manual)
```

Per check: passes, fails, manual.

## Common Findings

### API Server Auth
- Anonymous auth disabled
- Strong auth (cert, OIDC)
- Audit log enabled

### Kubelet
- Authentication on (not anonymous)
- Authorization mode webhook
- Read-only port disabled

### etcd
- Client certs required
- Peer certs required
- Data dir permissions

### Network
- NetworkPolicy enabled
- Pod-to-pod default deny

### RBAC
- No wildcard cluster-admin bindings
- Specific roles

### Policies
- Pod Security Standards
- Network Policies
- Resource quotas

## EKS / GKE / AKS

Provider handles control plane CIS compliance. Your job: workload + namespace.

```bash
# EKS specific
kube-bench run --targets node,policies --benchmark eks-1.5.0
```

Per cloud benchmark.

## kube-hunter

Penetration testing:
```bash
docker run --rm aquasec/kube-hunter
```

Scans for known K8s vulnerabilities.

Modes:
- Network scan
- Cluster (in-cluster pod)
- Active probe (exploit attempts)

## Falco

Runtime security:
```bash
helm install falco falcosecurity/falco
```

Watches syscalls; alerts on suspicious:
- Shell in container
- Privileged access
- File modifications
- Network anomalies

## Pod Security

Pod Security Standards (covered C06/T03):
- Privileged
- Baseline
- Restricted

For prod: restricted minimum.

## Image Security

- Sign images (Cosign)
- Verify signatures (Sigstore Policy Controller)
- Vulnerability scan (Trivy, Snyk)
- Block known-bad

```yaml
# Kyverno
- name: require-signed
  match: ...
  verifyImages:
  - imageReferences: ['myregistry/*']
    attestors:
    - entries:
      - keyless:
          subject: 'https://github.com/myorg/.*'
```

## Secrets Encryption

etcd encryption at rest (covered C06/T05).

Plus:
- External Secrets Operator
- Vault
- Sealed Secrets (Git-storable)

## Network Hardening

- NetworkPolicy default deny
- Block egress to metadata IP
- mTLS via mesh
- Restrict cross-namespace

## Audit Logging

API server audit log:
```yaml
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods/exec", "pods/portforward"]
```

For: who did what, when.

Ship to SIEM (Splunk, Datadog).

## RBAC Audit

```bash
# Find cluster-admin bindings
kubectl get clusterrolebinding -o json | jq '.items[] | select(.roleRef.name=="cluster-admin")'

# Wide permissions
kubectl who-can '*' '*'
```

Reduce to minimum.

## Defense in Depth

Layers:
1. CIS Benchmark (control plane)
2. PSS (pod security)
3. NetworkPolicy (network)
4. Image signing (supply chain)
5. Runtime detection (Falco)
6. RBAC (access)
7. Encryption at rest
8. Audit logging

Each catches what others miss.

## Continuous Compliance

Run kube-bench regularly:
- CronJob hourly/daily
- Alert on regression
- Report to dashboard

For audit evidence.

## Common Hardening

For self-managed:
```yaml
# kube-apiserver flags
- --anonymous-auth=false
- --audit-log-path=/var/log/audit.log
- --audit-log-maxage=30
- --enable-admission-plugins=NodeRestriction,PodSecurity
- --encryption-provider-config=/etc/kubernetes/enc/enc.yaml
- --tls-min-version=VersionTLS12
```

```yaml
# kubelet config
authentication:
  anonymous:
    enabled: false
authorization:
  mode: Webhook
readOnlyPort: 0
protectKernelDefaults: true
```

## CIS Profiles

CIS releases:
- General K8s benchmark
- EKS benchmark
- GKE benchmark
- AKS benchmark

Per provider; check applicable controls.

## Tooling Stack

Common:
- kube-bench: CIS checks
- kube-hunter: penetration
- Falco: runtime
- Trivy: image scan
- OPA Gatekeeper / Kyverno: policy
- cert-manager: certs
- External Secrets: secrets

For full security posture.

## Compliance Frameworks

CIS aligns with:
- PCI DSS
- HIPAA
- SOC 2
- ISO 27001

Map controls; provide evidence.

## Best Practices

- Run kube-bench in CI
- Fix all FAILs, review WARNs
- Audit log enabled
- Encryption at rest
- NetworkPolicy default deny
- PSS restricted
- Image signing
- Runtime detection
- Regular scans
- Documented exceptions

## Common Mistakes

- Default install accepted (insecure)
- Audit log off (no investigation)
- Wide RBAC
- No NetworkPolicy
- Unsigned images
- No runtime detection

## kube-bench Job Yaml

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: kube-bench
spec:
  template:
    spec:
      hostPID: true
      containers:
      - name: kube-bench
        image: aquasec/kube-bench:latest
        command: ["kube-bench"]
        volumeMounts:
        - name: var-lib-etcd
          mountPath: /var/lib/etcd
        - name: var-lib-kubelet
          mountPath: /var/lib/kubelet
        - name: etc-systemd
          mountPath: /etc/systemd
        - name: etc-kubernetes
          mountPath: /etc/kubernetes
        - name: usr-bin
          mountPath: /usr/local/mount-from-host/bin
      restartPolicy: Never
      volumes:
      ...
```

Run periodically; report findings.

## EKS Hardening

EKS-specific:
- API server endpoint private (or restricted CIDR)
- IRSA over node IAM role
- Secrets encryption (KMS)
- Audit log to CloudWatch
- VPC CNI security groups
- Bottlerocket nodes (smaller surface)

## Quick Refs

```bash
# kube-bench
docker run --rm -v /:/host aquasec/kube-bench:latest run

# kube-hunter
docker run --rm aquasec/kube-hunter

# Falco
helm install falco falcosecurity/falco

# RBAC review
kubectl get clusterrolebinding
kubectl who-can ...
```

## Interview Prep

**Mid**: "CIS Benchmark."

**Senior**: "Cluster hardening checklist."

**Staff**: "Compliance program for K8s."

## Next Topic

→ [T02 — Disaster Recovery](T02-DR.md)
