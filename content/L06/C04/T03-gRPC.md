# L06/C04/T03 — gRPC and Protocol Buffers

## Learning Objectives

- Understand gRPC trade-offs vs REST
- Write a `.proto` and generate code

## gRPC

Google's RPC framework. Built on:
- HTTP/2 (multiplexing, server push, header compression)
- Protocol Buffers (binary, typed schema)
- Code generation

Use cases: internal microservice communication, streaming, polyglot.

## Protocol Buffers

Binary serialization with schema.

```protobuf
syntax = "proto3";

package userservice;

option go_package = "github.com/me/userservice/proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (User);
  
  // Server streaming
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
  
  // Client streaming
  rpc UploadUsers(stream User) returns (UploadResponse);
  
  // Bidirectional
  rpc Chat(stream Message) returns (stream Message);
}

message GetUserRequest {
  int64 id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  repeated string tags = 4;
  Status status = 5;
}

enum Status {
  UNKNOWN = 0;
  ACTIVE = 1;
  INACTIVE = 2;
}

message ListUsersRequest {
  int32 limit = 1;
  string cursor = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_cursor = 2;
}
```

Field numbers are crucial: identify fields on wire; never reuse.

## Compile

```bash
protoc --go_out=. --go-grpc_out=. user.proto
# → user.pb.go (messages) + user_grpc.pb.go (service)
```

Other languages: `--python_out`, `--ts_out`, `--java_out`, etc.

## Server (Go)

```go
type server struct {
    pb.UnimplementedUserServiceServer
}

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    return &pb.User{
        Id:    req.Id,
        Name:  "alice",
        Email: "a@x.com",
    }, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    grpcServer := grpc.NewServer()
    pb.RegisterUserServiceServer(grpcServer, &server{})
    grpcServer.Serve(lis)
}
```

## Client (Go)

```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
defer conn.Close()

client := pb.NewUserServiceClient(conn)
user, _ := client.GetUser(ctx, &pb.GetUserRequest{Id: 1})
fmt.Println(user.Name)
```

## Streaming

### Server streaming
```go
func (s *server) StreamUsers(req *pb.StreamUsersRequest, stream pb.UserService_StreamUsersServer) error {
    for _, u := range allUsers {
        stream.Send(u)
    }
    return nil
}
```

### Client streaming
```go
stream, _ := client.UploadUsers(ctx)
for _, u := range users {
    stream.Send(u)
}
resp, _ := stream.CloseAndRecv()
```

### Bidi
```go
func (s *server) Chat(stream pb.ChatService_ChatServer) error {
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        stream.Send(&Message{Text: "echo: " + msg.Text})
    }
}
```

## Why gRPC

- **Performance**: 5-10× faster than JSON over HTTP/1.1
- **Schema enforced**: no shape drift
- **Code generation**: client libraries free
- **Streaming**: first-class
- **HTTP/2 benefits**: multiplexing, header compression
- **Polyglot**: any language

## Why NOT gRPC

- Not browser-friendly (need gRPC-Web proxy)
- Harder to debug (binary)
- Curl doesn't work directly
- Tooling not universal
- Requires more setup

## When to Choose

| Use case | Choose |
|---|---|
| Public API for web/mobile | REST/JSON |
| Internal microservices | gRPC |
| Streaming | gRPC |
| Polyglot teams | gRPC |
| Simple resource CRUD | REST |
| Mass-distribution SDK | REST (JSON) |

Many use both: gRPC internally; REST gateway externally.

## gRPC-Gateway

Generate REST/JSON proxy from .proto:
```protobuf
import "google/api/annotations.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (User) {
    option (google.api.http) = {
      get: "/v1/users/{id}"
    };
  }
}
```

Then `protoc --grpc-gateway_out=.` generates a HTTP server that proxies to gRPC. Single source of truth for both protocols.

## Authentication

