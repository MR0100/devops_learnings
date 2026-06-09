# L06/C04/T04 — Webhooks and Async APIs

## Learning Objectives

- Design webhooks correctly
- Async API patterns

## Webhooks

Server-to-server HTTP callbacks. Provider POSTs to consumer URL when event happens.

Examples:
- GitHub → CI on push
- Stripe → app on payment
- Slack → bot on message
- Twilio → app on SMS

## Pattern

Consumer:
1. Registers URL with provider
2. Provider POSTs events to URL
3. Consumer processes; returns 200

```
POST /my-webhook
Content-Type: application/json
X-Signature: ...

{
  "event": "payment.succeeded",
  "data": { ... }
}
```

## Security Concerns

URL is public → anyone can POST. Mitigations:

### Signed Payloads
```python
def verify(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def webhook(req: Request, x_signature: str = Header(...)):
    body = await req.body()
    if not verify(body, x_signature, WEBHOOK_SECRET):
        raise HTTPException(401)
    # process
```

Use `hmac.compare_digest` (timing-safe).

### IP Allowlist
Provider publishes IP ranges; firewall to those.

### Timestamp Check
Reject events older than 5 min (prevents replay):
```
X-Timestamp: 1717584000
```
Sign timestamp + body.

## Idempotency

Webhook may be delivered multiple times (retries on 5xx). Handle duplicates:
```python
# Use event ID
event_id = payload["id"]
if redis.set(f"webhook:{event_id}", "1", nx=True, ex=86400):
    process(payload)
else:
    pass  # duplicate
```

## Response

- Return 2xx fast (provider retries on timeout)
- Don't process synchronously; enqueue
- 200 means: I received; not "I processed"

```python
@app.post("/webhook")
async def webhook(req: Request):
    body = await req.json()
    queue.enqueue("process_event", body)
    return {"received": True}
```

## Retries

Provider retries on:
- 5xx
- timeout
- connection refused

Backoff: usually exponential (10s, 1m, 5m, 30m, ...). After N attempts, give up (dead letter).

## At-Least-Once Delivery

Webhooks are at-least-once. Consumer MUST be idempotent.

## Failure Modes

- Consumer down: provider retries; events may pile up
- Consumer slow: provider times out; retries
- Bad signature: 401; provider stops
- Wrong URL: 404; provider stops

## Async APIs (Patterns)

### Long-Running Job

Client doesn't want to block:
```
POST /jobs
→ 202 Accepted
Location: /jobs/abc123

GET /jobs/abc123
→ 200 OK
{
  "status": "running",
  "progress": 50
}

GET /jobs/abc123  (later)
→ 200 OK
{
  "status": "completed",
  "result": { ... }
}
```

### Polling
Simple but inefficient. Client polls until done.

### Webhooks (Callbacks)
Client provides URL; server calls when done:
```
POST /jobs
{
  "callback_url": "https://client.com/done"
}
→ 202 Accepted

Later:
POST https://client.com/done
{
  "job_id": "abc123",
  "status": "completed"
}
```

### Server-Sent Events (SSE)
Server pushes events over single connection:
```
GET /jobs/abc/events
→ 200 OK
Content-Type: text/event-stream

event: progress
data: {"percent": 50}

event: done
data: {"result": "..."}
```

One-way; long-lived; HTTP/1.1+.

### WebSockets
Bi-directional over single TCP. Real-time chat, dashboards.

### Long Polling
Client opens GET; server holds open until event or timeout. Client immediately reconnects. Simulates push over HTTP/1.1.

## Comparison

| | Setup | Latency | Server load | Reliable |
|---|---|---|---|---|
| Polling | Easy | High | High | Yes |
| Webhooks | Medium | Low | Low | If retried |
| SSE | Easy | Low | Medium | Reconnect needed |
| WebSocket | Medium | Low | Medium | Reconnect needed |
| Long Poll | Hard | Low | High | Tricky |

## Webhook Best Practices for Providers

- Send minimal data (event ID + type)
- Include sign signature
- Include timestamp
- Document IP ranges
- Provide replay UI (resend failed)
- Provide test events
- Wide retry window (24h+)
- Dashboard showing delivery status

## Webhook Best Practices for Consumers

- Public URL with HTTPS
- Verify signature ALWAYS
- Return 2xx fast (<5s ideally)
- Enqueue; process async
- Idempotent
- Log every event (audit)
- Alert on >threshold failures

## ngrok / Tailscale for Dev

Webhook receivers need public URL. For local dev:
```bash
ngrok http 3000
# → https://abc.ngrok.io → localhost:3000
```
Provider can post to ngrok URL.

## Cloud Event Spec

Standard for event data:
```json
{
  "specversion": "1.0",
  "type": "com.example.user.created",
  "source": "/users",
  "id": "abc123",
  "time": "2026-06-09T10:00:00Z",
  "data": {
    "userId": 42
  }
}
```

Widely adopted (Knative, Argo Events, etc.).

## Common Mistakes

- No signature verification → attacks
- Sync processing → timeouts
- Not idempotent → duplicate side effects
- Returning 4xx for transient (provider gives up)
- No monitoring on consumer
- Tying retries to single instance (use queue)

## Interview Prep

**Mid**: "Webhook security checklist."

**Senior**: "Webhook vs polling vs SSE."

**Staff**: "Design event delivery (retries, ordering, idempotency)."

## Next Topic

→ Move to [L06/C05 — Building Production Tools](../C05/README.md)
