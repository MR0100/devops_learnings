# L23/C05/T04 — Image Optimization at Edge

## Learning Objectives

- Optimize images at edge
- Reduce bandwidth

## Why

Images:
- Large bandwidth
- Format choice matters
- Per-device sizing

For: optimize on the fly.

## Edge Services

### Cloudflare Images / Polish
Auto-optimize on serve.

### CloudFront + Lambda@Edge
Custom logic.

### imgix
Image SaaS.

### Cloudinary
Full media platform.

### Bunny.net Optimizer

## Operations

- Resize
- Format convert (WebP, AVIF)
- Quality reduce
- Crop
- Watermark

## URL-Based

```
https://cdn.example.com/image.jpg?width=400&quality=80&format=webp
```

Edge processes; serves.

## WebP / AVIF

Modern formats:
- WebP: 25-35% smaller than JPEG
- AVIF: 30-50% smaller

Auto-serve based on Accept header.

## Cloudflare

```html
<img src="/cdn-cgi/image/width=400,quality=80/path/to/img.jpg">
```

Or Polish (auto):
- Lossy / lossless
- Auto WebP

## CloudFront + Lambda@Edge

```python
# Origin request
def handler(event, context):
    request = event['Records'][0]['cf']['request']
    # Parse params
    query = parse_qs(request['querystring'])
    width = query.get('width', ['original'])[0]
    
    # Modify origin path
    request['uri'] = f"/resized/{width}/{request['uri']}"
    return request
```

S3 origin has pre-rendered (or lazy generation).

## Lazy Generation

Worker fetches original; resizes; caches.

```javascript
// CF Worker
async function handleRequest(req) {
    const cached = await caches.default.match(req);
    if (cached) return cached;
    
    const original = await fetch(originalUrl);
    const resized = await resize(original, width, height);
    
    // Cache + return
    await caches.default.put(req, resized.clone());
    return resized;
}
```

For: per-size cache; pay only for variants needed.

## Format Negotiation

```
Accept: image/webp,image/avif,image/png,*/*
```

Edge serves best supported.

## Responsive Images

```html
<picture>
  <source srcset="img.webp" type="image/webp">
  <source srcset="img.jpg" type="image/jpeg">
  <img src="img.jpg">
</picture>
```

Browser picks best.

## Lazy Loading

```html
<img src="img.jpg" loading="lazy">
```

Native browser.

For: don't load below fold.

## srcset

```html
<img srcset="
  img-400.jpg 400w,
  img-800.jpg 800w,
  img-1600.jpg 1600w
" sizes="(max-width: 600px) 400px, 800px">
```

Browser picks size.

## Cache

Per (URL + size + format + quality):
- Cache aggressive
- Long TTL

## Cost Analysis

For 100k images @ 5 sizes × 2 formats = 1M variants:
- Lazy: only generate as needed
- Pre-generate: storage upfront

For: lazy preferred.

## Best Practices

- Edge optimize
- WebP / AVIF
- Responsive srcset
- Lazy loading
- Quality 80% (good visual)
- Cache aggressive

## Common Mistakes

- Serve original size everywhere
- Wrong format (PNG for photos)
- No lazy load
- Low cache TTL

## Quick Refs

```
Cloudflare: /cdn-cgi/image/width=N,quality=80,format=webp/PATH
imgix: ?w=400&q=80&fm=webp
Cloudinary: /image/upload/w_400,q_80,f_webp/PATH
```

## Interview Prep

**Mid**: "Image optimization."

**Senior**: "Edge image."

**Staff**: "Media platform."

## Next Topic

→ Move to [L23/C06 — Cache Failure Modes](../C06/README.md)