```go
// Server
opts := []grpc.ServerOption{
    grpc.UnaryInterceptor(authInterceptor),
}
grpcServer := grpc.NewServer(opts...)

func authInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }
    tokens := md.Get("authorization")
    if !validateToken(tokens) {
        return nil, status.Error(codes.Unauthenticated, "bad token")
    }
    return handler(ctx, req)
}

// Client
md := metadata.Pairs("authorization", "Bearer "+token)
ctx = metadata.NewOutgoingContext(ctx, md)
client.GetUser(ctx, req)
```

## TLS

```go
creds, _ := credentials.NewServerTLSFromFile("server.crt", "server.key")
grpcServer := grpc.NewServer(grpc.Creds(creds))

// Client
creds, _ := credentials.NewClientTLSFromFile("ca.crt", "")
conn, _ := grpc.Dial(addr, grpc.WithTransportCredentials(creds))
```

mTLS: client also presents cert; common in service mesh.

## Deadlines

gRPC has deadline propagation:
```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
client.GetUser(ctx, req)
```

Server can check `ctx.Err()` to abort early.

## Status Codes (gRPC)

Different from HTTP:
- OK
- CANCELLED
- INVALID_ARGUMENT
- NOT_FOUND
- ALREADY_EXISTS
- PERMISSION_DENIED
- UNAUTHENTICATED
- DEADLINE_EXCEEDED
- UNIMPLEMENTED
- INTERNAL
- UNAVAILABLE
- RESOURCE_EXHAUSTED

```go
return nil, status.Error(codes.NotFound, "user not found")
```

## Reflection

For tools like grpcurl:
```go
reflection.Register(grpcServer)
```
```bash
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 userservice.UserService/GetUser
```

## Versioning

Proto3 is backwards-compatible if:
- Don't change field numbers
- Don't change field types
- Adding fields OK
- Removing field → mark `reserved` (don't reuse number)

```protobuf
message User {
  reserved 4, 5;
  reserved "old_field";
  ...
}
```

## Observability

OpenTelemetry has gRPC instrumentation:
```go
import "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"

grpcServer := grpc.NewServer(
    grpc.UnaryInterceptor(otelgrpc.UnaryServerInterceptor()),
)
```

Auto traces, metrics.

## Common Mistakes

- Reusing field numbers (breaks compat)
- No deadlines (hangs)
- gRPC without TLS in production
- Returning huge messages (use streaming)
- Not handling stream errors

## Best Practices

- Evolve protos additively: only ever add new fields with new numbers; never renumber, reuse, or change the type of an existing field — `reserve` retired numbers/names.
- Always set deadlines on the client (`context.WithTimeout`) and check `ctx.Err()` on the server so calls can't hang forever.
- Use TLS (or mTLS) for any non-localhost traffic; never run plaintext gRPC across the network in production.
- Return proper `status.Error(codes.X, msg)` codes (NotFound, InvalidArgument, etc.) instead of generic errors so clients can react.
- Stream large or unbounded result sets rather than returning one giant message.
- Enable reflection in dev for `grpcurl`, and add OpenTelemetry interceptors for traces/metrics.

## Quick Refs

```protobuf
syntax = "proto3";
package user.v1;            // version in the package path

message User {
  string id    = 1;
  string email = 2;
  reserved 3;              // retired field number — never reuse
  reserved "phone";        // retired field name
}

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);   // server streaming
}
```

```bash
# Generate Go stubs
protoc --go_out=. --go-grpc_out=. user.proto

# Explore a running server (reflection enabled)
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext -d '{"id":"u1"}' localhost:50051 user.v1.UserService/GetUser
```

```go
// Client: deadline + TLS + status handling
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
conn, _ := grpc.NewClient("api:443", grpc.WithTransportCredentials(creds))
resp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: "u1"})
if status.Code(err) == codes.NotFound { ... }

// Server: typed error
return nil, status.Errorf(codes.InvalidArgument, "id is required")
```

## Interview Prep

**Mid**: "gRPC vs REST."

**Senior**: "Streaming use cases."

**Staff**: "Proto evolution — breaking change strategy."

## Next Topic

→ [T04 — Webhooks and Async APIs](T04-Webhooks.md)
