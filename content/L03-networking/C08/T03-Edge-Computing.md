# L03/C08/T03 — Edge Computing

## Learning Objectives

- Understand edge compute platforms
- Choose between providers
- Apply to real use cases

## What Edge Computing Is

Code runs at the CDN PoP, not at origin. Sub-50ms latency from anywhere.

```
User → Edge PoP runs code → response
                ↓ may call origin if needed
              Origin
```

## Platforms

### Cloudflare Workers
- V8 isolates (not containers; no cold start)
- Cold start: <5ms
- JavaScript / WASM / TS
- 50ms CPU limit (default)
- KV / Durable Objects / R2 storage
- Workers Routes attach to URLs
- Most popular edge platform

### Fastly Compute@Edge
- WebAssembly (compile Rust, Go, AssemblyScript)
- ~1-5ms startup
- More language options than Workers

### AWS Lambda@Edge
- Full Lambda; Node/Python
- Cold start ~200ms+
- Slower; more capable
- 5s execution limit (viewer events)
- Used with CloudFront

### AWS CloudFront Functions
- V8 subset
- Sub-millisecond
- Very limited (no network calls, restricted APIs)
- Lower cost than Lambda@Edge

### Vercel Edge Functions / Netlify Edge / Deno Deploy
- Similar to Workers but with framework integration

## Use Cases

### Auth at Edge
```javascript
// Cloudflare Worker
export default {
  async fetch(request) {
    const token = request.headers.get('Authorization');
    if (!verify(token)) {
      return new Response('Unauthorized', { status: 401 });
    }
    return fetch(request);   // continue to origin
  }
}
```

Saves origin round-trip for invalid auth.

### A/B Testing
```javascript
const variant = Math.random() < 0.1 ? 'B' : 'A';
const headers = new Headers(request.headers);
headers.set('X-Variant', variant);
return fetch(request.url, { headers });
```

### Geo-Routing
```javascript
const country = request.cf.country;  // Cloudflare provides
if (country === 'JP') {
  return fetch('https://jp-origin.example.com' + request.path);
}
return fetch(request);
```

### URL Rewrites / Redirects
Fast 301/302 logic without origin.

### Image Optimization
- Resize on-the-fly
- Format conversion (WebP, AVIF)
- Quality adjustment based on Accept header

### Edge KV / Storage
- Cloudflare KV: eventually consistent KV store at edge
- Durable Objects: strongly-consistent per-key state
- R2: S3-compatible storage with no egress fees

### Personalization
- Custom HTML injection (analytics tag, user preferences)
- Without sending sensitive data to origin

## Why It Matters

For global apps:
- Reduce origin load (auth checks, rewrites, AB at edge)
- Sub-50ms latency for some endpoints
- Origin can be in fewer regions (or one)
- Edge compute is cheap

For mobile:
- Less roundtrip = better UX
- Battery savings (faster done)

## Tradeoffs

### Pros
- Low latency
- Origin offload
- Geographic distribution
- Cheap at scale

