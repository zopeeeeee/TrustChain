---
phase: 2
slug: upload-and-preprocessing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend), manual curl/browser (frontend) |
| **Config file** | backend/pyproject.toml |
| **Quick run command** | `docker compose exec backend pytest tests/ -x -q` |
| **Full suite command** | `docker compose exec backend pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

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
| 02-01-01 | 01 | 1 | UPLD-01 | integration | `pytest tests/test_upload.py` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | UPLD-02 | unit | `pytest tests/test_upload.py` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | UPLD-03 | integration | `pytest tests/test_upload.py` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | PREP-01 | integration | `pytest tests/test_preprocessing.py` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | PREP-02 | integration | `pytest tests/test_preprocessing.py` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 1 | PREP-03 | integration | `pytest tests/test_preprocessing.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_upload.py` — stubs for UPLD-01, UPLD-02, UPLD-03
- [ ] `backend/tests/test_preprocessing.py` — stubs for PREP-01, PREP-02, PREP-03
- [ ] pytest + httpx already installed from Phase 1

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drag-and-drop upload in browser | UPLD-01 | Browser interaction | Open localhost:5173/upload, drag video file onto upload card |
| Frontend status polling display | UPLD-03 | Visual verification | Upload a video, verify status updates appear on results page |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
