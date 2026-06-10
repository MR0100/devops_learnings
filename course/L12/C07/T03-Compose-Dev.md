# L12/C07/T03 — Compose for Local Dev

## Learning Objectives

- Use Compose for development
- Apply patterns

## Why Compose Locally

- Reproducible env (DB, cache, queue)
- Multi-service apps
- Onboarding (one command)
- Match prod (similar setup)

## Basic Dev Setup

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev   # dev stage
    volumes:
    - .:/app
    - /app/node_modules
    ports:
    - "3000:3000"
    environment:
      NODE_ENV: development
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
    command: ["npm", "run", "dev"]

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
    - db-data:/var/lib/postgresql/data
    ports:
    - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
    
  redis:
    image: redis:7-alpine
    ports:
    - "6379:6379"

volumes:
  db-data:
```

## Hot Reload via Bind Mount

```yaml
services:
  app:
    volumes:
    - .:/app                 # code mounted
    - /app/node_modules      # don't override deps
    command: ["npm", "run", "dev"]
```

Code changes → restart via nodemon / fastify-cli / etc.

## Watch (Modern)

```yaml
services:
  app:
    develop:
      watch:
      - action: sync
        path: ./src
        target: /app/src
      - action: rebuild
        path: package.json
```

```bash
docker compose watch
```

File changes → action.

## Run Tests

```bash
docker compose run --rm app npm test
```

`run`: one-off. `--rm`: cleanup.

For: in-container testing.

## Debugging

```yaml
services:
  app:
    ports:
    - "3000:3000"
    - "9229:9229"   # debug port
    command: ["node", "--inspect=0.0.0.0:9229", "index.js"]
```

VS Code attach to debugger.

## Migrations

```yaml
services:
  migrator:
    build: .
    command: ["npm", "run", "migrate"]
    profiles: ['tools']
    depends_on:
      db:
        condition: service_healthy
```

```bash
docker compose --profile tools run --rm migrator
```

## Seeds / Fixtures

```yaml
services:
  seeder:
    build: .
    command: ["npm", "run", "seed"]
    profiles: ['tools']
    depends_on:
      db:
        condition: service_healthy
```

## Development DB

For Postgres locally:
- Port 5432 exposed for local clients
- Volume for persistence
- Or anonymous volume (resets each up)

## Mock Services

```yaml
services:
  app:
    depends_on:
    - mock-api
    environment:
      API_URL: http://mock-api:8080
  
  mock-api:
    image: mockserver/mockserver
    ports:
    - "1080:1080"
```

For: external dep mocking.

## Local SaaS

Mock cloud services locally:
- LocalStack (AWS)
- Azurite (Azure)
- gcloud emulators

```yaml
services:
  localstack:
    image: localstack/localstack
    ports:
    - "4566:4566"
    environment:
      SERVICES: s3,dynamodb,sqs
```

For: dev without cloud cost.

## Logs

```bash
docker compose logs -f app
docker compose logs --tail 100 db
docker compose logs -f   # all services
```

## Shell Access

```bash
docker compose exec app bash
docker compose exec db psql -U postgres
```

For: debugging.

## Restart Service

```bash
docker compose restart app
```

Without rebuild.

For: pick up env var changes.

## Rebuild

```bash
docker compose build
docker compose up -d --build
```

After Dockerfile changes.

## Clean Up

```bash
docker compose down       # stop + remove
docker compose down -v    # also volumes
docker compose down --rmi all   # remove images too
```

For: fresh start.

## .env File

```bash
# .env
DATABASE_URL=postgres://...
API_KEY=devsecret
DEBUG=true
```

```yaml
services:
  app:
    env_file: .env
    # OR
    environment:
      DATABASE_URL: ${DATABASE_URL}
```

For: local secrets.

Add to .gitignore.

## Multiple .env

```bash
docker compose --env-file .env.dev up
docker compose --env-file .env.test up
```

## Workspace Setup

Project root:
```
myproject/
├── docker-compose.yml
├── Dockerfile
├── .env
├── .env.example      # template (committed)
├── src/
├── tests/
└── README.md
```

`.env.example`:
```
DATABASE_URL=
API_KEY=
```

For: onboarding template.

## Onboarding Doc

```markdown
# Local Dev

1. Copy .env.example to .env; fill values
2. docker compose up -d
3. App at http://localhost:3000
4. DB at localhost:5432

## Tests

docker compose run --rm app npm test
```

## Multi-Repo

For multi-repo monorepo dev:
```yaml
services:
  api:
    build: ../api
  
  worker:
    build: ../worker
  
  frontend:
    build: ../frontend
```

For: working on multiple at once.

## Dev vs CI

Same Compose; different env:
```bash
# Dev
docker compose up

# CI
docker compose -f docker-compose.yml -f docker-compose.ci.yml up --abort-on-container-exit
```

CI override: no volumes, run tests, exit.

## Compose for Testing

```bash
docker compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from app
```

App service runs tests; exits.

## Common Mistakes

- Hot reload broken (volume mount wrong)
- node_modules mounted from host (arch mismatch)
- Hardcoded localhost (use service names)
- No cleanup (DB persists across runs)

## Best Practices

- Bind mount for code; volume for deps
- Per-service .env if needed
- Healthchecks + condition
- Profiles for optional tools
- README for setup
- .env.example committed
- Clean up volumes occasionally

## Performance on Mac

Docker Desktop: slow file sync on Mac.

Mitigations:
- `:delegated` flag (deprecated; was a hint)
- VirtioFS (newer; faster)
- Mutagen (third-party sync)

For: large repos.

## Dev Containers (VS Code)

```json
// .devcontainer/devcontainer.json
{
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/app"
}
```

VS Code opens inside container.

For: consistent dev env.

## Compose Watch (Modern)

```yaml
services:
  app:
    develop:
      watch:
      - action: sync
        path: ./src
        target: /app/src
        ignore:
        - node_modules/
```

```bash
docker compose watch
```

Native hot reload.

## Production Considerations

Compose for prod:
- Single-host OK
- Multi-host: K8s
- No auto-scaling
- Manual ops

Most: dev only.

## Real-World Example

Microservices project:
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    volumes:
    - db:/var/lib/postgresql/data
  
  redis:
    image: redis:7
  
  rabbitmq:
    image: rabbitmq:3-management
  
  api:
    build: ./api
    volumes:
    - ./api:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
  
  worker:
    build: ./worker
    volumes:
    - ./worker:/app
    depends_on:
    - rabbitmq
  
  frontend:
    build: ./frontend
    volumes:
    - ./frontend:/app
    ports:
    - "3000:3000"
  
  jaeger:
    image: jaegertracing/all-in-one
    profiles: ['tracing']
    ports:
    - "16686:16686"

volumes:
  db:
```

Full local stack.

## Quick Refs

```bash
docker compose up -d
docker compose down [-v]
docker compose logs -f [SERVICE]
docker compose exec SERVICE CMD
docker compose run --rm SERVICE CMD
docker compose restart [SERVICE]
docker compose build
docker compose pull
docker compose ps
docker compose watch
docker compose --profile NAME up
```

## Interview Prep

**Junior**: "Compose for dev."

**Mid**: "Multi-service local dev."

**Senior**: "Match prod with Compose."

## Next Topic

→ Move to [L12/C08 — Container Security](../C08/README.md)
