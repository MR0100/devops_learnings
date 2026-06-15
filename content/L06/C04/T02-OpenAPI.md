# L06/C04/T02 — OpenAPI / Swagger Specification

## Learning Objectives

- Write OpenAPI specs
- Generate clients / servers / docs

## What

OpenAPI (formerly Swagger): YAML/JSON spec that describes a REST API. Used to:
- Generate docs (Swagger UI, ReDoc)
- Generate clients in many languages
- Generate server stubs
- Mock servers for testing
- API gateways validate
- Contract testing

## Minimal Spec

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      required: [id, name, email]
      properties:
        id:
          type: integer
          example: 42
        name:
          type: string
        email:
          type: string
          format: email
    CreateUser:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
          minLength: 1
        email:
          type: string
          format: email
```

## Paths

```yaml
paths:
  /users/{id}:
    parameters:                       # path param shared by all methods
      - name: id
        in: path
        required: true
        schema:
          type: integer
    get:
      summary: Get user
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: Not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

## Schemas

```yaml
components:
  schemas:
    User:
      type: object
      required: [id]
      properties:
        id:
          type: integer
        name:
          type: string
        age:
          type: integer
          minimum: 0
          maximum: 150
        role:
          type: string
          enum: [admin, user, guest]
        tags:
          type: array
          items:
            type: string
        address:
          $ref: '#/components/schemas/Address'
```

## Discriminators (Polymorphism)

```yaml
Pet:
  type: object
  required: [species]
  properties:
    species:
      type: string
  discriminator:
    propertyName: species
    mapping:
      dog: '#/components/schemas/Dog'
      cat: '#/components/schemas/Cat'

Dog:
  allOf:
    - $ref: '#/components/schemas/Pet'
    - type: object
      properties:
        bark: { type: boolean }
```

## Security

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read: read data
            write: write data

security:
  - bearerAuth: []

paths:
  /secure:
    get:
      security:
        - bearerAuth: []
        - apiKey: []
```

## Examples

```yaml
responses:
  '200':
    description: OK
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/User'
        examples:
          alice:
            value:
              id: 1
              name: Alice
          bob:
            value:
              id: 2
              name: Bob
```

Shown in Swagger UI; great for docs.

## Tools

### Swagger UI
Interactive docs from spec. Hosted at `/docs`:
```bash
docker run -p 8080:8080 -e SWAGGER_JSON=/foo/swagger.yaml -v /local:/foo swaggerapi/swagger-ui
```

### ReDoc
Alternative; more polished:
```bash
npx redoc-cli serve swagger.yaml
```

### OpenAPI Generator
Generate client / server in many languages:
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g go \
  -o ./client
```

Languages: Python, Go, TypeScript, Java, C#, Ruby, etc.

### Prism (Mock Server)
```bash
npx prism mock openapi.yaml
# → http://localhost:4010 with mock responses based on schema/examples
```

### Spectral (Lint)
```bash
npx spectral lint openapi.yaml
```

## Workflow

**Design-first** (recommended):
1. Write OpenAPI spec
2. Review with consumers
3. Generate mocks; clients build against mocks
4. Generate server stubs; fill in
5. Contract tests verify implementation matches spec

**Code-first**:
1. Write code
2. Annotate / decorate
3. Auto-generate spec
4. Consumers use spec

Frameworks: FastAPI (Python, auto-generates), gin-swagger (Go), springdoc (Java), drf-spectacular (Django).

## FastAPI Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/users/{id}", response_model=User)
def get_user(id: int):
    return User(id=id, name="alice")
```

`/docs` → Swagger UI auto-generated. `/openapi.json` → spec.

## Validation

Spec defines validation rules:
- `minLength`, `maxLength`
- `minimum`, `maximum`
- `pattern` (regex)
- `format` (email, uri, date-time)
- `enum`
- `required`

API gateways (Kong, Apigee) can validate requests against spec; rejects bad early.

## Contract Testing

Pact / Schemathesis verify implementation matches spec:
```bash
schemathesis run http://localhost:8000/openapi.json
# Generates random valid requests; ensures 200; ensures responses match schema
```

## Versioning

```yaml
info:
  version: 1.2.0
servers:
  - url: https://api.example.com/v1
```

Different versions = different specs (or in-spec with paths).

## Common Mistakes

- `string` everywhere (use enums, formats)
- No `required` (everything optional)
- Inline schemas (no reuse; refactor to `components/schemas`)
- No examples (Swagger UI useless)
- No error responses defined
- Mixing v2 and v3 (use v3+; v2 deprecated)

## Best Practices

- One source of truth (spec is canonical)
- CI lints spec
- Generated clients in CI for changes
- Mock for early consumer dev
- Version bump on breaking changes
- Tag operations for grouping in UI
- Use `operationId` (used for generation)

## Quick Refs

```yaml
# Reusable schema with enum, format, required — referenced via $ref
components:
  schemas:
    Order:
      type: object
      required: [id, status, amount]
      properties:
        id:     { type: string, format: uuid }
        status: { type: string, enum: [pending, paid, shipped] }
        amount: { type: integer, minimum: 1 }
    Error:
      type: object
      required: [title, status]
      properties:
        title:  { type: string }
        status: { type: integer }

paths:
  /orders/{id}:
    get:
      operationId: getOrder        # drives client/codegen naming
      tags: [orders]
      parameters:
        - { name: id, in: path, required: true, schema: { type: string } }
      responses:
        "200": { content: { application/json: { schema: { $ref: "#/components/schemas/Order" } } } }
        "404": { content: { application/json: { schema: { $ref: "#/components/schemas/Error" } } } }
```

```bash
# Lint, mock, generate, contract-test
npx @redocly/cli lint openapi.yaml          # validate + style rules
npx @stoplight/prism-cli mock openapi.yaml  # mock server from spec
npx @openapitools/openapi-generator-cli generate \
    -i openapi.yaml -g python -o ./client   # typed client
schemathesis run openapi.yaml --url http://localhost:8000  # property/contract tests
```

```python
# FastAPI: code-first spec from Pydantic v2 models
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Order(BaseModel):
    id: str
    amount: int = Field(gt=0)

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order: ...
# OpenAPI JSON served at /openapi.json, Swagger UI at /docs
```

## Interview Prep

**Mid**: "Why OpenAPI?"

**Senior**: "Design-first vs code-first."

**Staff**: "Contract testing strategy."

## Next Topic

→ [T03 — gRPC and Protocol Buffers](T03-gRPC.md)
