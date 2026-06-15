# L08/C07/T07 — API Gateway (REST, HTTP, WebSocket)

## Learning Objectives

- Pick API Gateway type
- Configure for production

## Three Types

| | REST | HTTP | WebSocket |
|---|---|---|---|
| Protocol | HTTP | HTTP | WebSocket |
| Features | Most | Subset; cheaper | Bidirectional |
| Cost (1M) | $3.50 | $1.00 | $1.00 |
| Cold start | Slower | Faster | n/a |
| Caching | Yes | No | n/a |
| Request transform | Yes | Limited | Limited |
| When | Complex | Simple HTTP | Real-time |

## HTTP API

Newer; lower cost; simpler. Recommended for new.

Features:
- Routes
- Stage
- Lambda + HTTP backend
- JWT authorizer (Cognito, OIDC)
- IAM auth
- CORS
- Custom domain

Lacks:
- Caching
- WAF (only via CloudFront)
- API keys / usage plans (limited)
- Request validation
- Detailed request transformation

For most: HTTP API enough.

## REST API

Mature; feature-rich.

Has:
- Request validation
- Request/response transformation
- Caching
- API keys + usage plans
- WAF integration
- Stages with stage variables
- Resource policies
- SDK generation

For: complex APIs, B2B with quotas, legacy.

## Setup HTTP API

```bash
aws apigatewayv2 create-api --name myApi --protocol-type HTTP --target arn:aws:lambda:...:function:myFn
```

Returns endpoint:
```
https://<id>.execute-api.us-east-1.amazonaws.com/
```

## Routes

```
GET /users → Lambda A
POST /users → Lambda B
GET /orders/{id} → Lambda C
```

Path params: `{id}` → `event.pathParameters.id`.

## Stages

Deploy version of API:
- prod
- staging
- dev

Stage variables for env-specific (e.g., Lambda alias):
```
stageVariables.lambdaAlias → prod or staging
```

## Custom Domain

```bash
aws apigatewayv2 create-domain-name --domain-name api.example.com --domain-name-configurations CertificateArn=arn:...
aws apigatewayv2 create-api-mapping --domain-name api.example.com --api-id ... --stage prod
```

Plus Route53 ALIAS → API Gateway.

## Authentication

### JWT Authorizer (HTTP / REST)
Verify JWT (from Cognito, Auth0, custom):
```yaml
Authorizers:
  myAuth:
    Type: JWT
    Identity:
      Source: $request.header.Authorization
    JwtConfiguration:
      Issuer: https://cognito-idp.us-east-1.amazonaws.com/POOL
      Audience: [client-id]
```

### Lambda Authorizer
Custom logic in Lambda:
```python
def handler(event, context):
    token = event["authorizationToken"]
    if validate(token):
        return {"principalId": "user", "policyDocument": {...}}
    raise Exception("Unauthorized")
```

### IAM Auth
Sign requests with SigV4. For service-to-service.

### API Key (REST only)
Header `x-api-key: ...`. With usage plans for quotas.

## CORS

```yaml
CorsConfiguration:
  AllowOrigins: ["https://app.example.com"]
  AllowMethods: ["GET", "POST"]
  AllowHeaders: ["Authorization", "Content-Type"]
  MaxAge: 600
```

Allows cross-origin browser requests.

## Throttling

Default: 10k req/sec per account.

Per-route or per-method limits:
- Burst: temporary spike capacity
- Rate: sustained

Returns 429 when exceeded.

## Caching (REST only)

Cache responses at API Gateway:
```bash
aws apigateway update-stage --rest-api-id ... --stage-name prod --patch-operations 'op=replace,path=/cacheClusterEnabled,value=true'
```

Per-method TTL. Significant cost ($14-$112/hr depending size).

Reduces Lambda invocations.

## WebSocket API

For real-time bidirectional:
- Chat
- Live dashboards
- Notifications
- Games

Routes:
- $connect
- $disconnect
- $default
- Custom routes

Each routes to Lambda.

