# L24/C02 — Reverse Proxies

## Topics

- **T01 Nginx** — Configs, modules
- **T02 HAProxy** — High-performance L4/L7
- **T03 Envoy** — Modern, programmable
- **T04 Traefik** — K8s-native

## Nginx

The most-deployed reverse proxy. Battle-tested. Configurable.

```nginx
upstream backend {
    server backend-1:8080 weight=2 max_fails=3 fail_timeout=30s;
    server backend-2:8080 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Strengths
- Wide adoption
- Excellent static file serving
- Mature SSL/TLS
- Caching layer
- Modules for nearly everything

### Weaknesses
- Config reload required for changes (graceful but still)
- Less programmable than Envoy
- No dynamic config (without commercial Plus)

## HAProxy

The high-performance LB. Strong in pure TCP routing; great L7 too.

```haproxy
global
    maxconn 100000
    nbthread 8

defaults
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    log global

frontend web
    bind *:443 ssl crt /etc/ssl/cert.pem
    default_backend api

backend api
    balance leastconn
    server api-1 10.0.0.1:8080 check inter 5s fall 3 rise 2
    server api-2 10.0.0.2:8080 check inter 5s fall 3 rise 2
    
    http-check expect status 200
    option httpchk GET /healthz
```

### Strengths
- Fastest L4/L7 proxy
- Mature
- Reliable
- Data Plane API for dynamic config

### Weaknesses
- Config syntax can be daunting
- Smaller ecosystem than Nginx

## Envoy

Modern programmable proxy. Foundation of service mesh (Istio, App Mesh, Consul Connect).

```yaml
static_resources:
  listeners:
  - name: listener_0
    address: { socket_address: { address: 0.0.0.0, port_value: 8080 } }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          codec_type: AUTO
          stat_prefix: ingress_http
          route_config:
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/api/v1" }
                route: { cluster: api_v1, retry_policy: { num_retries: 3 } }
              - match: { prefix: "/api/v2" }
                route: { cluster: api_v2 }
          http_filters:
          - name: envoy.filters.http.router
  
  clusters:
  - name: api_v1
    type: STRICT_DNS
    load_assignment:
      cluster_name: api_v1
      endpoints:
      - lb_endpoints:
        - endpoint: { address: { socket_address: { address: api-v1, port_value: 8080 }}}
    health_checks:
    - timeout: 1s
      interval: 5s
      http_health_check: { path: /healthz }
    outlier_detection: { consecutive_5xx: 5, interval: 30s }
```

### Strengths
- Dynamic config via xDS APIs
- L7 features rich (gRPC, HTTP/2, HTTP/3)
- Observability built-in (stats, tracing)
- Service mesh standard
- WebAssembly extensibility (filter)

### Weaknesses
- Steep learning curve
- Verbose YAML
- Higher resource use than Nginx for static

## Traefik

K8s-native; auto-discovery via providers (Docker, K8s, Consul).

### K8s Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app
            port: { number: 80 }
```

Traefik auto-discovers; routes automatically.

### Strengths
- Zero-config for K8s
- Good UI/dashboard
- Cert-manager integration (Let's Encrypt)
- ACME built in

### Weaknesses
- Less performant at extreme scale than Envoy/HAProxy
- Some advanced features in commercial edition

## Comparison

| | Nginx | HAProxy | Envoy | Traefik |
|---|---|---|---|---|
| Strength | All-purpose, static | Pure perf | Programmable, mesh | K8s native |
| Config | Static reload | Static reload (or DPA) | Dynamic xDS | Dynamic discovery |
| Memory | ~10-50 MB | ~10-50 MB | ~50-200 MB | ~30-50 MB |
| Performance | Excellent | Best | Excellent | Good |
| L7 features | Rich | Good | Richest | Good |
| HTTP/3 | Yes (recent) | Yes (recent) | Yes | Yes |
| Default in | Web servers | Pure LB | Service meshes | K8s clusters |

## Choosing

| Need | Pick |
|---|---|
| K8s ingress, simple | Traefik or Nginx Ingress |
| K8s ingress, complex | Envoy-based (Contour, Emissary, Gloo) |
| Edge LB, very high traffic | HAProxy or Envoy |
| Web server + LB | Nginx |
| Service mesh | Envoy (you don't pick; Istio/Linkerd uses it) |

## Modern Trend

For K8s ingress, Envoy-based options (Gateway API implementations) are becoming standard:
- **Contour** (Envoy-based, mature)
- **Emissary** (Ambassador)
- **Gloo Edge** (Solo)
- **Cilium Gateway API**
- **Istio Ingress Gateway**

## Interview Themes

- "Compare Nginx, HAProxy, Envoy, Traefik"
- "Why is Envoy in every service mesh?"
- "K8s ingress controller options"
- "Dynamic vs static config — why it matters"
- "Reverse proxy = LB? Same or different?"
