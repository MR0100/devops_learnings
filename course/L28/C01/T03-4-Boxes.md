# L28/C01/T03 — The 4 Boxes (Client, App, Data, Infra)

## Learning Objectives

- Use the 4 boxes framework
- Structure design

## The Four Boxes

```
Client → App → Data
            ↑
         Infra
```

For: structured thinking.

## Box 1: Client

- Browser / mobile
- Authentication
- Compression / format
- Caching at client

## Box 2: App

- Web servers
- Microservices
- API gateway
- LB
- Auth service

## Box 3: Data

- DB
- Cache
- Object storage
- Message queue
- Search

## Box 4: Infra

- K8s
- Cloud accounts
- Networking
- CI/CD
- Monitoring

## Design Flow

In interview:
1. Sketch 4 boxes
2. Fill in
3. Detail each
4. Discuss trade-offs

## Per Box Concerns

### Client
- UX
- Network
- Mobile vs desktop
- Caching

### App
- Stateless preferred
- Scalable
- LB
- Health checks

### Data
- ACID vs eventual
- Sharding
- Replication
- Cache

### Infra
- Multi-AZ / region
- Monitoring
- Security
- CI/CD

## Example: Photo Sharing

### Client
- Mobile app
- Cache thumbnails
- Upload with resume

### App
- Photo service
- User service
- Feed service

### Data
- Photo metadata (DB)
- Photos (S3)
- Cache (Redis)
- Search (Elastic)
- Feed (precomputed)

### Infra
- K8s multi-AZ
- CDN
- Monitoring
- DR

## Cross-Cutting

- Security
- Observability
- Cost
- Compliance

## Best Practices

- Start with boxes
- Detail per box
- Discuss between boxes
- Iterate

## Common Mistakes

- Skip boxes (miss components)
- Detail too deep too early
- Forget infra

## Quick Refs

```
Client | App | Data | Infra

Each box:
- Components
- Concerns
- Trade-offs
- Interactions
```

## Interview Prep

**Mid**: "Design framework."

**Senior**: "Walk through."

**Staff**: "System design."

## Next Topic

→ Move to [L28/C02 — Scalability Patterns](../C02/README.md)
