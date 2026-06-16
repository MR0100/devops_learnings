# L06/C02/T04 — requests, httpx for HTTP

## Learning Objectives

- Make HTTP requests properly
- Handle errors + retries

## requests (Standard)

Most popular Python HTTP library. Not in stdlib (`pip install requests`).

```python
import requests

# GET
r = requests.get("https://api.example.com/users", timeout=5)
r.raise_for_status()              # raises on 4xx/5xx
data = r.json()

# Headers
r = requests.get(url, headers={"Authorization": f"Bearer {token}"})

# Query params
r = requests.get(url, params={"q": "search", "limit": 10})

# POST JSON
r = requests.post(url, json={"key": "value"})

# POST form
r = requests.post(url, data={"field": "value"})

# Files
r = requests.post(url, files={"file": open("data.txt", "rb")})

# Custom timeout
r = requests.get(url, timeout=(3, 10))    # connect, read
```

### Session (Connection Pooling)
```python
s = requests.Session()
s.headers.update({"Authorization": f"Bearer {token}"})
s.mount("https://", HTTPAdapter(max_retries=3))

for url in urls:
    r = s.get(url)
```

Reuses connection for performance.

## httpx (Modern, Async)

Drop-in compatible with requests + async support + HTTP/2.

```python
import httpx

# Sync
with httpx.Client() as client:
    r = client.get("https://api.example.com")
    data = r.json()

# Async
async with httpx.AsyncClient() as client:
    r = await client.get("https://api.example.com")

# HTTP/2
async with httpx.AsyncClient(http2=True) as client:
    r = await client.get(url)
```

### Concurrent
```python
import asyncio
import httpx

async def fetch(client, url):
    r = await client.get(url, timeout=10)
    return r.json()

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, u) for u in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

## Timeouts

**Always set timeouts.** Without: requests can hang forever.

```python
requests.get(url, timeout=5)              # 5s connect + read
requests.get(url, timeout=(3, 10))         # 3s connect, 10s read
```

httpx similar.

## Retries

Manual:
```python
import time

def request_with_retry(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
```

Better: use urllib3 retry:
```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=retry))
```

## Error Handling

```python
try:
    r = requests.get(url, timeout=5)
    r.raise_for_status()
except requests.Timeout:
    log.error("timeout")
except requests.ConnectionError:
    log.error("can't connect")
except requests.HTTPError as e:
    log.error(f"HTTP error: {e.response.status_code}")
except requests.RequestException as e:
    log.exception("unexpected")
```

## Auth

```python
# Basic auth
r = requests.get(url, auth=("user", "pass"))

# Token
r = requests.get(url, headers={"Authorization": f"Bearer {token}"})

# AWS SigV4
import boto3
session = boto3.Session()
# Use botocore Sigv4Auth + requests
```

## Streaming Response

For large responses:
```python
with requests.get(url, stream=True) as r:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
```

## SSL Verification

Default: verifies CA-signed certs.
```python
# Disable (rarely needed; security risk)
requests.get(url, verify=False)

# Custom CA bundle
requests.get(url, verify="/path/to/ca.crt")

# Client cert (mTLS)
requests.get(url, cert=("cert.pem", "key.pem"))
```

## Proxies

```python
requests.get(url, proxies={"https": "http://proxy:8080"})
```

Or env: `HTTPS_PROXY=http://proxy:8080`.

## Connection Pooling

Sessions reuse TCP/TLS connections. Critical for many requests:
```python
s = requests.Session()
# 1000 requests; ~5× faster than fresh Session each time
```

## Async at Scale

For 1000+ concurrent requests: httpx async + asyncio.

```python
sem = asyncio.Semaphore(100)    # limit concurrency

async def fetch(client, url):
    async with sem:
        return await client.get(url)
```

## Common Mistakes

- No timeout (script hangs)
- No retry on transient (5xx)
- No `raise_for_status()` (silent failures)
- Loading huge response to memory (use stream)
- Not closing session

## httpx vs requests

| | requests | httpx |
|---|---|---|
| Sync | Yes | Yes |
| Async | No | Yes |
| HTTP/2 | No | Yes |
| API | Original | Same + more |
| Popularity | Massive | Growing |

For new code: httpx. Existing requests-based: fine to keep.

## Best Practices

- Always pass an explicit `timeout=` (connect and read); a missing timeout is the #1 cause of hung automation.
- Reuse a `Session`/`Client` across requests for connection pooling, then `raise_for_status()` on every response.
- Retry only idempotent calls on transient failures (429, 5xx, connection errors) with exponential backoff and jitter; cap total attempts.
- Honor `Retry-After` on 429/503 instead of hammering with fixed backoff.
- Stream large responses (`stream=True` / `client.stream`) so you don't load whole payloads into memory.
- Verify TLS (keep `verify=True`); pin a custom CA bundle rather than disabling verification.
- Prefer `httpx.AsyncClient` with `asyncio.gather` for high-fan-out concurrent calls.

## Quick Refs

```python
import httpx

# Reusable client with timeout + connection pooling
limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
with httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0), limits=limits) as client:
    r = client.get("https://api.example.com/v1/things", params={"page": 1})
    r.raise_for_status()
    data = r.json()
```

```python
# Retry with backoff (tenacity) — idempotent calls only
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(5),
       wait=wait_exponential(multiplier=0.5, max=10),
       retry=retry_if_exception_type(httpx.TransportError))
def fetch(client, url):
    r = client.get(url, timeout=10.0)
    r.raise_for_status()
    return r.json()
```

```python
# Async fan-out
import asyncio, httpx
async def main(urls):
    async with httpx.AsyncClient(http2=True, timeout=10.0) as c:
        resps = await asyncio.gather(*(c.get(u) for u in urls))
    return [r.json() for r in resps]
```

## Interview Prep

**Mid**: "Why always timeout?"

**Senior**: "Concurrent HTTP with httpx."

**Staff**: "Retry strategy with backoff."

## Next Topic

→ [T05 — Boto3 for AWS, the Kubernetes Python Client](T05-Boto3-K8s-Client.md)
