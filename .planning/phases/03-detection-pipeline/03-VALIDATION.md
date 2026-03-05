---
phase: 3
slug: detection-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (backend) |
| **Config file** | backend/pyproject.toml |
| **Quick run command** | `docker compose exec backend pytest tests/ -x -q` |
| **Full suite command** | `docker compose exec backend pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `docker compose exec backend pytest tests/ -x -q`
- **After every plan wave:** Run `docker compose exec backend pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | DETC-01 | unit | `pytest tests/test_visual.py` | No W0 | pending |
| 03-01-02 | 01 | 1 | DETC-02 | unit | `pytest tests/test_audio.py` | No W0 | pending |
| 03-01-03 | 01 | 1 | DETC-03 | unit | `pytest tests/test_vad.py` | No W0 | pending |
| 03-01-04 | 01 | 1 | DETC-04 | unit | `pytest tests/test_fusion.py` | No W0 | pending |
| 03-02-01 | 02 | 1 | DETC-05 | manual | Visual inspection | N/A | pending |
| 03-02-02 | 02 | 2 | DETC-06 | unit | `pytest tests/test_uploads.py` | Yes | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_visual.py` — stubs for DETC-01 (mock ResNet-50, verify 2048-dim output)
- [ ] `backend/tests/test_audio.py` — stubs for DETC-02 (mock Wav2Vec2, verify 768-dim output)
- [ ] `backend/tests/test_vad.py` — stubs for DETC-03 (mock webrtcvad, speech/no-speech)
- [ ] `backend/tests/test_fusion.py` — stubs for DETC-04 (MLP forward pass, output range)
- [ ] `backend/tests/test_detection.py` — integration pipeline with mocked models
- [ ] pytest + pytest-asyncio already installed from Phase 1

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Multi-stage status display | DETC-05 | Browser interaction | Upload video, verify status labels cycle through: visual_analysis, audio_analysis, computing_fusion, completed |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
