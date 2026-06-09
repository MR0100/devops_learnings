# L13/C03/T02 — Secrets (And Why They're Not Really Secret)

## Learning Objectives

- Use Secrets correctly
- Understand limitations

## Secret

Like ConfigMap but for sensitive data:
- Stored base64-encoded (NOT encrypted by default!)
- Cluster-wide visible to RBAC-authorized
- Mounted as files or env vars

## YAML

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=        # base64("admin")
  password: c2VjcmV0        # base64("secret")
```

Or `stringData`:
```yaml
stringData:
  username: admin
  password: secret    # plaintext; auto-base64-encoded
```

## Create

```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=secret

kubectl create secret generic db-secret \
  --from-file=./creds/

kubectl create secret docker-registry my-reg-secret \
  --docker-server=... --docker-username=... --docker-password=...
```

## Why "Not Really Secret"

- Base64: trivially decoded (`base64 -d`)
- Stored in etcd: encryption optional
- Anyone with cluster admin can read
- Pod with mount can read
- Visible in `kubectl get secret -o yaml`

## Encryption at Rest

For etcd: configure EncryptionConfiguration:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-key>
  - identity: {}
```

API Server encrypts on write to etcd. Without: plaintext in etcd file.

For cloud KMS:
```yaml
providers:
- kms:
    name: aws-kms
    endpoint: unix:///tmp/socketfile.sock
    cachesize: 1000
```

Plugin integrates with AWS KMS / similar.

## Types

```yaml
type: Opaque                # default; generic
type: kubernetes.io/tls     # TLS cert (tls.crt + tls.key)
type: kubernetes.io/dockerconfigjson  # image pull secret
type: kubernetes.io/service-account-token  # SA token
type: bootstrap.kubernetes.io/token
```

## Mount as Env Var

```yaml
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: password
```

Or all keys:
```yaml
envFrom:
- secretRef:
    name: db-secret
```

## Mount as Volume

```yaml
volumes:
- name: creds
  secret:
    secretName: db-secret
    defaultMode: 0400

volumeMounts:
- name: creds
  mountPath: /etc/creds
  readOnly: true
```

Files in /etc/creds/:
- /etc/creds/username
- /etc/creds/password

Mode 0400 = owner read only.

## Auto-Update

Mounted Secret: updates propagate (~minute lag).
Env vars: NO update; pod restart needed.

## Image Pull Secret

For private registry:
```bash
kubectl create secret docker-registry my-reg \
  --docker-server=123.dkr.ecr.us-east-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password)
```

Pod:
```yaml
spec:
  imagePullSecrets:
  - name: my-reg
```

Or on ServiceAccount (all pods using SA inherit):
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
imagePullSecrets:
- name: my-reg
```

For ECR: better use IRSA (no static creds).

## TLS Secret

```bash
kubectl create secret tls my-tls \
  --cert=tls.crt \
  --key=tls.key
```

Used by Ingress:
```yaml
spec:
  tls:
  - hosts: [example.com]
    secretName: my-tls
```

## ServiceAccount Token

Auto-created when SA exists; mounted into pods at:
```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

For API Server access from pod.

For external (AWS): IRSA / Pod Identity.

## Best Practices

- Encryption at rest enabled (KMS-backed)
- Limit RBAC to read Secrets
- Don't commit Secret YAML (committed = leaked)
- Use SealedSecrets, SOPS, ExternalSecrets
- Rotate (manual or automated)
- Audit access

## SealedSecrets (Bitnami)

Encrypted Secret committable to Git:
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: my-secret
spec:
  encryptedData:
    password: <encrypted>
```

Controller in cluster decrypts → creates Secret.

GitOps-friendly.

## SOPS (Mozilla)

Encrypt files with KMS / age / PGP:
```bash
sops -e secrets.yaml > secrets.enc.yaml
sops -d secrets.enc.yaml | kubectl apply -f -
```

Used with FluxCD / Argo CD for GitOps.

## External Secrets Operator

Fetch from external (AWS Secrets Manager, Vault, etc.):
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-store
    kind: ClusterSecretStore
  target:
    name: db-secret-k8s
  data:
  - secretKey: password
    remoteRef:
      key: prod/db
      property: password
```

ESO creates K8s Secret from AWS Secrets Manager.

For: single source of truth in external system.

## Secrets Store CSI Driver

Mount external secrets as files:
- AWS Secrets Manager
- Azure Key Vault
- GCP Secret Manager
- Vault

```yaml
volumes:
- name: secrets
  csi:
    driver: secrets-store.csi.k8s.io
    readOnly: true
    volumeAttributes:
      secretProviderClass: my-secrets

volumeMounts:
- name: secrets
  mountPath: /mnt/secrets
```

No K8s Secret created (unless explicit syncSecret). Direct from external.

## Vault Agent

HashiCorp Vault sidecar:
- Authenticates with Vault
- Fetches secrets
- Renders templates
- Writes to shared volume
- App reads files

For: complex Vault setups.

## Rotation

Manual:
1. Update Secret (or external system)
2. Restart pods

Automated:
- ESO refreshInterval
- Vault Agent
- App polls secret file
- Reloader (restart pods on Secret change)

## Audit

```bash
# Who read this Secret
# Check audit log:
kubectl get events --field-selector involvedObject.name=db-secret
```

API Server audit log: comprehensive (configure audit policy).

## Common Mistakes

- Plaintext Secret in Git
- No encryption at rest (etcd file readable)
- Permissive RBAC (everyone can read)
- Hardcoded creds in image (worse)
- Secrets in container env vars logged on crash
- No rotation

## Anti-Patterns

- Single Secret shared across many apps (blast radius)
- env var sensitive (visible in `ps`, sometimes logged)
- Same Secret in dev + prod
- No external secret manager for serious secrets

## Best Approach

1. External secret manager (AWS Secrets Manager, Vault) source of truth
2. K8s Secret synced via ESO / Vault Agent / CSI driver
3. Mount as file (not env)
4. Encryption at rest enabled
5. RBAC restrictive
6. Rotate
7. Audit

## RBAC for Secrets

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: prod
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["my-secret"]   # specific
  verbs: ["get"]
```

Restrict; don't `["*"]`.

## Audit Annotations

```yaml
metadata:
  annotations:
    secret.k8s.io/sensitive: "true"
```

For tooling to identify (custom convention).

## Encrypted Backup

etcd backup contains Secrets. Encrypt etcd backups too.

## Quick Refs

```bash
# Create
kubectl create secret generic my-sec --from-literal=password=secret

# Get
kubectl get secret my-sec -o yaml

# Decode value
kubectl get secret my-sec -o jsonpath='{.data.password}' | base64 -d

# Update (entire)
kubectl apply -f secret.yaml

# Patch one key
kubectl patch secret my-sec -p '{"data":{"password":"bmV3LXBhc3M="}}'

# Delete
kubectl delete secret my-sec
```

## Interview Prep

**Junior**: "Secret vs ConfigMap."

**Mid**: "K8s Secret encryption."

**Senior**: "External Secrets Operator vs CSI driver."

**Staff**: "Secret rotation at scale."

## Next Topic

→ [T03 — Downward API](T03-Downward-API.md)
