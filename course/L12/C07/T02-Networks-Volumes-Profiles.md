# L12/C07/T02 — Networks, Volumes, Profiles

## Learning Objectives

- Use Compose networks
- Apply profiles

## Networks Detail

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true   # no internet access
```

Services attach:
```yaml
services:
  web:
    networks:
    - frontend
    - backend
  
  db:
    networks:
    - backend
```

For: tiered isolation.

## Network Driver

```yaml
networks:
  app:
    driver: bridge       # default
    driver_opts:
      com.docker.network.bridge.name: my-bridge
```

## Subnet

```yaml
networks:
  app:
    ipam:
      config:
      - subnet: 172.20.0.0/16
        gateway: 172.20.0.1
```

For: explicit IP space.

## Static IP

```yaml
services:
  app:
    networks:
      app:
        ipv4_address: 172.20.0.10
```

For: predictable IPs.

## External Networks

```yaml
networks:
  app:
    external: true
    name: shared-network
```

Use existing network (not created by Compose).

## Aliases

```yaml
services:
  app:
    networks:
      app:
        aliases:
        - api
        - service
```

Multiple DNS names.

## Volumes Detail

```yaml
volumes:
  db-data:
  cache:
    driver: local
  shared:
    driver_opts:
      type: nfs
      o: "addr=nfs.example.com,rw"
      device: ":/data"
```

Per-volume driver opts.

## External Volume

```yaml
volumes:
  prod-data:
    external: true
    name: prod-data-vol
```

Use existing.

## Bind Mounts

```yaml
services:
  app:
    volumes:
    - type: bind
      source: ./code
      target: /app
      read_only: true
```

Or shorthand:
```yaml
volumes:
- ./code:/app:ro
```

## Volume Mount Options

```yaml
volumes:
- type: volume
  source: db-data
  target: /var/lib/db
  volume:
    nocopy: true   # don't copy initial container contents
```

## Profiles

Conditional services:
```yaml
services:
  app:
    image: myapp
  
  debug:
    image: alpine
    profiles: ['debug']
  
  monitoring:
    image: prometheus
    profiles: ['monitoring', 'observability']
```

Default `docker compose up`: only app.

```bash
docker compose --profile debug up      # app + debug
docker compose --profile monitoring up # app + monitoring
docker compose --profile debug --profile monitoring up
```

## Use Cases for Profiles

### Optional Tools
```yaml
services:
  app:
    image: myapp
  
  pgadmin:
    image: dpage/pgadmin4
    profiles: ['tools']
```

```bash
docker compose up          # just app
docker compose --profile tools up   # app + pgadmin
```

### Environment-Specific
```yaml
services:
  app:
    image: myapp
  
  app-debugger:
    image: myapp
    command: ["--debug"]
    profiles: ['dev']
```

For: dev-only services.

## Compose File Layering

```bash
# Base
docker-compose.yml

# Auto-loaded override
docker-compose.override.yml

# Explicit
docker compose -f base.yml -f prod.yml up
```

Later files override earlier.

## Override Example

`docker-compose.yml`:
```yaml
services:
  web:
    image: myapp
    environment:
      ENV: dev
```

`docker-compose.prod.yml`:
```yaml
services:
  web:
    environment:
      ENV: prod
    deploy:
      replicas: 5
```

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
# Merged: ENV=prod, replicas=5
```

## Extends

```yaml
services:
  base:
    image: alpine
    environment:
      KEY: value
  
  child1:
    extends:
      service: base
    command: ["sh"]
```

For: shared base.

## Healthcheck Conditions

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
```

Wait for DB to be ready before starting app.

DB needs healthcheck:
```yaml
db:
  healthcheck:
    test: ["CMD", "pg_isready"]
    interval: 5s
```

## Reset / Recreate

```bash
docker compose up --force-recreate
docker compose down --volumes --rmi all
```

For: clean slate.

## Pulling Latest

```bash
docker compose pull
docker compose up -d
```

For: update images.

## Watch (Newer)

```bash
docker compose watch
```

File changes → rebuild + restart. For dev.

```yaml
services:
  app:
    build: .
    develop:
      watch:
      - action: rebuild
        path: ./src
```

## Run One-Off

```bash
docker compose run app sh
docker compose run --rm app npm test
```

Like `docker run`; uses Compose context.

## Configs

```yaml
configs:
  nginx_conf:
    file: ./nginx.conf

services:
  nginx:
    configs:
    - source: nginx_conf
      target: /etc/nginx/conf.d/default.conf
      mode: 0444
```

For: configuration injection.

## Secrets (Compose)

```yaml
secrets:
  db_password:
    file: ./db_password.txt

services:
  db:
    secrets:
    - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

For Swarm; local: env vars.

## Variable Substitution

```yaml
services:
  app:
    image: myapp:${TAG:-latest}
    environment:
      DEBUG: ${DEBUG}
```

`.env` file:
```
TAG=v1.2.3
DEBUG=true
```

## Multi-Environment

```
.env                        # dev defaults
.env.staging
.env.prod
```

```bash
docker compose --env-file .env.prod up
```

## Compose Spec

Open spec: compose-spec.io.

Implementations:
- Docker Compose
- Podman Compose
- Some others

For: portability.

## Compose v2 (Newer)

`docker compose` (built-in):
- Faster
- Better UX
- Default in modern Docker

`docker-compose` (Python): deprecated.

## Best Practices

- Networks for isolation
- Named volumes for persistence
- Profiles for optional
- healthcheck + depends_on conditions
- Per-env override files
- .env for secrets
- Restart policies

## Common Mistakes

- All services one network
- Anonymous volumes
- Hardcoded credentials
- No healthchecks
- Profile name conflicts

## Production?

Compose for:
- Dev environments
- Small single-host
- Testing

Not for:
- Multi-host
- Auto-scaling
- Production at scale

For prod: K8s typically.

## Quick Refs

```yaml
# Networks
networks:
  NAME:
    driver: bridge
    internal: true

# Volumes
volumes:
  NAME:
    driver: local
    driver_opts: ...

# Profiles
services:
  X:
    profiles: ['debug']
```

```bash
docker compose --profile NAME up
docker compose -f FILE1 -f FILE2 up
docker compose --env-file FILE up
```

## Interview Prep

**Mid**: "Compose networks."

**Senior**: "Profiles use case."

**Staff**: "Compose for 20-service stack."

## Next Topic

→ [T03 — Compose for Local Dev](T03-Compose-Dev.md)
