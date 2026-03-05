---
phase: 1
slug: foundation-and-infrastructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend), vitest (frontend - deferred to later phases) |
| **Config file** | backend/pyproject.toml or backend/pytest.ini (Wave 0 installs) |
| **Quick run command** | `docker compose exec backend pytest tests/ -x -q` |
| **Full suite command** | `docker compose exec backend pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `docker compose exec backend pytest tests/ -x -q`
- **After every plan wave:** Run `docker compose exec backend pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INFR-01 | integration | `pytest tests/test_health.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INFR-04 | integration | `pytest tests/test_health.py` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | INFR-02 | integration | `pytest tests/test_database.py` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | INFR-05 | unit | `pytest tests/test_lifespan.py` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | INFR-03 | integration | `docker compose up --build` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/conftest.py` — shared fixtures (async client, test DB)
- [ ] `backend/tests/test_health.py` — stubs for INFR-01, INFR-04
- [ ] `backend/tests/test_database.py` — stubs for INFR-02
- [ ] `backend/tests/test_lifespan.py` — stubs for INFR-05
- [ ] `pytest` + `httpx` + `pytest-asyncio` — test framework install

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Docker Compose starts all 3 services | INFR-03 | Requires Docker daemon | Run `docker compose up`, verify 3 containers running |
| React shell loads with routing | INFR-01 (frontend) | Browser-based | Open http://localhost:5173, navigate between pages |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
