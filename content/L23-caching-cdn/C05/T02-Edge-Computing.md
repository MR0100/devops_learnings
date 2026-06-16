# L23/C05/T02 — Edge Computing (CF Workers, Lambda@Edge)

## Learning Objectives

- Use edge compute
- Choose platform

## Edge Compute

Run code at CDN edge:
- Closer to user
- Lower latency
- Less origin load

## Cloudflare Workers

V8 isolates:
- Sub-millisecond cold start
- JS / TypeScript / WASM
- Free tier 100k req/day

```javascript
export default {
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === '/api/hello') {
      return new Response('Hello!');
    }
    return fetch(req);
  }
}
```

Deploy:
```bash
wrangler deploy
```

## Lambda@Edge

CloudFront + Lambda:
- Run on viewer request/response
- Origin request/response
- 50 ms cold start

```python
def handler(event, context):
    req = event['Records'][0]['cf']['request']
    req['uri'] = req['uri'].replace('/old', '/new')
    return req
```

For: customization.

## Fastly Compute@Edge

WebAssembly:
- Rust / Go / JS
- Sub-ms start

For: high-perf edge.

## Use Cases

### A/B Testing
At edge: assign variant; route.

### Authentication
JWT verify at edge.

### Personalization
Modify response based on user.

### Image Optimization
Resize on the fly.

### Geo Routing
Different content per region.

### Header Manipulation
Add security headers.

## Cloudflare Workers Examples

### Redirect
```javascript
if (url.pathname === '/old') {
  return Response.redirect(url.origin + '/new', 301);
}
```

### Auth
```javascript
const token = req.headers.get('Authorization');
if (!verifyToken(token)) {
  return new Response('Unauthorized', { status: 401 });
}
```

### KV
```javascript
const value = await MY_KV.get('key');
await MY_KV.put('key', 'value');
```

### Durable Objects
Stateful at edge:
```javascript
class Counter {
  async fetch(req) {
    const count = (await this.state.storage.get('count')) || 0;
    await this.state.storage.put('count', count + 1);
    return new Response(count);
  }
}
```

## Lambda@Edge Examples

### Header
```python
response['headers']['x-custom'] = [{'key': 'X-Custom', 'value': 'value'}]
```

### Routing
```python
if 'mobile' in user_agent:
    request['origin']['s3']['path'] = '/mobile'
```

## Performance

- Workers: <1 ms cold start; <5 ms typical
- Lambda@Edge: 50 ms cold start
- Compute@Edge: < 1 ms

For latency-critical: Workers or Compute@Edge.

## Limits

### Workers
- 10 ms CPU (free)
- 50 ms (paid)
- 128 MB

### Lambda@Edge
- 5 sec
- 128 MB (viewer)
- 10 GB (origin)

## Cost

### Workers
- Free 100k req/day
- $5/M after

### Lambda@Edge
- $0.60/M requests
- Plus duration

For: Workers cheaper at scale.

## Limitations

- No filesystem
- Limited CPU
- Stateless (mostly)
- Vendor lock-in

## Best Practices

- Idempotent
- Stateless or Durable Objects
- Test latency
- Monitor errors
- Edge config in code

## Common Mistakes

- Heavy compute (timeouts)
- Calls to slow backend (no edge benefit)
- No fallback
- Personalization breaks cache

## Real Examples

### Cloudflare
Many: routing, auth, CDN customization.

### AWS
A/B testing, security headers, geofencing.

### Discord
Edge auth.

## Quick Refs

```javascript
// Workers
export default { async fetch(req, env, ctx) { ... } }

// KV
await env.MY_KV.get / put

// Durable Object
class X { async fetch(req) { ... } }
```

```python
# Lambda@Edge
def handler(event, context):
    request = event['Records'][0]['cf']['request']
    ...
```

## Interview Prep

**Mid**: "Edge compute."

**Senior**: "Workers vs Lambda@Edge."

**Staff**: "Edge architecture."

## Next Topic

→ [T03 — Cache Keys & Vary Headers](T03-Cache-Keys-Vary.md)
