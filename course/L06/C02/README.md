# L06/C02 — Python for DevOps

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Idiomatic-Python.md) | Idiomatic Python (PEP 8, Typing, Black, Ruff) | 1 hr |
| [T02](T02-Venv-Poetry-Uv.md) | Virtual Environments, Poetry, uv | 1 hr |
| [T03](T03-Standard-Library.md) | Standard Library Highlights (subprocess, pathlib, argparse) | 1.5 hr |
| [T04](T04-HTTP-Clients.md) | requests, httpx for HTTP | 1 hr |
| [T05](T05-Boto3-K8s-Client.md) | Boto3 for AWS, the Kubernetes Python Client | 1.5 hr |
| [T06](T06-Click-Typer.md) | Writing CLIs with Click / Typer | 1 hr |
| [T07](T07-Pytest.md) | Testing with pytest | 1 hr |

## Idiomatic Python (Modern)

### Style
- **PEP 8** — the style guide
- **Black** — opinionated formatter (no debate)
- **Ruff** — fast linter+formatter (Rust-based; ~100× faster than flake8/black)
- **mypy / pyright** — type checkers

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### Type Hints

```python
from typing import Optional

def deploy(service: str, version: str, dry_run: bool = False) -> bool:
    ...

# Modern (3.10+)
def get_pod(name: str | None = None) -> Pod | None:
    ...

# Generics (3.12+ syntax)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None
```

## Package Management (Modern)

### uv (Astral, Rust-based — RECOMMENDED in 2025+)
```bash
uv venv                            # create .venv
uv pip install requests
uv add requests                    # for project mgmt
uv run script.py
uv sync                            # install lockfile

# Faster than pip by 10-100×
```

### Poetry
```bash
poetry new myproj
poetry add requests
poetry install
poetry run python script.py
poetry build && poetry publish
```

### Plain venv + pip (still works)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip-tools to lock
```

## Standard Library Highlights

### subprocess
```python
import subprocess

# Simple
result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True, check=True)
print(result.stdout)

# Stream output
with subprocess.Popen(["long-cmd"], stdout=subprocess.PIPE, text=True) as proc:
    for line in proc.stdout:
        print(line, end="")

# DON'T use shell=True with user input (injection risk)
```

### pathlib
```python
from pathlib import Path

p = Path("/etc/nginx/nginx.conf")
p.exists()
p.read_text()
p.write_text("new content")
p.parent       # /etc/nginx
p.stem         # nginx
p.suffix       # .conf
p.name         # nginx.conf

for f in Path("logs").glob("**/*.log"):
    print(f)

Path("dir/sub").mkdir(parents=True, exist_ok=True)
```

### argparse
```python
import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--mode", choices=["dry", "wet"], default="dry")
    args = p.parse_args()

    if args.verbose:
        print(f"Processing {args.file}")
```

### logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)
log.info("starting")
log.error("failed", exc_info=True)
```

For production: structured JSON logging.
```python
import structlog
log = structlog.get_logger()
log.info("event", user_id=42, action="login")
```

### dataclasses / Pydantic

```python
from dataclasses import dataclass
@dataclass
class Service:
    name: str
    port: int = 8080

# Pydantic — validates input, used everywhere (FastAPI, etc.)
from pydantic import BaseModel
class Service(BaseModel):
    name: str
    port: int = 8080
    
s = Service.model_validate({"name": "api", "port": "8080"})  # parses str to int
```

## HTTP Clients

### requests (still standard)
```python
import requests

r = requests.get("https://api.example.com/users", timeout=5)
r.raise_for_status()
data = r.json()

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {token}"})
r = s.post("https://api.example.com/x", json={"foo": "bar"})
```

### httpx (async-capable, HTTP/2)
```python
import httpx

async with httpx.AsyncClient(http2=True) as client:
    r = await client.get("https://api.example.com/users")
```

## Boto3 (AWS)

```python
import boto3

s3 = boto3.client("s3")
s3.upload_file("local.txt", "my-bucket", "remote.txt")

# Paginators handle truncation
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket"):
    for obj in page.get("Contents", []):
        print(obj["Key"])

# EC2
ec2 = boto3.resource("ec2")
for i in ec2.instances.filter(Filters=[{"Name": "instance-state-name", "Values": ["running"]}]):
    print(i.id, i.private_ip_address)

# Assume role
sts = boto3.client("sts")
creds = sts.assume_role(RoleArn="arn:aws:iam::123:role/X", RoleSessionName="me")["Credentials"]
session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)
```

## Kubernetes Client

```python
from kubernetes import client, config

config.load_kube_config()    # or load_incluster_config() in a pod
v1 = client.CoreV1Api()

for p in v1.list_pod_for_all_namespaces().items:
    print(p.metadata.namespace, p.metadata.name, p.status.phase)

# Watch
from kubernetes.watch import Watch
w = Watch()
for event in w.stream(v1.list_pod_for_all_namespaces):
    print(event["type"], event["object"].metadata.name)
```

## CLIs with Typer (recommended) / Click

```python
import typer

app = typer.Typer()

@app.command()
def deploy(
    service: str,
    version: str,
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Deploy a service."""
    typer.echo(f"Deploying {service} v{version}")

@app.command()
def rollback(service: str):
    typer.echo(f"Rolling back {service}")

if __name__ == "__main__":
    app()
```

Run: `mycli deploy myservice v1.2.3 --dry-run`.

## Testing with pytest

```python
# test_foo.py
import pytest

def add(a, b): return a + b

def test_add():
    assert add(1, 2) == 3

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_param(a, b, expected):
    assert add(a, b) == expected

@pytest.fixture
def client():
    c = setup_client()
    yield c
    c.teardown()

def test_uses_client(client):
    assert client.connect()
```

```bash
pytest                    # discover and run
pytest -k "test_add"      # filter
pytest -x                 # stop at first failure
pytest --cov=src          # coverage
```

## Interview Themes

- "Walk me through a Python script you'd write to..."
- "Why use Typer/Click over argparse?"
- "Test isolation — how do you mock AWS?"
- "uv vs Poetry vs pip — what's the choice?"
- "How would you instrument structured logging?"
