# L06/C02/T01 — Idiomatic Python (PEP 8, Typing, Black, Ruff)

## Learning Objectives

- Write modern idiomatic Python
- Use type hints
- Configure formatter + linter

## PEP 8 — Style

Standard Python style guide. Highlights:
- 4-space indent
- 79-char lines (or 88 if you use Black)
- snake_case for functions/variables
- PascalCase for classes
- UPPER_CASE for constants
- Two blank lines between top-level defs

## Modern Defaults

```python
"""Module docstring."""
from __future__ import annotations    # newer typing in older Python

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def process(path: Path, max_items: int = 100) -> list[dict[str, Any]]:
    """Process file and return parsed items."""
    with path.open() as f:
        data = json.load(f)
    return data[:max_items]


if __name__ == "__main__":
    process(Path("data.json"))
```

## Type Hints

```python
# Basic
def add(a: int, b: int) -> int:
    return a + b

# Optional / Union (Python 3.10+)
def maybe_get(key: str) -> dict | None:
    return cache.get(key)

# Collections
def names(users: list[User]) -> set[str]:
    return {u.name for u in users}

# Callable
from typing import Callable
def apply(f: Callable[[int], int], x: int) -> int:
    return f(x)

# TypedDict for dict shapes
from typing import TypedDict
class UserData(TypedDict):
    name: str
    age: int
```

## Static Type Check

```bash
pip install mypy
mypy src/
```

Catches type errors before runtime. Optional but recommended.

Alternative: pyright (Microsoft; faster).

## Black Formatter

Opinionated; no config.
```bash
pip install black
black .
```

Reformats all code consistently. End "style debates."

## Ruff (Modern Linter)

Rust-based. 100× faster than flake8 + black. Replaces both.

```bash
pip install ruff
ruff check .
ruff format .
```

Config in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "RUF"]
```

Codes:
- E: pycodestyle errors
- F: pyflakes
- I: isort (imports)
- B: bugbear (likely bugs)
- UP: pyupgrade (modernize)
- N: PEP 8 naming
- RUF: ruff-specific

## Idiomatic Patterns

### List Comprehensions
```python
# Pythonic
squares = [x*x for x in range(10) if x % 2 == 0]

# Less Pythonic
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x*x)
```

### Dict Comprehension
```python
{k: v.upper() for k, v in data.items()}
```

### Set Operations
```python
common = set1 & set2
unique_to_a = set1 - set2
```

### enumerate
```python
for i, x in enumerate(items):
    print(i, x)
```

### zip
```python
for name, age in zip(names, ages):
    print(name, age)
```

### Walrus (3.8+)
```python
if (n := len(items)) > 10:
    print(f"Too many: {n}")
```

### Context Managers
```python
with open("file") as f:
    data = f.read()
# file auto-closed
```

### Pathlib over os.path
```python
# Modern
p = Path("/etc/conf")
p.exists()
p.read_text()

# Old
os.path.exists("/etc/conf")
```

### f-strings
```python
name = "alice"
greeting = f"Hello, {name}"
debug = f"{value=}"     # value=42
```

## Common Anti-Patterns

```python
# Bad
if x == None: ...
# Good
if x is None: ...

# Bad
for i in range(len(items)): print(items[i])
# Good
for item in items: print(item)

# Bad
import *
# Good
from module import specific_name

# Bad
def foo(x = []):    # mutable default
    x.append(1)
# Good
def foo(x: list | None = None):
    if x is None: x = []
```

## Modern Project Layout

```
myproject/
├── pyproject.toml
├── README.md
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

## pyproject.toml

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.31"]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.12"
strict = true
```

## Testing with pytest

```python
def test_add():
    assert add(2, 3) == 5
```

```bash
pytest
```

Covered more in T07.

## Logging Setup

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
log = logging.getLogger(__name__)
log.info("starting")
```

For production: structlog (structured JSON).

## Interview Prep

**Junior**: "PEP 8 — what's it?"

**Mid**: "Why type hints?"

**Senior**: "Black + Ruff workflow."

## Next Topic

→ [T02 — Virtual Environments, Poetry, uv](T02-Venv-Poetry-Uv.md)