To send to client:
```python
import boto3
client = boto3.client("apigatewaymanagementapi", endpoint_url=ENDPOINT)
client.post_to_connection(ConnectionId=connection_id, Data="...")
```

Cost: $1/M messages + $0.25/M connection-minutes.

## Request Validation (REST)

Validate against JSON schema:
```json
{
  "validateRequestBody": true,
  "requestSchema": {
    "type": "object",
    "required": ["name"],
    "properties": {"name": {"type": "string"}}
  }
}
```

Reject 400 if invalid. Saves Lambda invocation.

## Request/Response Mapping (REST)

Transform between client and backend:
- Add headers
- Restructure body
- Default values

VTL templates. Powerful; complex.

## Integration Types

- AWS_PROXY: Lambda proxy (simple)
- HTTP_PROXY: forward to HTTP backend
- AWS: AWS service direct (S3, DynamoDB etc.)
- HTTP: with transformation
- MOCK: no backend (return static)

For most: AWS_PROXY → Lambda.

## Function URLs vs API Gateway

Lambda Function URL:
- Direct HTTPS endpoint per function
- Cheap (no API GW cost)
- Lacks: custom domain (sort of), caching, throttling per-route, WAF
- For: internal / simple endpoints

API Gateway: full-featured.

## Cost Comparison

For 1M requests:
- HTTP API: $1.00
- REST API: $3.50
- Function URL: $0 (just Lambda cost)

Plus Lambda costs.

For high-volume: Function URL or HTTP API.

## CloudFront in Front

Add CloudFront in front for:
- Caching (REST API has its own cache; HTTP API needs CF)
- DDoS protection (WAF + Shield)
- Custom domain shared
- Global edge

```
User → CloudFront → API Gateway → Lambda
```

## Monitoring

CloudWatch metrics:
- Count
- 4XXError / 5XXError
- Latency
- IntegrationLatency

Per-API and per-route.

Access logs: detailed per request.

## Logging Configuration

```yaml
AccessLogSettings:
  DestinationArn: arn:aws:logs:...
  Format: $context.requestId $context.identity.sourceIp ...
```

Useful for audit / debug.

## Common Mistakes

- REST when HTTP fits (paying 3.5×)
- No throttling (DDoS risk)
- Heavy Lambda for static (cache)
- No validation (Lambda invoked for bad input)
- Open CORS (security)
- No custom domain (ugly URL)

## Best Practices

- HTTP API for new
- JWT authorizer (Cognito or external IdP)
- Throttle per-route
- Custom domain
- Validation (REST) or in Lambda
- WAF on CloudFront
- Access logs
- Monitor 5XX

## Deployment

Use IaC: SAM / Serverless Framework / CDK / Terraform.

```yaml
# SAM
Resources:
  MyApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: prod
      Auth:
        Authorizers:
          JwtAuth:
            JwtConfiguration: ...
```

## Versioning

URL path:
```
/v1/users
/v2/users
```

Or stage:
```
prod-v1.example.com
prod-v2.example.com
```

Plan from start.

## WAF Integration

Attach Web ACL to API GW (REST) or CloudFront:
- SQL injection
- XSS
- Rate-based
- Custom rules

Cost: ~$5/mo + rule cost.

## Quotas & Limits

- 10k req/sec per account default
- 30s timeout (no longer than Lambda)
- 10 MB payload
- 32 KB headers

For longer: WebSocket or polling pattern.

## Quick Refs

```bash
# Create HTTP API
aws apigatewayv2 create-api --name myApi --protocol-type HTTP --target arn:...

# Add route
aws apigatewayv2 create-route --api-id ... --route-key "POST /users" --target ...

# Deploy stage
aws apigatewayv2 create-stage --api-id ... --stage-name prod --auto-deploy
```

## Interview Prep

**Mid**: "HTTP API vs REST API."

**Senior**: "API Gateway + Cognito design."

**Staff**: "API at 100k QPS — architecture."

## Next Topic

→ Move to [L08/C08 — Container Services](../C08/README.md)
