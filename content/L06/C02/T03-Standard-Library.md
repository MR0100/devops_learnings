# L06/C02/T03 — Standard Library Highlights (subprocess, pathlib, argparse)

## Learning Objectives

- Use Python's stdlib effectively
- Avoid reinventing the wheel

## subprocess

Run shell commands.

```python
import subprocess

# Run; capture output; check exit
result = subprocess.run(
    ["kubectl", "get", "pods"],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)

# Don't use shell=True with user input (injection)
# Safe
subprocess.run(["grep", pattern, file])

# Dangerous
subprocess.run(f"grep {pattern} {file}", shell=True)

# Stream output
with subprocess.Popen(["long-cmd"], stdout=subprocess.PIPE, text=True) as proc:
    for line in proc.stdout:
        print(line, end="")
```

## pathlib

Modern file paths.

```python
from pathlib import Path

p = Path("/etc/nginx/nginx.conf")
p.exists()
p.is_file()
p.is_dir()
p.read_text()
p.write_text("data")
p.parent                            # /etc/nginx
p.stem                              # nginx
p.suffix                            # .conf
p.name                              # nginx.conf

# Iterate
for f in Path("logs").glob("**/*.log"):
    print(f)

# Create dirs
Path("dir/sub").mkdir(parents=True, exist_ok=True)
```

## argparse

CLI args.

```python
import argparse

p = argparse.ArgumentParser(description="My tool")
p.add_argument("file", help="Input file")
p.add_argument("--verbose", "-v", action="store_true")
p.add_argument("--count", type=int, default=10)
p.add_argument("--mode", choices=["dry", "wet"], default="dry")
args = p.parse_args()

print(args.file, args.verbose, args.count, args.mode)
```

For modern: typer or click (covered in T06).

## logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)

log.debug("debug message")
log.info("starting")
log.warning("careful")
log.error("failed")
log.exception("caught exception", exc_info=True)
```

## os

```python
import os
os.environ["MY_VAR"]
os.environ.get("VAR", "default")
os.cpu_count()
os.getpid()
```

## datetime

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
iso = now.isoformat()                     # 2026-06-09T12:00:00+00:00
parsed = datetime.fromisoformat(iso)

later = now + timedelta(hours=2)
```

## json / yaml

```python
import json
data = json.loads(json_str)
output = json.dumps(data, indent=2)
json.dump(data, f)
```

For YAML: `pip install pyyaml`
```python
import yaml
data = yaml.safe_load(yaml_str)
output = yaml.safe_dump(data)
```

## hashlib

```python
import hashlib
h = hashlib.sha256(b"hello").hexdigest()
```

## itertools

```python
from itertools import chain, groupby, accumulate, product, combinations

list(chain([1,2], [3,4]))                  # [1,2,3,4]
list(accumulate([1,2,3,4]))                # [1,3,6,10]
list(product([1,2], ['a','b']))            # cartesian
```

## collections

```python
from collections import Counter, defaultdict, OrderedDict

c = Counter("hello")                       # {'l': 2, 'h': 1, ...}
c.most_common(3)

d = defaultdict(list)
d["key"].append(1)                         # no KeyError
```

## functools

```python
from functools import lru_cache, partial, reduce

@lru_cache(maxsize=100)
def expensive(x):
    return ...

f = partial(some_func, x=1)
sum_v = reduce(lambda a, b: a + b, nums, 0)
```

## tempfile

```python
import tempfile

with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
    tmp.write("data")
    path = tmp.name
# Use path, then delete

with tempfile.TemporaryDirectory() as tmpdir:
    # use tmpdir; auto-cleaned
```

## concurrent.futures

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process, items))

# For CPU-bound: ProcessPoolExecutor
```

## asyncio

```python
import asyncio

async def fetch(url):
    # async HTTP via httpx
    ...

async def main():
    results = await asyncio.gather(*[fetch(u) for u in urls])

asyncio.run(main())
```

## urllib.request

For dependency-free HTTP:
```python
from urllib.request import urlopen
import json
data = json.loads(urlopen("https://api.example.com").read())
```

But `requests` / `httpx` are much nicer.

## Useful Helper Patterns

```python
# Defaults dict
config = data.get("config", {}).get("setting", "default")

# Or use pydantic for structured config

# Read env with type
debug = os.environ.get("DEBUG", "0") == "1"
```

## Common Mistakes

- Calling `subprocess.run(cmd, shell=True)` with interpolated user input — that is shell injection. Pass a list and leave `shell=False`.
- Forgetting `check=True`, so a failing command returns silently and the script marches on as if it succeeded.
- Building paths with string concatenation/`os.path.join` instead of `pathlib`, breaking on Windows and hiding bugs.
- Using naive `datetime.now()` for anything cross-system; store and compare in UTC with `datetime.now(tz=UTC)`.
- Reaching for `requests`/`httpx` deps inside a tiny tool when `urllib.request` from the stdlib would do.
- Spawning threads for CPU-bound work — the GIL serializes it; use `ProcessPoolExecutor` instead.

## Best Practices

- Default to `subprocess.run([...], check=True, capture_output=True, text=True)` and inspect `CompletedProcess` rather than shelling out.
- Use `pathlib.Path` everywhere: `Path(__file__).parent`, `p.read_text()`, `p.glob("*.yaml")`, `p.mkdir(parents=True, exist_ok=True)`.
- Pick the right concurrency tool: `ThreadPoolExecutor` for I/O-bound, `ProcessPoolExecutor` for CPU-bound, `asyncio` for high-fan-out network calls.
- Configure logging once via `logging.basicConfig(...)` and use module-level `log = logging.getLogger(__name__)`; never `print()` for diagnostics.
- Use `tempfile.TemporaryDirectory()` as a context manager so scratch files are always cleaned up, even on error.
- Keep timestamps timezone-aware and serialized as ISO 8601 (`dt.isoformat()`).

## Quick Refs

```python
import subprocess, pathlib, argparse, logging
from datetime import datetime, UTC

# subprocess — safe by default
r = subprocess.run(["kubectl", "get", "pods", "-o", "json"],
                   check=True, capture_output=True, text=True)
pods = r.stdout

# pathlib
p = pathlib.Path("config") / "app.yaml"
p.parent.mkdir(parents=True, exist_ok=True)
text = p.read_text() if p.exists() else ""

# argparse
ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

# utc timestamp
ts = datetime.now(UTC).isoformat()
```

```python
# concurrency selector
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
with ThreadPoolExecutor(max_workers=10) as ex:   # I/O-bound
    results = list(ex.map(fetch, urls))
# ProcessPoolExecutor for CPU-bound; asyncio for very high fan-out
```

## Interview Prep

**Mid**: "subprocess.run safely."

**Senior**: "Pathlib over os.path — why?"

**Staff**: "Async vs threads — when each?"

## Next Topic

→ [T04 — requests, httpx for HTTP](T04-HTTP-Clients.md)
