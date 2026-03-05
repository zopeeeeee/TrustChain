# Testing Patterns

**Analysis Date:** 2026-03-05

## Test Framework

**Runner:**
- No automated test framework is configured for either frontend or backend
- No `jest`, `vitest`, `pytest`, or any test runner config files exist
- No test scripts defined in `Frontend/package.json` (only `dev` and `build` scripts)
- No `pytest.ini`, `setup.cfg`, `conftest.py`, or `pyproject.toml` for backend testing

**Assertion Library:**
- Not applicable (no test framework)

**Run Commands:**
```bash
# No automated test commands available
# Manual backend smoke tests only:
python test_backend.py          # Requires running Flask server
python test_backend_check.py    # Same, slightly different version
```

## Test File Organization

**Location:**
- Two manual test scripts at project root:
  - `test_backend.py` - Backend API smoke test (original)
  - `test_backend_check.py` - Backend API smoke test (cleaned-up version)
- No frontend test files exist anywhere in the codebase
- No `__tests__/` directories, no `*.test.ts`, no `*.spec.ts` files

**Naming:**
- `test_backend.py` / `test_backend_check.py` at project root level

**Structure:**
```
Implementation/
├── test_backend.py          # Manual backend smoke test
├── test_backend_check.py    # Manual backend smoke test (variant)
├── Frontend/                # Zero test files
└── backend/                 # Zero test files
```

## Test Structure

**Suite Organization:**
The only tests are manual HTTP-based smoke tests that require a running Flask server. They are not unit tests and do not use any test framework.

```python
# Pattern from test_backend.py
def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("Health Check: PASSED")
            return True
        else:
            print("Health Check: FAILED")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to backend")
        return False

def main():
    print("Test 1: Health Check")
    health_ok = test_health()
    # ... sequential test execution
```

**Patterns:**
- Each test function makes an HTTP request and checks the response
- Tests print pass/fail status with emoji indicators
- `main()` orchestrates sequential test execution
- Tests exit early if health check fails (server not running)
- No assertions -- return boolean True/False
- No setup/teardown
- No test isolation

## Mocking

**Framework:** Not applicable

**Patterns:** No mocking is used anywhere in the codebase

**What to Mock (recommendations for future tests):**
- Frontend: `fetch()` API calls to backend
- Frontend: `URL.createObjectURL()`, `navigator.clipboard`
- Backend: `torch` model loading and inference, `cv2` image processing, `PIL.Image.open()`

**What NOT to Mock:**
- `cn()` utility function (pure function, test directly)
- Simple config objects and color mappings

## Fixtures and Factories

**Test Data:**
- `test_backend.py` expects a `test_image.jpg` file in the same directory for the analyze endpoint test
- No fixture files, no factory functions, no seed data

**Location:**
- No dedicated test data directory

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# No coverage tooling configured
```

## Test Types

**Unit Tests:**
- None exist for frontend or backend

**Integration Tests:**
- The two `test_backend*.py` scripts serve as manual integration/smoke tests
- They test the Flask API endpoints over HTTP
- Require the Flask server to be running (`python backend/app.py`)
- Test three endpoints: `/api/health`, `/api/info`, `/api/analyze`

**E2E Tests:**
- Not used. No Playwright, Cypress, or Selenium configuration.

## Common Patterns

**Async Testing:**
- Not applicable (no test framework)

**Error Testing:**
- The manual tests check for `ConnectionError` to detect if the server is not running
- No systematic error path testing

## What Needs Testing (Priority Recommendations)

**High Priority:**
1. `backend/app.py` - `analyze_image()` function: core business logic with score calculation
2. `backend/app.py` - `/api/analyze` route: input validation (file type, size, missing file)
3. `backend/app.py` - Graceful degradation when `torch` is unavailable (`MODEL_AVAILABLE = False`)

**Medium Priority:**
4. `Frontend/src/App.tsx` - `handleFileUpload()`: API call, response parsing, error handling
5. `Frontend/src/App.tsx` - `getStatusConfig()`: mapping prediction to display config
6. `Frontend/src/components/AuthenticityMeter.tsx` - SVG math (circumference, offset calculations)

**Low Priority:**
7. `Frontend/src/components/MetricCard.tsx` - color class mapping
8. `Frontend/src/components/BlockchainSection.tsx` - clipboard copy behavior
9. `Frontend/src/components/figma/ImageWithFallback.tsx` - error fallback rendering

## Recommended Test Setup

**Frontend (if adding tests):**
```bash
# Install Vitest (matches existing Vite setup)
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

Config: Add to `Frontend/vite.config.ts`:
```typescript
/// <reference types="vitest" />
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

Add to `Frontend/package.json` scripts:
```json
"test": "vitest",
"test:coverage": "vitest --coverage"
```

**Backend (if adding tests):**
```bash
pip install pytest pytest-cov
```

Use Flask's test client pattern:
```python
# backend/test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

---

*Testing analysis: 2026-03-05*