### Cons
- Limited CPU/time
- Smaller language support
- Less mature debugging tools
- Vendor lock-in (each platform's APIs)
- Edge runtime != Node.js (subset)

## Code Constraints

Each platform has its own subset:
- Cloudflare Workers: Web APIs (no Node.js APIs); some Node.js compat via polyfills
- Fastly: WASM-compatible languages
- Lambda@Edge: Node 18+, Python; AWS SDK works
- CloudFront Functions: JS subset (no async, no fetch)

## Cold Start

| Platform | Cold Start |
|---|---|
| CloudFront Functions | <1ms |
| Cloudflare Workers | ~5ms |
| Fastly Compute | ~5ms |
| Lambda@Edge | 200ms+ |
| Vercel Edge | ~5ms |

For high-traffic: rarely cold. For low-traffic: matters more.

## Pricing

| | Pricing |
|---|---|
| Cloudflare Workers | $0.50/M req (after 100K free/day) |
| CloudFront Functions | $0.10/M |
| Lambda@Edge | $0.60/M + duration |
| Fastly Compute | per usage |
| AWS WAF | $1/M req for custom rules |

Often cheap relative to origin compute.

## Common Patterns

### Multi-CDN with Edge
- Cloudflare front + AWS CloudFront secondary
- Workers at Cloudflare for primary path
- Fall back to CloudFront if Cloudflare misses

### Edge as Frontend
- Static site at edge (Pages, etc.)
- Worker calls API at origin or other edge

### Edge ML Inference
- Small models at edge
- Fast inference
- Use cases: bot detection, recommendation

## Operations

```bash
# Deploy a Worker via Wrangler
wrangler init my-worker
wrangler publish

# Lambda@Edge via CDK / SAM
cdk deploy MyStack
```

## Limits to Be Aware Of

- Bundle size (Workers: 1 MB free, 10 MB paid)
- CPU time (50ms-30s)
- Memory (128 MB typical)
- Network: yes, but limited concurrent

## Future

Edge compute increasingly used for:
- AI inference (small models)
- WebSocket termination
- Real-time data sync
- Privacy-preserving processing (no data leaves region)

## Common Mistakes

- **Porting a Node.js app verbatim** — edge runtimes are Web-API environments (Workers) or WASM, not full Node; `fs`, native modules, and many npm packages won't run.
- **Doing heavy compute at the edge** — strict CPU/time budgets (e.g., Workers ~50ms CPU) mean image processing or big loops will be killed; offload to origin.
- **Chasing cold starts on the wrong platform** — Lambda@Edge cold-starts ~200ms+; for sub-ms needs use CloudFront Functions or Workers/Fastly (~1–5ms).
- **Calling a single-region origin/DB from every PoP** — the edge is global but your database isn't; cross-globe round-trips erase the latency win. Cache or use edge storage.
- **Putting secrets in the bundle** — edge code is widely distributed; use the platform's secret/env binding, never hardcode keys.
- **Ignoring lock-in** — each platform's APIs (`request.cf`, KV, Durable Objects) differ; portability needs a deliberate abstraction.

## Best Practices

- **Match the platform to the workload**: CloudFront Functions for ultra-fast header/URL tweaks (sub-ms, no network), Workers/Fastly for real logic with fetch, Lambda@Edge only when you need the full runtime.
- Keep functions **small, fast, and stateless**; pull state from **edge stores** (Cloudflare KV / Durable Objects / R2) rather than a far-away origin DB.
- Use the edge to **offload origin**: auth rejection, redirects, A/B assignment, and geo-routing before any origin round-trip.
- **Set per-platform budgets** (bundle size, CPU time, memory) in CI and fail the build if exceeded — limits are hard, not advisory.
- **Bind secrets/config** through the platform rather than baking them in, and test in the *edge* runtime (Wrangler `dev`, `miniflare`) — it differs from Node.
- Abstract platform-specific APIs behind a thin layer if multi-CDN portability matters.

## Quick Refs

| Platform | Runtime | Cold start | Network calls |
|---|---|---|---|
| CloudFront Functions | JS subset | <1ms | none |
| Cloudflare Workers | V8 isolate (JS/WASM) | ~5ms | yes (fetch) |
| Fastly Compute | WASM (Rust/Go/AS) | ~5ms | yes |
| Lambda@Edge | Node/Python | ~200ms+ | yes (AWS SDK) |
| Vercel/Netlify Edge | V8 isolate | ~5ms | yes |

Decision rule: **header/URL rewrite only → CloudFront Functions; programmable logic with fetch → Workers/Fastly; needs full Node/AWS SDK → Lambda@Edge.**

```bash
# Cloudflare Workers
wrangler init my-worker
wrangler dev          # local edge runtime (miniflare)
wrangler deploy

# Read geo/edge metadata available in a Worker
#   request.cf.country, request.cf.colo, request.cf.asn
```

## Interview Prep

**Mid**: "Cloudflare Workers vs Lambda@Edge."

**Senior**: "Use case for edge computing."

**Staff**: "Auth at edge — design and tradeoffs."

## Next Topic

→ [T04 — DDoS Protection at the Edge](T04-DDoS-Edge.md)
