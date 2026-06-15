# L06/C02/T07 — Testing with pytest

## Learning Objectives

- Write tests for DevOps Python code
- Use fixtures, mocking, parametrization

## Why Test DevOps Code

Tools that touch infrastructure: bugs = outages. Tests catch:
- Wrong API calls
- Bad config parsing
- Auth failures
- Edge cases in input data

## pytest Basics

```bash
pip install pytest
```

```python
# test_basic.py
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -2) == -3
```

```bash
pytest
pytest test_basic.py
pytest test_basic.py::test_add
pytest -v                    # verbose
pytest -x                    # stop on first fail
pytest -k "add"              # match name
```

## Assertions

```python
assert x == 5
assert x != 0
assert "abc" in s
assert isinstance(x, int)

# Pytest rewrites assert for good error messages
```

## Exceptions

```python
import pytest

def test_raises():
    with pytest.raises(ValueError):
        int("not a number")

def test_message():
    with pytest.raises(ValueError, match="invalid"):
        int("bad")
```

## Fixtures

Setup/teardown reusable across tests.

```python
@pytest.fixture
def sample_data():
    return {"name": "alice", "id": 1}

def test_user(sample_data):
    assert sample_data["name"] == "alice"
```

### Scope
```python
@pytest.fixture(scope="session")  # once per pytest run
def db_connection():
    conn = create_conn()
    yield conn                    # test runs here
    conn.close()                  # teardown
```

Scopes: function (default), class, module, session.

### Built-in Fixtures
```python
def test_tmp(tmp_path):           # auto-cleaned temp dir
    f = tmp_path / "test.txt"
    f.write_text("data")
    assert f.exists()

def test_capsys(capsys):          # capture stdout/stderr
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

def test_monkeypatch(monkeypatch):
    monkeypatch.setenv("MY_VAR", "value")
    # In test, env var is set
```

## Parametrize

Run test with multiple inputs:
```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

3 tests run; each value shown if fails.

## Mocking

`unittest.mock` or `pytest-mock`.

```python
from unittest.mock import patch, MagicMock

@patch("mymodule.requests.get")
def test_api(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    mock_get.return_value.status_code = 200
    
    result = my_func_that_calls_api()
    
    assert result == "ok"
    mock_get.assert_called_with("https://api.example.com")
```

### pytest-mock (cleaner)
```python
def test_api(mocker):
    mock_get = mocker.patch("mymodule.requests.get")
    mock_get.return_value.json.return_value = {"status": "ok"}
    
    result = my_func()
    assert result == "ok"
```

### Mock boto3
```python
@patch("boto3.client")
def test_s3(mock_client):
    mock_s3 = MagicMock()
    mock_client.return_value = mock_s3
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "b1"}]}
    
    result = list_my_buckets()
    assert result == ["b1"]
```

### moto (for AWS)
Mocks AWS services in-memory:
```python
from moto import mock_s3
import boto3

@mock_s3
def test_s3():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="my-bucket")
    s3.put_object(Bucket="my-bucket", Key="x", Body=b"data")
    
    objs = s3.list_objects_v2(Bucket="my-bucket")
    assert objs["Contents"][0]["Key"] == "x"
```

Much better than mocking each call.

## Coverage

```bash
pip install pytest-cov
pytest --cov=myapp --cov-report=html
# Open htmlcov/index.html
```

Coverage targets in CI: 70-90% typical.

## Plugins

- `pytest-xdist`: parallel (`pytest -n 4`)
- `pytest-cov`: coverage
- `pytest-mock`: easier mocking
- `pytest-asyncio`: async test
- `pytest-bdd`: BDD style

## Async Tests
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async():
    result = await some_async_func()
    assert result == "ok"
```

## conftest.py

Shared fixtures across tests:
```python
# conftest.py — auto-loaded
@pytest.fixture
def api_client():
    return Client(base_url="http://test")

# In any test:
def test_x(api_client):
    ...
```

## Markers

```python
@pytest.mark.slow
def test_slow():
    ...

@pytest.mark.skip(reason="WIP")
def test_skip():
    ...

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix():
    ...

@pytest.mark.xfail
def test_known_fail():
    assert False    # expected to fail; OK
```

Run subset:
```bash
pytest -m "not slow"
pytest -m slow
```

## Integration vs Unit

Unit: mock everything external; fast.
Integration: hit real systems (test DB, moto for AWS); slower.

Split:
```bash
pytest tests/unit/             # fast; PR check
pytest tests/integration/      # nightly
```

## CI Integration

```yaml
- name: Tests
  run: |
    pytest --cov=myapp --cov-report=xml --junitxml=junit.xml
- uses: codecov/codecov-action@v3
```

## Common Mistakes

- Tests that depend on each other (use fresh fixtures)
- Mocking too much (tests pass but bugs slip)
- No coverage gate
- Brittle tests (assert exact strings instead of structure)
- Slow tests not marked → CI slow

## Test Organization

```
myapp/
├── src/
│   └── myapp/
└── tests/
    ├── unit/
    │   └── test_parser.py
    ├── integration/
    │   └── test_s3.py
    └── conftest.py
```

## Hypothesis (Property-Based)

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_commutative(a, b):
    assert a + b == b + a
```

Generates many inputs automatically; finds edge cases humans miss.

## Best Practices

- Keep each test independent and order-agnostic; build state from fixtures, never from a previous test's side effects.
- Mock at the boundary (the AWS/HTTP/K8s client), not your own logic — over-mocking lets real bugs pass.
- Parametrize instead of copy-pasting near-identical tests; it shrinks code and names each case in the report.
- Mark slow/integration tests (`@pytest.mark.integration`) so the fast unit suite gates every commit and slow ones run separately.
- Assert on structure/values, not exact log strings or whitespace, so refactors don't cause false failures.
- Enforce a coverage gate in CI (`--cov-fail-under`) but treat coverage as a floor, not the goal.

## Quick Refs

```python
import pytest

@pytest.mark.parametrize("value,expected", [(2, 4), (3, 9), (0, 0)])
def test_square(value, expected):
    assert square(value) == expected

def test_raises():
    with pytest.raises(ValueError, match="empty"):
        parse("")

@pytest.fixture
def tmp_config(tmp_path):           # built-in tmp_path fixture
    p = tmp_path / "config.yaml"
    p.write_text("region: eu-west-1\n")
    return p
```

```python
# Mock the boundary, not your code
from unittest.mock import patch

def test_upload(monkeypatch):
    with patch("mymod.boto3.client") as m:
        m.return_value.upload_file.return_value = None
        upload("file.txt")
        m.return_value.upload_file.assert_called_once()
```

```bash
pytest -q                          # quiet run
pytest -k "upload and not slow"    # select by expression
pytest -m integration              # run a marker group
pytest --cov=src --cov-fail-under=80
pytest -x --lf                     # stop at first fail, rerun last-failed
```

## Interview Prep

**Junior**: "Write a test for `is_palindrome`."

**Mid**: "Mock vs real test — when each?"

**Senior**: "Test pyramid; flakiness; coverage strategy."

## Next Topic

→ Move to [L06/C03 — Go for DevOps](../C03/README.md)
