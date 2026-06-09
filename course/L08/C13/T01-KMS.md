# L08/C13/T01 — KMS (Customer-Managed Keys, Envelope Encryption)

## Learning Objectives

- Use KMS
- Apply envelope encryption

## KMS

Key Management Service. Stores / manages encryption keys.

## Key Types

### AWS-Owned Keys
- Free
- Used by AWS service for you
- Don't see in your account
- Can't audit per-key

E.g., default S3 SSE-S3.

### AWS-Managed Keys
- AWS creates per-service per-account
- Free
- Visible (alias/aws/s3, alias/aws/rds)
- Auto-rotated yearly
- Limited control

### Customer-Managed Keys (CMK)
- You create
- $1/mo per key
- Full control (policy, rotation, deletion)
- Audit per-key access (CloudTrail)
- BYOK option

For sensitive / compliance: CMK.

## Create Key

```bash
aws kms create-key --description "My key"
aws kms create-alias --alias-name alias/myKey --target-key-id ...
```

## Key Policy

Required. Without it, key unusable.

```json
{
  "Statement": [
    {
      "Sid": "RootAccess",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "AppUse",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123:role/MyApp"},
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*"
    }
  ]
}
```

Root statement: REQUIRED. Removing locks you out.

## Encryption / Decryption

```python
import boto3
kms = boto3.client("kms")

# Encrypt (up to 4 KB)
result = kms.encrypt(KeyId="alias/myKey", Plaintext=b"secret")
ciphertext = result["CiphertextBlob"]

# Decrypt
result = kms.decrypt(CiphertextBlob=ciphertext)
plaintext = result["Plaintext"]
```

For data > 4 KB: envelope encryption.

## Envelope Encryption

For larger data:
1. Generate Data Key (KMS):
   - Returns plaintext + encrypted versions
2. Encrypt data with plaintext data key (AES-GCM, etc.)
3. Store encrypted data + encrypted data key
4. Discard plaintext data key from memory

To decrypt:
1. Send encrypted data key to KMS
2. KMS returns plaintext data key
3. Decrypt data

```python
# Generate data key
result = kms.generate_data_key(KeyId="alias/myKey", KeySpec="AES_256")
plaintext_key = result["Plaintext"]
encrypted_key = result["CiphertextBlob"]

# Encrypt data locally (AES)
from cryptography.fernet import Fernet
# Use plaintext_key
cipher = Fernet(plaintext_key)
encrypted_data = cipher.encrypt(big_data)

# Store: encrypted_data + encrypted_key
# Forget: plaintext_key

# Later, decrypt
result = kms.decrypt(CiphertextBlob=encrypted_key)
plaintext_key = result["Plaintext"]
data = Fernet(plaintext_key).decrypt(encrypted_data)
```

Why: KMS API call once per envelope (not per byte). Efficient.

## AWS Services Use Envelope

S3 SSE-KMS, EBS encryption, RDS encryption: all envelope. AWS handles automatically.

You see the high-level config; envelope under hood.

## Key Rotation

Automatic (CMK):
- Yearly by default
- Old key versions retained (decrypt old data)
- Re-encryption happens lazily (next access)

```bash
aws kms enable-key-rotation --key-id ...
```

For tighter rotation: manual (re-encrypt and re-key).

## Multi-Region Keys

Replicate key to other regions:
```bash
aws kms replicate-key --key-id ... --replica-region us-west-2
```

Same key material; different region. For multi-region apps.

## BYOK (Bring Your Own Key)

Import your key material:
```bash
aws kms create-key --origin EXTERNAL
aws kms get-parameters-for-import --key-id ... --wrapping-algorithm RSAES_OAEP_SHA_256 --wrapping-key-spec RSA_2048
# Wrap your key with returned public key
aws kms import-key-material --key-id ... --import-token ... --encrypted-key-material ...
```

For: strict compliance; existing keys; loss of trust in AWS.

Material can expire; rotation manual.

