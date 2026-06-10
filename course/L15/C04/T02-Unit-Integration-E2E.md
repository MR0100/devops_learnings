# L15/C04/T02 — Unit, Integration, E2E

## Learning Objectives

- Distinguish test types
- Implement effectively

## Unit Tests

Single function / class in isolation:
```python
def test_calculate_tax():
    result = calculate_tax(100, 0.08)
    assert result == 8.0
```

Fast (< 10 ms). Mock externals.

## Integration Tests

Multiple components working together:
```python
def test_create_user_writes_to_db():
    user = create_user("alice@example.com")
    db_user = User.query.filter_by(email="alice@example.com").first()
    assert db_user is not None
```

Real DB (Testcontainers).

## E2E Tests

Full user journey:
```javascript
test('user can checkout', async ({ page }) => {
  await page.goto('/');
  await page.click('button#add-to-cart');
  await page.click('a#checkout');
  await page.fill('input#email', 'alice@example.com');
  await page.click('button#pay');
  await expect(page).toHaveURL('/thank-you');
});
```

Real browser; real backend.

## Test Doubles

### Mock (Verify Interaction)
```python
@mock.patch('myapp.email.send_email')
def test_signup_sends_welcome(mock_send):
    signup('alice@example.com')
    mock_send.assert_called_once_with('alice@example.com', subject='Welcome')
```

### Stub (Return Value)
```python
def test_with_stub():
    mock_api = MagicMock(return_value={'user': 'alice'})
    result = process(mock_api)
    assert result == 'Hello alice'
```

### Fake (Real Implementation, Faster)
```python
# In-memory DB
class FakeDB:
    def __init__(self): self.data = {}
    def get(self, key): return self.data.get(key)
    def set(self, key, value): self.data[key] = value

def test_with_fake():
    db = FakeDB()
    db.set('user:1', {'name': 'alice'})
    assert db.get('user:1')['name'] == 'alice'
```

## Testcontainers

Real Docker containers for tests:
```python
from testcontainers.postgres import PostgresContainer

with PostgresContainer("postgres:15") as postgres:
    db_url = postgres.get_connection_url()
    # Run tests against real Postgres
```

For: integration realism without infra.

## Frameworks

### Python
- pytest (recommended)
- unittest (built-in)

### JS
- Jest, Vitest
- Mocha
- Playwright (E2E)

### Java
- JUnit 5
- Mockito
- Testcontainers (Java)

### Go
- testing (built-in)
- testify
- gomock

### Rust
- built-in `#[test]`

## pytest Patterns

```python
import pytest

@pytest.fixture
def db():
    db = SetupDB()
    yield db
    db.cleanup()

def test_create_user(db):
    user = create_user(db, "alice")
    assert user.id is not None

@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (5, 25),
    (10, 100),
])
def test_square(input, expected):
    assert square(input) == expected
```

## Speed Tips

### Parallel
```bash
pytest -n auto
jest --maxWorkers=4
```

### Selective
```bash
pytest -k "test_create"
pytest tests/test_user.py
```

### Profile
```bash
pytest --durations=10
```

Find slow tests.

## E2E Tools

### Playwright
- Modern
- Multi-browser
- Mobile emulation
- Auto-wait

```javascript
await page.click('button');
await expect(page.locator('h1')).toContainText('Welcome');
```

### Cypress
- Time-travel debugger
- Network stubbing
- Big community

### Selenium
- Mature
- Many language bindings
- Older API

For new: Playwright.

## Page Object Model

```javascript
class LoginPage {
  constructor(page) { this.page = page; }

  async login(email, password) {
    await this.page.fill('input#email', email);
    await this.page.fill('input#password', password);
    await this.page.click('button#submit');
  }
}

test('login', async ({ page }) => {
  const login = new LoginPage(page);
  await login.login('alice@example.com', 'pass');
  await expect(page).toHaveURL('/dashboard');
});
```

For: reusable, maintainable.

## API Tests

Between unit and full E2E:
```python
def test_api_create_user():
    response = client.post('/users', json={'email': 'alice@example.com'})
    assert response.status_code == 201
    assert response.json()['id'] > 0
```

For: API contracts.

## Snapshot Tests

```javascript
expect(component).toMatchSnapshot();
```

Initial run: stores snapshot.
Subsequent: compares.

For: UI regression.

Risk: snapshot rot. Review changes.

## Mutation Testing

Tools (e.g. Stryker, mutmut):
- Modify code
- Run tests
- See if tests catch

For: test quality.

## Property-Based

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_reverse_twice_is_identity(x):
    assert reverse(reverse(x)) == x
```

Random inputs; finds edge cases.

For: pure logic.

## Test Data

### Fixtures
Sample data files (JSON, SQL).

### Factories
```python
def make_user(**kwargs):
    defaults = {'name': 'alice', 'email': 'a@b.com'}
    return User(**{**defaults, **kwargs})
```

### Faker
```python
from faker import Faker
fake = Faker()
user = make_user(email=fake.email(), name=fake.name())
```

## Async Tests

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async():
    result = await fetch_data()
    assert result is not None
```

## Coverage Gates

```yaml
- run: coverage report --fail-under=80
```

For: prevent slipping.

## Best Practices

- Most unit
- Critical paths E2E
- Real DB for integration (Testcontainers)
- Parallel
- Fast: < 10 ms unit
- Independent
- Page Object for E2E
- Selective during dev

## Common Mistakes

- Mock everything (test mocks not code)
- Skip integration (miss real bugs)
- Flaky E2E (network, timing)
- Sequential when parallel possible
- Slow unit
- No coverage of critical paths

## Quick Refs

```bash
# Unit
pytest tests/unit/
jest

# Integration
pytest tests/integration/  # uses Testcontainers

# E2E
npx playwright test
cypress run

# Coverage
coverage run -m pytest
coverage report

# Parallel
pytest -n auto
```

## Interview Prep

**Junior**: "Test types."

**Mid**: "Mock vs fake."

**Senior**: "Test strategy."

**Staff**: "Testing at scale."

## Next Topic

→ [T03 — Contract Testing (Pact)](T03-Contract-Testing.md)
