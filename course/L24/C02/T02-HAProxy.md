# L24/C02/T02 — HAProxy

## Learning Objectives

- Configure HAProxy
- Use for HA

## HAProxy

High-availability load balancer:
- L4 / L7
- Very fast
- Mature
- Strong observability

## Install

```bash
apt install haproxy
```

## Config

```
# /etc/haproxy/haproxy.cfg
global
    log /dev/log local0
    maxconn 100000

defaults
    mode http
    timeout connect 5s
    timeout client 50s
    timeout server 50s

frontend web
    bind *:80
    default_backend webservers

backend webservers
    balance roundrobin
    server web1 10.0.0.1:8080 check
    server web2 10.0.0.2:8080 check
    server web3 10.0.0.3:8080 check
```

## Reload

```bash
systemctl reload haproxy
```

## Health Check

```
backend web
    option httpchk GET /health
    server web1 :80 check inter 5s rise 2 fall 3
```

inter: 5s interval.
rise 2: 2 ok → healthy.
fall 3: 3 fails → down.

## SSL

```
frontend web
    bind *:443 ssl crt /etc/ssl/certs/site.pem
```

## Stats

```
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
```

Built-in dashboard.

## ACL + Routing

```
frontend web
    bind *:80
    
    acl is_api path_beg /api
    acl is_static path_beg /static
    
    use_backend api if is_api
    use_backend static if is_static
    default_backend default
```

## Sticky

```
backend web
    cookie SRV_ID insert indirect nocache
    server web1 :80 cookie web1 check
    server web2 :80 cookie web2 check
```

## Rate Limit

```
frontend web
    stick-table type ip size 100k expire 30s store conn_rate(10s)
    tcp-request connection track-sc0 src
    tcp-request connection reject if { sc_conn_rate(0) gt 100 }
```

## SSL Pass-Through

L4 mode:
```
frontend ssl
    mode tcp
    bind *:443
    default_backend backend_ssl

backend backend_ssl
    mode tcp
    server web1 :443
```

For: end-to-end TLS.

## SNI Routing

```
frontend ssl
    mode tcp
    bind *:443
    
    tcp-request inspect-delay 5s
    tcp-request content accept if { req_ssl_hello_type 1 }
    
    use_backend www if { req.ssl_sni -i www.example.com }
    use_backend api if { req.ssl_sni -i api.example.com }
```

For: multi-tenant TLS.

## HA Setup

VRRP via keepalived:
- 2 HAProxy nodes
- One active; one standby
- Floating IP

```
vrrp_instance haproxy {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    virtual_ipaddress { 10.0.0.100 }
}
```

For: HA LB.

## Performance

- 100k+ req/sec
- Low memory
- Mature

## Compared

| | HAProxy | Nginx | Envoy |
|---|---|---|---|
| Type | LB | web + LB | proxy |
| Config | declarative | declarative | dynamic |
| Web | no | yes | no |
| L4 | yes | yes | yes |
| L7 | yes | yes | yes (most) |

For LB: HAProxy or Envoy.
For web + LB: Nginx.

## Best Practices

- Stats enabled
- Health checks
- Sensible timeouts
- VRRP for HA
- Log to syslog
- Use SSL

## Common Mistakes

- Single HAProxy (SPOF)
- No health check
- No stats
- Wrong timeouts (drop connections)

## Quick Refs

```
frontend / backend / listen / global / defaults

balance roundrobin / leastconn / source / uri
mode http / tcp
option httpchk
cookie / sticky
acl X if Y; use_backend Z if X
```

## Interview Prep

**Mid**: "HAProxy."

**Senior**: "L4 vs L7."

**Staff**: "HA LB."

## Next Topic

→ [T03 — Envoy](T03-Envoy.md)
