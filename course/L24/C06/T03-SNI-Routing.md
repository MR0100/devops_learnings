# L24/C06/T03 — SNI Routing

## Learning Objectives

- Use SNI routing
- Multi-tenant TLS

## SNI

Server Name Indication:
- TLS extension
- Client sends hostname in TLS handshake
- Server picks cert

## Why

Before SNI:
- One cert per IP
- Multiple hosts: need IP each

With SNI:
- Multiple certs per IP
- Multiple hosts share IP

## How

```
ClientHello with SNI: api.example.com
Server: uses cert for api.example.com
```

## SNI Routing

LB picks backend by SNI:
```
SNI: api.example.com → backend-api
SNI: www.example.com → backend-www
SNI: blog.example.com → backend-blog
```

Without decrypting.

## TCP Mode

LB doesn't terminate:
- Reads SNI
- Forwards to backend
- E2E encryption

For: e2e + multi-tenant.

## HAProxy

```
frontend ssl
    mode tcp
    bind *:443
    
    tcp-request inspect-delay 5s
    tcp-request content accept if { req_ssl_hello_type 1 }
    
    use_backend api if { req.ssl_sni -i api.example.com }
    use_backend web if { req.ssl_sni -i www.example.com }
```

## Nginx Stream

```nginx
stream {
    map $ssl_preread_server_name $backend {
        api.example.com api_pool;
        www.example.com web_pool;
    }
    
    server {
        listen 443;
        proxy_pass $backend;
        ssl_preread on;
    }
}
```

## Use Cases

### Multi-Tenant SaaS
Per-customer SNI; route to tenant backend.

### Multi-Service
Same IP; different services per host.

### E2E Encryption
Don't terminate; just route.

## Limitations

### Older Clients
Some old clients don't send SNI.
- Need fallback (default cert)
- Or refuse

### Visible Hostname
SNI is plaintext.
- Privacy concern
- ECH (Encrypted Client Hello) addresses

## ECH

Encrypted Client Hello:
- Encrypts SNI
- Privacy preserved
- Cloudflare and others rolling out

## Wildcard Certs

For *.example.com:
- One cert
- Multiple subdomains

Combined with SNI: flexible.

## Subject Alternative Name (SAN)

One cert for multiple hosts:
```
api.example.com
www.example.com
blog.example.com
```

For: small set known hosts.

## SNI vs SAN

| | SNI | SAN |
|---|---|---|
| Client choice | yes (sends to server) | server cert covers |
| Multi-host per IP | yes | yes (one cert) |
| Per-host cert | yes | no (one cert) |

For: combine.

## Best Practices

- SNI routing for multi-tenant
- SAN certs for related hosts
- Plan for ECH (privacy)
- Default backend for no SNI
- Test old clients

## Common Mistakes

- No fallback (old client breaks)
- Wrong cert (SNI mismatch)
- Plain SNI logged (privacy)

## Quick Refs

```nginx
# Stream + ssl_preread
ssl_preread_server_name → variable
map to backend pool

# HAProxy
req.ssl_sni for routing
```

## Interview Prep

**Senior**: "What's SNI."

**Staff**: "SNI routing."

**Principal**: "Multi-tenant TLS."

## Next Topic

→ Move to [L24/C07 — DDoS Defense](../C07/README.md)
