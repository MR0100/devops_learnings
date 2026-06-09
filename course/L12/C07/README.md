# L12/C07 — Docker Compose

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Compose-Anatomy.md) | docker-compose.yml Anatomy | 1 hr |
| [T02](T02-Networks-Volumes-Profiles.md) | Networks, Volumes, Profiles | 0.5 hr |
| [T03](T03-Compose-Local-Dev.md) | Compose for Local Dev | 0.5 hr |

## docker-compose.yml

```yaml
# compose.yaml (v2 syntax — modern)
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:dev
    ports:
      - "8080:8080"
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_PASSWORD: ${DB_PASSWORD:-devpass}
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - cached-deps:/app/node_modules
    networks:
      - app-net
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpass}
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    networks:
      - app-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

volumes:
  pgdata:
  cached-deps:

networks:
  app-net:
```

## Commands

```bash
docker compose up                    # foreground, all services
docker compose up -d                 # detached
docker compose up --build            # rebuild images
docker compose down                  # stop + remove
docker compose down -v               # also remove volumes
docker compose ps
docker compose logs -f web
docker compose exec web sh
docker compose restart web
docker compose pull                  # pull latest images
docker compose config                # validate + show effective config
docker compose run --rm web npm test  # one-off command
docker compose scale web=3
```

Note: `docker compose` (with space) is the modern v2 CLI; `docker-compose` (with dash) is the Python v1 (legacy).

## Profiles

Run subsets:
```yaml
services:
  web: { ... }
  db: { ... }
  metrics:
    image: prom/prometheus
    profiles: [observability]
```

```bash
docker compose up                          # web + db (no profile)
docker compose --profile observability up  # adds metrics
```

## Override Files

```bash
compose.yaml             # base
compose.override.yaml    # auto-merged
compose.prod.yaml        # explicit
```

```bash
docker compose -f compose.yaml -f compose.prod.yaml up
```

Common pattern:
- `compose.yaml` for service definitions
- `compose.override.yaml` for dev-only (volumes, debug ports)
- `compose.prod.yaml` for production tweaks (replicas, resource limits)

## Compose for Local Dev

```yaml
services:
  api:
    build: .
    volumes:
      - ./src:/app/src         # live reload
    command: ["npm", "run", "dev"]   # dev command
    environment:
      NODE_ENV: development
```

### Cache deps in a named volume (avoid host bind for node_modules)
```yaml
    volumes:
      - ./src:/app/src
      - node_modules:/app/node_modules
volumes:
  node_modules:
```

### Mock external services
```yaml
  localstack:                # mock AWS locally
    image: localstack/localstack
    environment:
      SERVICES: s3,sqs,dynamodb
    ports: ["4566:4566"]
```

## Compose for CI

```yaml
services:
  app: { ... }
  test:
    build: .
    depends_on:
      app:
        condition: service_healthy
    command: ["pytest"]
```

```bash
docker compose run --rm test
```

Tests run against a real stack. Tear down after.

## Where Compose Stops

Compose is single-host. For production multi-host, use:
- Docker Swarm (legacy)
- Kubernetes (de-facto)
- Nomad
- ECS / Cloud Run / etc.

For dev: Compose is great. For prod: K8s.

## Compose v2 vs v1

| | v1 (docker-compose) | v2 (docker compose) |
|---|---|---|
| Language | Python | Go (built into docker CLI) |
| Performance | Slower | Faster |
| Compose Spec | Stuck on v3 | Tracks the spec |
| BuildKit | Limited | First-class |
| Maintained | No (deprecated) | Yes |

## Common Issues

- Port conflicts (host port in use)
- depends_on not waiting for health (use `condition: service_healthy`)
- Volume permissions
- Stale build cache (`--no-cache` to force)
- Env files not loaded (`.env` is auto-loaded; others need `env_file`)

## Interview Themes

- "Walk me through a Compose file"
- "depends_on — does it wait for ready?"
- "Override files — how?"
- "When Compose vs K8s?"
- "Compose for CI integration tests"
