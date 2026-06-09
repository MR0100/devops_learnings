# L13/C03 — Configuration

## Topics

- **T01 ConfigMaps** — Key/value config. Mounted as files (preferred) or env vars. Updates to mounted ConfigMaps propagate (~minute); env vars don't update without restart.
- **T02 Secrets (And Why They're Not Really Secret)** — Base64 encoded (NOT encrypted by default). Use EncryptionConfiguration at rest (KMS). Better: External Secrets Operator, Sealed Secrets, Vault sidecar.
- **T03 Downward API** — Inject pod's own metadata as env vars or files (pod name, namespace, IP, labels, resource limits). Useful for app awareness.
- **T04 Environment Variables vs Files** — Files refresh on ConfigMap/Secret update; env vars don't. Files preferred for production.

## Secret Storage Options

| Approach | Pros | Cons |
|---|---|---|
| Plain K8s Secrets | Built-in | Base64, not encrypted at rest by default |
| Encrypted at rest (KMS) | Built-in + secure | Still in etcd if etcd compromised |
| External Secrets Operator | Pulls from Vault/Secrets Manager/Parameter Store | Adds operator |
| Sealed Secrets (Bitnami) | Can commit to Git | Per-cluster decryption key |
| Vault sidecar | Most flexible | Most complex |
| CSI Secrets Store | Mount cloud-native secrets directly | Vendor-specific drivers |

## Common Pitfalls

- Using env vars and wondering why secrets didn't refresh (they can't)
- Committing K8s Secret manifests to Git (just base64 — not safe)
- Not enabling encryption at rest (etcd backup leaks all secrets)

## Interview Themes

- "How do you manage secrets in Kubernetes?"
- "Are K8s Secrets actually secure?"
- "Compare External Secrets vs Sealed Secrets"
