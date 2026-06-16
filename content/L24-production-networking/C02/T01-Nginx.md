# L24/C02/T01 — Nginx (Configs, Modules)

## Learning Objectives

- Configure Nginx
- Use as reverse proxy

## Nginx

Most popular web server / reverse proxy:
- Event-driven
- High concurrency
- Modular

## Install

```bash
apt install nginx
```

## Config

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend1:8080;
        server backend2:8080;
    }
    
    server {
        listen 80;
        server_name example.com;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Reload

```bash
nginx -s reload
# Or
systemctl reload nginx
```

Zero-downtime config.

## upstream

```nginx
upstream backend {
    server backend1:8080 weight=3;
    server backend2:8080 weight=1;
    server backend3:8080 backup;
    
    least_conn;     # algorithm
    keepalive 32;   # keep-alive connections
}
```

## Health Check

OSS Nginx: passive only.
Nginx Plus / OpenResty: active.

## SSL

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

## Modules

- `ngx_http_proxy_module`
- `ngx_http_ssl_module`
- `ngx_http_gzip_module`
- `ngx_http_realip_module`
- `ngx_http_limit_req_module`
- 100+ more

## Rate Limit

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
    
    server {
        location / {
            limit_req zone=mylimit burst=20 nodelay;
        }
    }
}
```

## Caching

```nginx
http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=mycache:10m max_size=10g;
    
    server {
        location / {
            proxy_pass http://backend;
            proxy_cache mycache;
            proxy_cache_valid 200 1h;
            proxy_cache_use_stale error timeout updating;
        }
    }
}
```

## gzip

```nginx
gzip on;
gzip_types text/plain application/json application/javascript;
gzip_min_length 1000;
```

## WebSocket

```nginx
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Logging

```nginx
log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent"';

access_log /var/log/nginx/access.log main;
```

JSON format for structured:
```nginx
log_format json escape=json '{"time":"$time_iso8601","method":"$request_method","status":$status}';
```

## Stream

For TCP/UDP:
```nginx
stream {
    upstream backend {
        server backend1:3306;
    }
    
    server {
        listen 3306;
        proxy_pass backend;
    }
}
```

## OpenResty

Nginx + Lua:
- Scriptable
- Run code in nginx

```lua
location /api {
    content_by_lua_block {
        ngx.say("hello from lua")
    }
}
```

For: dynamic processing.

## Test Config

```bash
nginx -t   # validate
```

## Best Practices

- worker_processes auto
- worker_connections high (10k+)
- keepalive to backend
- gzip enabled
- Sensible timeouts
- Log structured (JSON)

## Common Mistakes

- Default config (low conns)
- No reload (downtime)
- No timeouts (hung connections)
- No rate limit (DoS easy)

## Quick Refs

```bash
nginx -t        # test config
nginx -s reload # reload
nginx -s stop / -s quit  # stop
```

```nginx
upstream / server / location / proxy_pass
limit_req / proxy_cache / gzip
```

## Interview Prep

**Mid**: "Nginx basics."

**Senior**: "Caching + rate limit."

**Staff**: "Nginx at scale."

## Next Topic

→ [T02 — HAProxy](T02-HAProxy.md)
