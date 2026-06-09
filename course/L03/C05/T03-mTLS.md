# L03/C05/T03 — mTLS (Mutual TLS)

## Learning Objectives

- Understand mutual authentication
- Implement mTLS in common platforms
- Operate cert rotation at scale

## What mTLS Is

Both client AND server present certificates. Both verify the other.

```
Server says: "Here's my cert"  ← Client verifies as before
Server says: "Show me your cert"
Client says: "Here's mine"
Server verifies: ✓
Connection established with both authenticated.
```

## Use Cases

- **Service-to-service auth** in service mesh
- **API access** where each caller has a cert
- **Zero Trust** networks (BeyondCorp model)
- **IoT** device authentication
- **K8s API server ↔ kubelet**

## TLS Handshake with mTLS

```
ClientHello
   ───────────────────→
ServerHello + Certificate + CertificateRequest
   ←───────────────────
Certificate + CertificateVerify + Finished
   ───────────────────→
Finished
   ←───────────────────
```

The `CertificateRequest` triggers client to send its cert.

## Implementing mTLS

### Nginx
```nginx
server {
    listen 443 ssl;
    ssl_certificate server.crt;
    ssl_certificate_key server.key;
    
    ssl_client_certificate ca.crt;       # CA that signs client certs
    ssl_verify_client on;                 # require client cert
    
    # Extract client cert subject for app use
    proxy_set_header X-Client-CN $ssl_client_s_dn_cn;
    proxy_set_header X-Client-Verify $ssl_client_verify;
}
```

### Envoy
```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
    require_client_certificate: true
    common_tls_context:
      tls_certificates: [...]
      validation_context:
        trusted_ca: { filename: /etc/ca.crt }
```

### Go
```go
config := &tls.Config{
    Certificates: []tls.Certificate{cert},
    ClientCAs:    caPool,
    ClientAuth:   tls.RequireAndVerifyClientCert,
}
server := http.Server{TLSConfig: config}
```

## Service Mesh Auto-mTLS

Istio / Linkerd handle mTLS transparently:
- Inject sidecar (Envoy / linkerd2-proxy)
- Sidecar terminates client TLS; opens new TLS to next sidecar
- Cert auto-rotation (Istio every 24h)
- No app changes

## Identity Models

### IP-based
Use Authorization header / API key in addition to mTLS. Cert identifies device; auth identifies user.

### Cert-based
Cert IS the identity. Subject CN or SAN encodes the service name.
- SPIFFE ID format: `spiffe://cluster.local/ns/NS/sa/SA`
- Used by Istio (compatible with SPIFFE)

## Cert Distribution

### Manual
Generate certs; distribute to each service. Painful at scale.

### CA + Automation
Internal CA (Vault PKI, cert-manager + internal Issuer) signs requests.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-app
spec:
  secretName: my-app-tls
  issuerRef:
    name: internal-ca
    kind: ClusterIssuer
  dnsNames:
    - my-app.default.svc.cluster.local
  duration: 24h          # short
  renewBefore: 6h
```

### SPIFFE/SPIRE
Vendor-neutral workload identity. Each workload gets X.509 SVID.

### Service Mesh
Mesh auto-provisions per-pod certs. Most teams use this for K8s.

## Cert Rotation

Short-lived certs (hours, days, weeks):
- Pre-renewal before expiry
- Reload (some servers need restart; modern ones reload)
- Automate

### Hot Reload
- Nginx: `nginx -s reload`
- Envoy: SDS (Secret Discovery Service) — no restart
- HAProxy: socket command
- Apps: re-read cert file on signal (SIGHUP common)

## Performance

mTLS adds:
- Larger handshake (extra cert exchange)
- Slightly more CPU
- Same bulk encryption as TLS

For most: cost is negligible. Service mesh sidecar adds CPU; but mTLS within is cheap.

## Common Pitfalls

- **Trust anchor mismatch**: client signed by CA-A; server trusts CA-B. Connection fails.
- **Cert expired**: services start failing simultaneously across env. Hot-reload didn't fire.
- **Client doesn't send cert**: server says "required"; client config wrong; error.
- **Mixed mode**: some services mTLS, some not. Complex troubleshooting.

## Operations

```bash
# Test mTLS server
curl --cert client.crt --key client.key https://service.example.com/

# Without client cert (should fail)
curl https://service.example.com/

# Verify chain
openssl s_client -connect host:443 -cert client.crt -key client.key
```

## When mTLS

- Zero Trust networking
- Service mesh adoption
- High-security APIs
- IoT
- Internal data tier

## When NOT mTLS

- Public APIs (users won't have certs)
- Where API key + TLS is sufficient
- Without automation to handle cert lifecycle

## Interview Prep

**Mid**: "What is mTLS?"

**Senior**: "Cert rotation at 10K microservices — how?"

**Staff**: "Service mesh mTLS — how does it work without app changes?"

## Next Topic

→ [T04 — Cipher Suites, Forward Secrecy](T04-Cipher-Suites.md)
