# L12/C08/T04 — Runtime Security (Falco, Tetragon)

## Learning Objectives

- Detect runtime threats
- Use Falco / Tetragon

## Why Runtime

Build-time security (scanning, signing) doesn't catch:
- Zero-days
- Misuse
- Compromise post-deploy
- Insider threats

Runtime: monitor + alert.

## Falco

CNCF; detects suspicious behavior:
- syscalls
- container changes
- network anomalies

```bash
helm install falco falcosecurity/falco
```

Pre-configured rules.

## Rules

```yaml
- rule: Shell in Container
  desc: Shell launched in container
  condition: container and shell_procs
  output: "Shell launched (user=%user.name container=%container.name)"
  priority: WARNING
  tags: [container]
```

When shell launched in container: alert.

## Default Rules

- Suspicious processes
- File system access (sensitive paths)
- Network anomalies
- Privileged operations
- Container escapes

## Output

Default: stderr.

For: send to:
- Syslog
- Kafka
- HTTP webhook
- Slack
- Files

```yaml
http_output:
  enabled: true
  url: http://falco-sidekick:2801/
```

## Falco Sidekick

Forwards Falco events to:
- Slack
- Datadog
- Elasticsearch
- Alertmanager
- many more

```bash
helm install falcosidekick falcosecurity/falcosidekick
```

For: integrate alerts.

## Custom Rules

```yaml
- rule: My Custom Rule
  desc: Detect XYZ
  condition: >
    container and 
    proc.name = "suspicious-tool"
  output: "Bad process %proc.cmdline"
  priority: CRITICAL
```

For: specific patterns.

## Tetragon (Cilium)

eBPF-based; deeper visibility:
- Process events
- File access
- Network connections
- Without sidecar

```bash
helm install tetragon cilium/tetragon
```

For: kernel-level observability.

## Tracing Policies

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: file-monitoring
spec:
  kprobes:
  - call: "fd_install"
    syscall: false
    args:
    - index: 0
      type: int
    - index: 1
      type: file
    selectors:
    - matchArgs:
      - index: 1
        operator: Prefix
        values:
        - "/etc/"
```

Trace file opens in /etc/.

## Tetragon vs Falco

| | Falco | Tetragon |
|---|---|---|
| Tech | Kernel module / eBPF | eBPF |
| Performance | Good | Excellent |
| K8s native | Yes | Yes |
| Cilium integration | Separate | Native |
| Maturity | High | Growing |

For Cilium users: Tetragon.
For others: Falco.

## Use Cases

### Shell Detection
Alert when shell launched in pod (often attacker activity).

### Privilege Escalation
sudo / setuid in container.

### Sensitive File Access
/etc/shadow, ~/.ssh/, /var/run/docker.sock.

### Crypto Mining
xmrig, kinsing, hash patterns.

### Reverse Shell
nc / bash redirect to TCP.

## Performance Impact

Falco: ~5-10% CPU overhead (default rules).
Tetragon: eBPF; lower overhead.

For: tune rule complexity if needed.

## Pod Security Standards (Combine)

PSS restrictricts what's possible.
Runtime detects what slips through.

Both: defense in depth.

## SIEM Integration

For prod:
- Falco → Falcosidekick → Splunk / Datadog
- Tetragon → Hubble → backend

Correlated with other signals.

## Common Detections

```
- Container started privileged
- /etc/shadow read
- Modify /etc/passwd
- New executable in container
- Unexpected network connection
- Crypto miner detected
- Shell access
- Reverse shell pattern
```

## Tuning

Default rules: noisy in some envs.

Process:
1. Deploy with default
2. Identify false positives
3. Whitelist or modify rules
4. Reduce noise
5. Real alerts surface

For: actionable alerts.

## False Positives

Common:
- CI/CD running scripts
- Legitimate admin actions
- Service mesh sidecar

Whitelist by:
- Container name
- Namespace
- Process name

## Container Escape

Most attacks try:
- Mount host filesystem
- Modify host
- Access kernel

Runtime tools catch these.

## CSI / Storage Plugins

Privileged containers (CSI, CNI): trusted; whitelist.

## Cloud Provider Integration

- AWS GuardDuty (runtime via EKS data source)
- GCP Cloud SCC
- Azure Defender

For: cloud-managed.

## eBPF Limitations

- Kernel 4.18+ required
- Some distros restrict eBPF

For older: Falco kernel module.

## Best Practices

- Falco / Tetragon installed
- Forwarded to SIEM
- Whitelist tuning
- Alerts SLI-based
- Runbook per alert
- Periodic rule review

## Common Mistakes

- Install but don't monitor
- Too many rules (noise)
- No whitelist (alarm fatigue)
- No response procedure

## Compliance

For PCI / HIPAA:
- Runtime monitoring required
- Documented response
- Evidence (logs)

## Real Incidents

Detected by runtime tools:
- Cryptominer dropped via supply chain
- Reverse shell from compromised app
- Privilege escalation attempts
- Unauthorized file access

## Quick Refs

```bash
# Falco
helm install falco falcosecurity/falco
kubectl logs -n falco -l app=falco

# Tetragon
helm install tetragon cilium/tetragon
kubectl logs -n tetragon -l app=tetragon

# Rules
kubectl get falcorule
kubectl get tracingpolicy
```

## Interview Prep

**Mid**: "Runtime detection."

**Senior**: "Falco rules."

**Staff**: "Container runtime security at scale."

## Next Topic

→ Move to [L12/C09 — Registries](../C09/README.md)
