# L22/C05 — NATS & JetStream

## Topics

- **T01 When NATS Beats Kafka** — Use cases

## NATS

Ultra-light pub/sub.
- Open source (CNCF graduated)
- Written in Go
- Single binary, no deps
- Wire protocol: plain text
- Sub-millisecond latency

## Core NATS (no persistence)

- Topics (subjects)
- Publish-subscribe
- Request-reply
- At-most-once
- No replay

```go
nc, _ := nats.Connect("nats://nats:4222")
nc.Publish("orders.created", payload)

nc.Subscribe("orders.*", func(m *nats.Msg) {
    handle(m.Data)
})
```

## JetStream

NATS's persistence + streaming layer (built-in, not separate).

- At-least-once
- Replay
- Pull and push consumers
- KV store
- Object store

```go
js, _ := nc.JetStream()
js.AddStream(&nats.StreamConfig{Name: "ORDERS", Subjects: []string{"orders.>"}})
js.Publish("orders.created", payload)

sub, _ := js.PullSubscribe("orders.>", "consumer-group")
msgs, _ := sub.Fetch(10)
```

## When NATS

### Use Cases
- **Request-reply at sub-ms** (microservices RPC)
- **IoT** (low overhead, mass scale)
- **K8s leader election**
- **NATS as event bus** (lighter than Kafka)
- **JetStream** when persistence needed but Kafka feels overkill

### Strengths
- Minimal ops (single binary, tiny memory)
- Sub-ms latency
- Easy to learn
- Embedded use cases

### Limits
- Smaller ecosystem than Kafka
- JetStream relatively new
- Less throughput than Kafka at very high scale

## NATS vs Kafka

| | NATS | Kafka |
|---|---|---|
| Footprint | Tiny (~10 MB) | Heavy (JVM) |
| Latency | Sub-ms | Few ms |
| Throughput | 100K-1M msg/sec | Millions msg/sec |
| Persistence | JetStream | Built-in |
| Replay | JetStream | First-class |
| Use | Microservices RPC, IoT, light streams | Heavy streams, replay-first |

## Interview Themes

- "NATS vs Kafka — when each?"
- "JetStream — what it adds"
- "Sub-ms messaging — strategies"
