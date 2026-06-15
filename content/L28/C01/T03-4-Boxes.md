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

**Junior**: "What are the four boxes?" — Client, App, Data, Infra. It's a checklist so you sketch a complete system instead of forgetting a layer — most commonly people forget Infra (monitoring, CI/CD, multi-AZ).

**Mid**: "How do you use the framework in an interview?" — Sketch the four boxes first as a skeleton, fill each with its components (App: LB, services, gateway; Data: DB, cache, queue, object store), then go deep on the 2–3 risky ones. It keeps you structured and stops you from rabbit-holing into one component while leaving the design half-drawn.

**Senior**: "Walk through a photo-sharing design with it." — Client: mobile app with resumable upload and thumbnail cache. App: stateless photo/user/feed services behind an LB. Data: metadata in a DB, blobs in S3, Redis cache, Elastic for search, precomputed feeds. Infra: multi-AZ K8s, CDN, monitoring, DR. The framework makes me name the cross-box interactions (App writes blob to S3, metadata to DB) which is where the interesting consistency questions live.

**Staff**: "How do you avoid the framework making your design generic?" — The boxes are scaffolding, not the answer — the value is the depth I add inside the risky boxes and the explicit decisions at the boundaries. I use the boxes to ensure completeness, then immediately pivot to the 2–3 components the non-functional requirements make hard (the Data box for a write-heavy system, the Infra box for a multi-region one) and drive trade-offs there. Spending equal time on every box is the junior mistake; the boxes just make sure none is missing.

## Next Topic

→ Move to [L28/C02 — Scalability Patterns](../C02/README.md)
