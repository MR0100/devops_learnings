# L12/C07/T01 — docker-compose.yml Anatomy

## Learning Objectives

- Write docker-compose.yml
- Use core features

## Compose

Define multi-container apps:
```yaml
version: '3.8'

services:
  web:
    image: nginx
    ports:
    - "80:80"
  
  app:
    build: .
    environment:
      DB_URL: postgres://db:5432/myapp
    depends_on:
    - db
  
  db:
    image: postgres:15
    volumes:
    - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: changeme

volumes:
  db-data:
```

```bash
docker compose up
```

## Services

Each service: container definition.

### Image vs Build
```yaml
services:
  web:
    image: nginx           # pull from registry
  
  app:
    build: .               # build from Dockerfile in current dir
    # or
    build:
      context: ./app
      dockerfile: Dockerfile.dev
      args:
        VERSION: 1.0
```

### Environment
```yaml
environment:
  KEY: value
  KEY2: value2

# Or list
environment:
- KEY=value
- KEY2

# From file
env_file:
- .env
```

### Ports
```yaml
ports:
- "8080:80"
- "127.0.0.1:8443:443"
- target: 80
  published: 8080
  protocol: tcp
```

### Volumes
```yaml
volumes:
- db-data:/var/lib/data    # named volume
- ./code:/app              # bind mount
- /tmp/cache:/cache:ro     # read-only
```

### Depends On
```yaml
depends_on:
- db
- redis

# Or with condition
depends_on:
  db:
    condition: service_healthy
```

Order of start; doesn't wait for readiness (without condition).

### Healthcheck
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Networks

```yaml
services:
  web:
    networks:
    - frontend
    - backend
  
  db:
    networks:
    - backend

networks:
  frontend:
  backend:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.0.0/16
```

Per-network isolation.

## Volumes Section

```yaml
volumes:
  db-data:
  cache:
    driver: local
  shared:
    external: true    # use existing
```

## Profiles

```yaml
services:
  web:
    profiles: ['web']
  
  monitoring:
    profiles: ['monitoring']
    image: prometheus
```

```bash
docker compose --profile monitoring up
```

For: conditional services.

## Commands

```bash
docker compose up        # start
docker compose up -d     # detached
docker compose down      # stop + remove
docker compose down -v   # also remove volumes
docker compose ps        # list
docker compose logs      # logs
docker compose logs -f web  # follow specific
docker compose exec web bash
docker compose restart
docker compose build
docker compose pull
```

## Detached Mode

```bash
docker compose up -d
```

Runs in background. Show logs:
```bash
docker compose logs -f
```

## Restart Policies

```yaml
restart: always         # always restart
restart: unless-stopped # unless manually stopped
restart: on-failure     # on non-zero exit
restart: "no"           # never (default)
```

## Resources

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

For: limits + requests.

## Scale

```yaml
services:
  worker:
    image: myworker
    deploy:
      replicas: 3
```

Or CLI:
```bash
docker compose up -d --scale worker=5
```

## Configs

```yaml
configs:
  nginx_conf:
    file: ./nginx.conf

services:
  web:
    configs:
    - source: nginx_conf
      target: /etc/nginx/nginx.conf
```

For: file mounts (Swarm-style).

## Secrets

```yaml
secrets:
  db_password:
    file: ./db_password.txt

services:
  app:
    secrets:
    - db_password
    # Available at /run/secrets/db_password
```

For Swarm; in dev: env vars.

## Extends

```yaml
services:
  common:
    image: alpine
    environment:
      KEY: value
  
  app:
    extends:
      service: common
    command: ["app", "start"]
```

For: reuse.

## Override Files

```bash
docker-compose.yml         # base
docker-compose.override.yml  # auto-loaded
docker-compose.prod.yml    # explicit
```

```bash
docker compose up   # uses base + override
docker compose -f docker-compose.yml -f docker-compose.prod.yml up   # explicit
```

For env-specific.

## Build Args

```yaml
services:
  app:
    build:
      context: .
      args:
        NODE_VERSION: 20
        APP_VERSION: 1.2.3
```

```dockerfile
ARG NODE_VERSION
FROM node:${NODE_VERSION}
```

## Container Name

```yaml
services:
  web:
    container_name: my-nginx
```

Vs auto-generated (myproject_web_1).

Caveat: prevents scaling (name conflicts).

## Hostname

```yaml
services:
  app:
    hostname: app-server
```

Inside container: hostname is `app-server`.

## DNS

```yaml
dns:
- 8.8.8.8
- 1.1.1.1
dns_search:
- example.com
```

Override DNS.

## Tmpfs

```yaml
services:
  cache:
    tmpfs:
    - /run
    - /tmp:size=100m
```

RAM-backed mounts.

## ulimits

```yaml
services:
  app:
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

For: file descriptor limits.

## Logging

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: 10m
        max-file: 3
```

For: log rotation.

## init

```yaml
services:
  app:
    init: true
```

Run tini as init (PID 1). For signal handling.

## Examples

### Web App
```yaml
version: '3.8'

services:
  web:
    build: ./web
    ports:
    - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
    - ./web:/app
    - /app/node_modules

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
    - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s

  redis:
    image: redis:7-alpine
    volumes:
    - redis-data:/data

  nginx:
    image: nginx
    ports:
    - "80:80"
    - "443:443"
    volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./certs:/etc/certs
    depends_on:
    - web

volumes:
  db-data:
  redis-data:
```

### Microservices
```yaml
services:
  api:
    build: ./api
  
  worker:
    build: ./worker
    deploy:
      replicas: 3
  
  scheduler:
    build: ./scheduler
  
  message-queue:
    image: rabbitmq:3-management
    ports:
    - "15672:15672"
  
  redis:
    image: redis
```

## Compose vs Swarm

Same syntax; different runtime:
- `docker compose up`: standalone Docker
- `docker stack deploy`: Swarm cluster

For prod: K8s typically (not Compose/Swarm).

## Compose Deprecation Warning

`docker-compose` (separate binary) being deprecated.

Use `docker compose` (built-in subcommand).

## Best Practices

- Use named volumes
- Healthchecks
- depends_on with conditions
- Per-env override files
- Restart policies
- Resource limits
- Networks for isolation

## Common Mistakes

- depends_on without condition (race)
- Single network for all
- No restart policy
- Hardcoded passwords

## Quick Refs

```bash
docker compose up [-d]
docker compose down [-v]
docker compose ps
docker compose logs [-f] [SERVICE]
docker compose exec SERVICE CMD
docker compose restart [SERVICE]
docker compose build
docker compose pull
docker compose stop / start
docker compose --profile NAME up
docker compose -f FILE up
```

## Interview Prep

**Junior**: "What is Compose."

**Mid**: "Multi-service stack."

**Senior**: "Compose for prod dev."

## Next Topic

→ [T02 — Networks, Volumes, Profiles](T02-Networks-Volumes-Profiles.md)
