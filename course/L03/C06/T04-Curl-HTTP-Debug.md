# L03/C06/T04 — curl and HTTP Debugging

## Learning Objectives

- Use curl flags for HTTP debugging
- Measure timing phases
- Test specific HTTP versions and configurations

## Basic curl

```bash
curl https://example.com                       # GET; print body
curl -v https://example.com                    # verbose (request + response)
curl -I https://example.com                    # HEAD only (response headers)
curl -i https://example.com                    # body with response headers
curl -s https://example.com                    # silent (no progress meter)
curl -L https://example.com                    # follow redirects
curl -o output.html https://example.com        # save to file
```

## Method, Headers, Body

```bash
curl -X POST https://example.com/api/foo

curl -H 'Content-Type: application/json' \
     -H 'Authorization: Bearer TOKEN' \
     -d '{"key": "value"}' \
     https://example.com/api/foo

curl --data-urlencode 'q=hello world' \
     https://example.com/search
```

## Force HTTP Version

```bash
curl --http1.1 https://example.com
curl --http2 https://example.com
curl --http3 https://example.com    # if compiled with HTTP/3 support
```

Verify connection version:
```
< HTTP/2 200
```

## Force TLS Version / Cipher

```bash
curl --tlsv1.2 https://example.com
curl --tlsv1.3 https://example.com
curl --ciphers 'AES256-GCM-SHA384' https://example.com
```

## Timing Breakdown

```bash
curl -w "@curl-format.txt" -o /dev/null -s https://example.com
```

curl-format.txt:
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                      ----------\n
          time_total:  %{time_total}\n
```

Output:
```
     time_namelookup:  0.024
        time_connect:  0.156
     time_appconnect:  0.388    # TLS handshake done
    time_pretransfer:  0.388
       time_redirect:  0.000
  time_starttransfer:  0.512    # first byte received (server processing time)
                      ----------
          time_total:  0.945    # full response done
```

Phases:
- DNS lookup
- TCP connect
- TLS handshake (app_connect - connect)
- Server processing (start_transfer - app_connect)
- Body transfer (total - start_transfer)

## Bypass DNS

Useful for testing specific origin:
```bash
curl --resolve example.com:443:1.2.3.4 https://example.com/
```

Forces a specific IP for the hostname. Tests behavior at specific endpoint.

## Test Specific Server

```bash
curl --resolve example.com:443:1.2.3.4 \
     --header 'Host: example.com' \
     https://example.com/
```

Hits 1.2.3.4 with Host header `example.com`. Tests servers behind LB.

## Show TLS Details

```bash
curl -v https://example.com 2>&1 | grep -i 'SSL\|TLS\|certif'
```

Shows: cipher, cert details, validity.

## Cookies

```bash
curl -c cookies.txt https://example.com/login -d 'user=alice&pass=...'
curl -b cookies.txt https://example.com/protected
```

`-c` saves; `-b` loads.

## Insecure Mode

For testing self-signed certs:
```bash
curl -k https://internal.example.com
```

`-k` skips cert validation. Production traffic should NOT use this.

## Concurrent Requests

```bash
# 10 parallel
seq 1 10 | xargs -n 1 -P 10 -I {} curl -s -o /dev/null -w '%{http_code} %{time_total}\n' https://example.com
```

Crude load test.

## Authentication

```bash
# Basic
curl -u alice:secret https://example.com/api

# Bearer token
curl -H 'Authorization: Bearer TOKEN' https://example.com/api

# AWS SigV4 (curl 7.75+)
curl --aws-sigv4 "aws:amz:us-east-1:s3" \
     -u "ACCESS_KEY:SECRET_KEY" \
     https://my-bucket.s3.amazonaws.com/file
```

## Output Format

```bash
# Print just the HTTP status
curl -o /dev/null -s -w '%{http_code}\n' https://example.com

# JSON of all metrics
curl -o /dev/null -s -w '%{json}\n' https://example.com | jq
```

## Common Diagnostics

### "Couldn't resolve host"
DNS issue. Try: `dig example.com`. Try different resolver: `curl --dns-servers 8.8.8.8 ...`.

### Connection timeout
Network reachability or firewall. Try `ping`, `traceroute`, `nc -vz host port`.

### TLS handshake failure
```bash
curl -v https://host 2>&1 | grep -i tls
```
Likely: cert issue, cipher mismatch, version mismatch.

### Slow time_appconnect
TLS handshake slow. Check: TLS version (1.3 is fastest), session resumption.

### Slow time_starttransfer
Server-side processing slow. Capture trace; investigate server.

### Slow body
Bandwidth limited, large body, server slow streaming.

## Modern Alternatives

- **httpie**: friendlier curl
- **xh**: fast Rust httpie clone
- **grpcurl**: for gRPC
- **websocat**: for WebSocket
- **httpfetch**: pretty output

## Interview Prep

**Mid**: "Measure each phase of a slow HTTPS request."

**Senior**: "Test specific server behind LB without DNS changes."

**Staff**: "Debug: TLS handshake takes 2 seconds. Walk through."

## Next Topic

→ [T05 — Reading Real Packet Captures](T05-Packet-Captures.md)