## CloudHSM-Backed Keys

Key in dedicated FIPS 140-2 Level 3 HSM:
- Higher assurance
- More expensive

For: defense, financial, regulated.

## Encryption Context

Optional additional auth data:
```python
kms.encrypt(KeyId="...", Plaintext=b"data", EncryptionContext={"customer_id": "alice"})

# Must provide SAME context to decrypt
kms.decrypt(CiphertextBlob=..., EncryptionContext={"customer_id": "alice"})
```

For: tying ciphertext to context; auditing.

## Pricing

- $1/mo per CMK (per key)
- $0.03 per 10000 API calls
- $1/mo per key per region replica

For 10 keys: $10/mo + API.

For high-volume apps: API calls dominate (use envelope to reduce).

## Grants

Programmatic delegation:
```bash
aws kms create-grant --key-id ... --grantee-principal arn:... --operations Encrypt Decrypt
```

For: temporary access (vs policy edit). AWS services use grants for cross-service.

## Cross-Account

Key policy allows other account:
```json
{
  "Principal": {"AWS": "arn:aws:iam::OTHER:role/X"}
}
```

Plus IAM policy in source account.

## Common Patterns

### S3 Bucket Encrypted with CMK
- Bucket default encryption: aws:kms
- KMS key: alias/myKey
- Bucket policy: deny unencrypted PutObject
- KMS key policy: app role allowed

### RDS Encrypted
- Create with CMK
- All storage encrypted
- Snapshots inherit
- Encrypted snapshot can replicate to other region (if key allowed there)

### Secrets Manager
- KMS-encrypts secrets
- Default AWS-managed or CMK
- KMS API call per secret read

## Audit

CloudTrail KMS events:
- Encrypt
- Decrypt
- GenerateDataKey

Per call: principal, key, time, context.

For: data access audit, anomaly detection.

## Anti-Pattern: Root Access Removed

```json
// BAD: removes root
{
  "Statement": [{
    "Principal": {"AWS": "arn:aws:iam::123:role/X"},
    ...
  }]
}
```

Lockout. Root statement must remain (or AWS support recovers; pain).

## Best Practices

- CMK for compliance / audit
- Key policy with root + minimum app
- Encryption context (audit trail)
- Multi-region for global apps
- Aliases (not raw key IDs in code)
- Rotation on
- Monitor CloudTrail for unusual

## Deletion

CMK deletion has 7-30 day waiting period:
```bash
aws kms schedule-key-deletion --key-id ... --pending-window-in-days 30
```

Cancel:
```bash
aws kms cancel-key-deletion --key-id ...
```

Once deleted: data encrypted with that key is permanently lost.

## Key Aliases

Reference key by alias (stable; key ID changes):
```
alias/myKey
alias/prod-encryption
```

Use aliases in app config; rotate key without code change.

## Asymmetric Keys

KMS supports RSA, ECC for sign/verify, encrypt/decrypt:
```bash
aws kms create-key --key-spec RSA_2048 --key-usage SIGN_VERIFY
```

For: signing tokens, document signing.

## Common Mistakes

- Encrypting with KMS API for big data (use envelope)
- AWS-owned key when CMK audit needed
- Removing root from policy
- Aliases not used (key ID drift)
- No CloudTrail (no audit)

## Quick Refs

```bash
# Create key
aws kms create-key

# Alias
aws kms create-alias --alias-name alias/myKey --target-key-id ...

# Encrypt
aws kms encrypt --key-id alias/myKey --plaintext fileb://data

# Decrypt
aws kms decrypt --ciphertext-blob fileb://ciphertext

# Rotate
aws kms enable-key-rotation --key-id ...
```

## Interview Prep

**Mid**: "KMS vs hardcoded key."

**Senior**: "Envelope encryption."

**Staff**: "Multi-region key strategy."

## Next Topic

→ [T02 — Secrets Manager vs Parameter Store](T02-Secrets-Manager.md)
