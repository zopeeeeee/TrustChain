---
phase: 4
slug: results-ui-and-frontend-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (backend); manual (frontend) |
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
| 04-01-01 | 01 | 1 | RSLT-01 | manual | Visual inspection | N/A | pending |
| 04-01-02 | 01 | 1 | RSLT-02 | manual | Visual inspection | N/A | pending |
| 04-01-03 | 01 | 1 | HIST-01 | unit | `pytest tests/test_uploads.py` | Yes | pending |
| 04-01-04 | 01 | 1 | HIST-02 | manual | Visual inspection | N/A | pending |
| 04-02-01 | 02 | 2 | EXPT-01 | manual | Visual inspection | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers backend tests (pytest + pytest-asyncio from Phase 1)
- No frontend test framework -- all frontend requirements verified manually via UAT

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Multi-card results display | RSLT-01 | Browser UI interaction | Upload video, verify verdict card, modality card, metadata card layout |
| Modality breakdown with decision basis | RSLT-02 | Browser UI interaction | Verify visual score, audio score, speech info, and static decision basis text |
| History row click expands inline | HIST-02 | Browser UI interaction | Click history row, verify inline expansion with key fields and "View full results" link |
| PDF download | EXPT-01 | Browser file download | Click "Download PDF" on results page and history row, verify PDF opens with correct content |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
