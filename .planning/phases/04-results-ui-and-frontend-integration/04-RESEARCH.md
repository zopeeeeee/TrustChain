# Phase 4: Results UI and Frontend Integration - Research

**Researched:** 2026-03-06
**Domain:** React frontend UI (results display, history table, PDF export)
**Confidence:** HIGH

## Summary

Phase 4 transforms three placeholder/minimal pages into full-featured UI: (1) refactoring ResultsPage into a multi-card layout with verdict, modality breakdown, metadata, and post-result actions, (2) building a paginated, searchable, filterable history table with inline expandable rows, and (3) adding client-side PDF verification report generation. A backend list endpoint (GET /api/uploads) with pagination/search/filter is also required, plus a small schema change to expose `completed_at` for processing time calculation.

The existing codebase provides strong foundations: ResultsPage already renders verdict, confidence bar, and modality scores. The Upload model has `created_at` and `completed_at` fields (completed_at is set by the detection service). shadcn/ui is configured but no UI components are installed yet -- this phase should add Table, Badge, Button, Input, and Select components. jsPDF 4.x handles client-side PDF generation without server dependency.

**Primary recommendation:** Use jsPDF 4.x for PDF generation (client-side, no server dependency), add shadcn/ui components for consistent table/badge/button styling, and create a single new backend endpoint GET /api/uploads with query parameters for pagination, search, and filtering.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Multi-card layout for results: separate cards for verdict, modality breakdown, and metadata
- Add total processing time display (backend must track and return this)
- Add static decision basis placeholder text: "Prototype model -- verdict is based on untrained fusion weights"
- Keep existing fields: verdict badge, confidence bar, visual/audio scores, SHA-256 hash, speech detection info
- Add "Upload another video" button and "Share results link" (copy URL to clipboard) as post-result actions
- Add "Download PDF" button for completed analyses
- History columns: filename, submission date, verdict badge, confidence %, status, truncated file hash (8 chars), processing time
- Search by filename + filter by verdict (REAL/FAKE/failed)
- Chronological ordering (newest first), 10 items per page with pagination
- Empty state: friendly illustration/icon + "No analyses yet" message + CTA button linking to /upload
- Inline expandable rows: clicking a row expands to show verdict badge, confidence bar, visual/audio scores, truncated hash, and "View full results" link
- Download PDF button in each history row (for completed analyses)
- Client-side PDF generation (jsPDF or similar browser library)
- PDF content: TrustChain-AV branding/header, report title, generation timestamp, verdict, confidence, visual score, audio score, speech detected, SHA-256 hash, filename, date, total processing time, decision basis text, blockchain placeholder section
- Home page updated with quick stats: total analyses count, recent verdict breakdown, quick links to upload and history
- Results page: "Upload another video" and "Share results link" actions

### Claude's Discretion
- Exact card styling, spacing, and responsive breakpoints
- jsPDF vs other client-side PDF library choice
- Empty state illustration/icon selection
- Search/filter UI component design (search bar placement, filter dropdown vs tabs)
- Quick stats layout on home page
- Clipboard copy feedback (toast notification style)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RSLT-01 | Results screen shows REAL/FAKE verdict with color-coded confidence bar (green=real, red=fake) | Existing ResultsPage already has verdict badge + confidence bar; multi-card refactor enhances layout without changing logic |
| RSLT-02 | Results screen shows modality breakdown: visual score, audio score, whether audio was analyzed, decision basis | Existing ResultsPage has visual/audio score cards; add decision basis text and processing time from backend completed_at - created_at |
| HIST-01 | History page shows paginated table of all past analyses with status, date, verdict, and confidence | New GET /api/uploads backend endpoint + shadcn Table component + frontend pagination state |
| HIST-02 | User can click a history entry to view full results | Inline expandable rows with "View full results" Link to /results/:id |
| EXPT-01 | User can download a PDF verification report for any completed analysis | jsPDF 4.x client-side generation, shared utility function callable from both results and history pages |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| jsPDF | ^4.2.0 | Client-side PDF generation | 2.6M weekly downloads, mature API, no server dependency, lightweight |
| shadcn/ui | latest (CLI) | Pre-built accessible React components | Already configured in project (components.json exists), consistent with zinc theme |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| lucide-react | ^0.577.0 (installed) | Icons for empty state, actions, table | Already in project, use for all icon needs |
| clsx + tailwind-merge | (installed) | Conditional class merging | Already in project via cn() utility |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| jsPDF | @react-pdf/renderer | Heavier bundle, React component model for PDF is overkill for a simple report |
| jsPDF | pdfmake | Declarative JSON API is nice but adds 1MB+ to bundle, unnecessary for single-page report |
| Custom table | shadcn Table | shadcn Table is already consistent with project style, accessible, zero custom CSS needed |

**Recommendation for Claude's Discretion (PDF library):** Use jsPDF 4.x. It is the lightest option (~300KB), has the simplest API for a structured text report with no complex layouts, and the PDF content is text-heavy (no HTML rendering needed). Lazy-import it to keep initial bundle small.

**Installation:**
```bash
cd frontend && npm install jspdf
```

shadcn/ui components are added individually via the CLI:
```bash
cd frontend && npx shadcn@latest add table badge button input select
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── components/
│   ├── layout/          # NavBar (existing)
│   ├── ui/              # shadcn components (table, badge, button, input, select)
│   ├── results/         # ResultsPage sub-components (VerdictCard, ModalityCard, MetadataCard)
│   └── history/         # HistoryPage sub-components (HistoryTable, HistoryRow, ExpandedRow)
├── hooks/
│   ├── useJobStatus.ts  # Existing polling hook
│   └── useHistory.ts    # New: fetch paginated history with search/filter
├── lib/
│   ├── api.ts           # Add getUploads(), getStats() functions
│   ├── pdf.ts           # New: generateReport() using jsPDF
│   └── utils.ts         # Existing cn() utility
└── pages/
    ├── HomePage.tsx      # Enhanced with quick stats
    ├── UploadPage.tsx    # Unchanged
    ├── ResultsPage.tsx   # Multi-card refactor
    └── HistoryPage.tsx   # Full implementation
```

### Pattern 1: Multi-Card Results Layout
**What:** Break single results card into 3 separate cards: Verdict, Modality Breakdown, Metadata
**When to use:** ResultsPage for completed analyses
**Example:**
```typescript
// ResultsPage.tsx structure
{isCompleted && (
  <div className="space-y-6">
    <VerdictCard verdict={status.verdict} confidence={status.confidence} />
    <ModalityCard
      visualScore={status.visual_score}
      audioScore={status.audio_score}
      speechDetected={status.speech_detected}
      audioWeight={status.audio_weight}
    />
    <MetadataCard
      fileHash={status.file_hash}
      filename={status.filename}
      createdAt={status.created_at}
      processingTime={status.processing_time}
    />
    {/* Post-result actions */}
    <div className="flex gap-3">
      <Link to="/upload">Upload another video</Link>
      <button onClick={copyShareLink}>Share results link</button>
      <button onClick={downloadPdf}>Download PDF</button>
    </div>
  </div>
)}
```

### Pattern 2: Paginated History with Backend API
**What:** Frontend manages page/search/filter state, passes as query params to backend
**When to use:** HistoryPage
**Example:**
```typescript
// useHistory.ts hook
function useHistory(page: number, search: string, filter: string) {
  const [data, setData] = useState<HistoryResponse | null>(null);
  useEffect(() => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: "10",
      ...(search && { search }),
      ...(filter && filter !== "all" && { verdict: filter }),
    });
    fetch(`/api/uploads?${params}`).then(r => r.json()).then(setData);
  }, [page, search, filter]);
  return data;
}
```

### Pattern 3: Lazy-Loaded PDF Generation
**What:** Dynamic import of jsPDF only when user clicks "Download PDF"
**When to use:** Both ResultsPage and HistoryPage PDF download buttons
**Example:**
```typescript
// lib/pdf.ts
export async function generateReport(data: UploadStatusResponse) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF();

  // Header
  doc.setFontSize(20);
  doc.text("TrustChain-AV Verification Report", 20, 20);

  // Content sections...
  doc.setFontSize(12);
  doc.text(`Verdict: ${data.verdict}`, 20, 40);
  doc.text(`Confidence: ${Math.round((data.confidence ?? 0) * 100)}%`, 20, 50);
  // ... more fields

  doc.save(`trustchain-av-report-${data.id}.pdf`);
}
```

### Pattern 4: Inline Expandable Table Rows
**What:** Clicking a history row toggles an expanded section below it showing details
**When to use:** HistoryPage table
**Example:**
```typescript
// Track expanded rows by ID
const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

const toggleRow = (id: string) => {
  setExpandedIds(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });
};

// Render: for each item, render the main row + conditional expanded row
{items.map(item => (
  <React.Fragment key={item.id}>
    <TableRow onClick={() => toggleRow(item.id)} className="cursor-pointer">
      {/* columns */}
    </TableRow>
    {expandedIds.has(item.id) && (
      <TableRow>
        <TableCell colSpan={7}>
          {/* Expanded detail content */}
        </TableCell>
      </TableRow>
    )}
  </React.Fragment>
))}
```

### Anti-Patterns to Avoid
- **Fetching all uploads at once for history:** Use server-side pagination. Even for a prototype, this establishes the correct pattern and prevents performance issues.
- **Server-side PDF generation:** Adds backend complexity (wkhtmltopdf, Puppeteer, etc.) for no benefit -- client-side jsPDF is simpler and the data is already in the browser.
- **Duplicating API response types:** Keep a single `UploadStatusResponse` interface and extend it rather than creating parallel types.
- **Inline jsPDF code in components:** Extract PDF generation to `lib/pdf.ts` so both ResultsPage and HistoryPage can share it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF generation | Custom canvas/blob PDF creation | jsPDF 4.x | Well-tested text layout, font handling, save-as-download |
| Data table | Custom `<table>` with accessibility | shadcn Table | Accessible markup, consistent styling, responsive |
| Pagination controls | Custom prev/next buttons | Simple component with page state | Small enough to hand-build, but use shadcn Button for styling |
| Clipboard copy | Manual execCommand | `navigator.clipboard.writeText()` | Modern API, works in all current browsers |
| URL construction for share | String concatenation | `window.location.href` | Already contains the correct results URL |

**Key insight:** This phase is primarily UI composition -- combining existing data (already returned by the backend) with new layout components. The only backend work is the list endpoint and exposing processing_time.

## Common Pitfalls

### Pitfall 1: Missing Backend List Endpoint
**What goes wrong:** History page has no data source because GET /api/uploads doesn't exist yet
**Why it happens:** Backend only has POST /api/uploads and GET /api/uploads/:id/status
**How to avoid:** Plan 1 MUST create the backend list endpoint before frontend history implementation
**Warning signs:** 404 errors when history page loads

### Pitfall 2: Processing Time Not Exposed
**What goes wrong:** Frontend can't show processing time because it's not in the API response
**Why it happens:** Upload model has `created_at` and `completed_at` but the schema doesn't include `completed_at` or computed `processing_time`
**How to avoid:** Add `processing_time` (computed as seconds between created_at and completed_at) to UploadStatusResponse schema and the list endpoint response
**Warning signs:** Processing time shows as "N/A" or undefined

### Pitfall 3: jsPDF Bundle Size
**What goes wrong:** jsPDF (~300KB) loaded on every page, slowing initial load
**Why it happens:** Static import at top of component
**How to avoid:** Use dynamic `import("jspdf")` inside the download handler, only loaded when user clicks "Download PDF"
**Warning signs:** Lighthouse bundle size warnings

### Pitfall 4: Pagination Off-by-One
**What goes wrong:** Page 1 shows same items as page 2, or first page is empty
**Why it happens:** Inconsistent 0-based vs 1-based page indexing between frontend and backend
**How to avoid:** Standardize: frontend sends 1-based page numbers, backend uses `offset = (page - 1) * per_page`
**Warning signs:** Duplicate items across pages, total count mismatch

### Pitfall 5: Search Debouncing
**What goes wrong:** API called on every keystroke during filename search, causing excessive requests
**Why it happens:** No debounce on search input
**How to avoid:** Debounce search input by 300ms before triggering API call, or use a "Search" button
**Warning signs:** Network tab shows rapid-fire GET requests while typing

### Pitfall 6: Clipboard API Requires HTTPS
**What goes wrong:** `navigator.clipboard.writeText()` fails in development
**Why it happens:** Clipboard API requires secure context (HTTPS) in some browsers, but localhost is treated as secure
**How to avoid:** localhost works fine. Add a try/catch and fallback message if it fails in other environments
**Warning signs:** "Clipboard write failed" errors in non-localhost environments

## Code Examples

### Backend: GET /api/uploads List Endpoint
```python
# backend/app/api/uploads.py - new endpoint
from sqlalchemy import select, func, or_

@router.get("", response_model=UploadListResponse)
async def list_uploads(
    page: int = 1,
    per_page: int = 10,
    search: str | None = None,
    verdict: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List uploads with pagination, search, and filtering."""
    query = select(Upload).order_by(Upload.created_at.desc())

    if search:
        query = query.where(Upload.filename.ilike(f"%{search}%"))
    if verdict:
        if verdict == "failed":
            query = query.where(Upload.status == "failed")
        else:
            query = query.where(Upload.verdict == verdict.upper())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    uploads = result.scalars().all()

    return UploadListResponse(
        items=[_to_status_response(u) for u in uploads],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )
```

### Backend: Stats Endpoint for Home Page
```python
# backend/app/api/uploads.py - stats endpoint
@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregate statistics for the home page."""
    total = (await db.execute(select(func.count(Upload.id)))).scalar() or 0
    real_count = (await db.execute(
        select(func.count(Upload.id)).where(Upload.verdict == "REAL")
    )).scalar() or 0
    fake_count = (await db.execute(
        select(func.count(Upload.id)).where(Upload.verdict == "FAKE")
    )).scalar() or 0

    return {"total": total, "real": real_count, "fake": fake_count}
```

### Backend: Processing Time in Schema
```python
# backend/app/schemas/upload.py - add processing_time
class UploadStatusResponse(BaseModel):
    # ... existing fields ...
    processing_time: float | None = None  # seconds

# In the endpoint, compute:
processing_time = None
if upload.completed_at and upload.created_at:
    processing_time = (upload.completed_at - upload.created_at).total_seconds()
```

### Frontend: Clipboard Share with Toast Feedback
```typescript
const copyShareLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    // Show brief success feedback (toast or inline text)
    setShareCopied(true);
    setTimeout(() => setShareCopied(false), 2000);
  } catch {
    // Fallback: select text in a hidden input
    console.error("Clipboard write failed");
  }
};
```

### Frontend: PDF Generation Utility
```typescript
// lib/pdf.ts
import type { UploadStatusResponse } from "./api";

export async function generateReport(data: UploadStatusResponse): Promise<void> {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF();
  const margin = 20;
  let y = margin;

  // Header
  doc.setFontSize(22);
  doc.setTextColor(26, 26, 26);
  doc.text("TrustChain-AV", margin, y);
  y += 8;
  doc.setFontSize(14);
  doc.text("Verification Report", margin, y);
  y += 12;

  // Divider line
  doc.setDrawColor(200);
  doc.line(margin, y, 190, y);
  y += 10;

  // Report fields
  doc.setFontSize(11);
  const fields = [
    ["Generated", new Date().toLocaleString()],
    ["Filename", data.filename],
    ["Date Submitted", new Date(data.created_at).toLocaleString()],
    ["Verdict", data.verdict ?? "N/A"],
    ["Confidence", data.confidence !== null ? `${Math.round(data.confidence * 100)}%` : "N/A"],
    ["Visual Score", data.visual_score !== null ? `${Math.round(data.visual_score * 100)}%` : "N/A"],
    ["Audio Score", data.audio_score !== null && data.audio_score > 0
      ? `${Math.round(data.audio_score * 100)}%` : "N/A"],
    ["Speech Detected", data.speech_detected ? "Yes" : "No"],
    ["SHA-256 Hash", data.file_hash ?? "N/A"],
    ["Processing Time", data.processing_time ? `${data.processing_time.toFixed(1)}s` : "N/A"],
  ];

  for (const [label, value] of fields) {
    doc.setFont("helvetica", "bold");
    doc.text(`${label}:`, margin, y);
    doc.setFont("helvetica", "normal");
    doc.text(String(value), margin + 45, y);
    y += 7;
  }

  // Decision basis
  y += 5;
  doc.setFont("helvetica", "italic");
  doc.setFontSize(9);
  doc.text("Prototype model -- verdict is based on untrained fusion weights", margin, y);

  // Blockchain placeholder
  y += 15;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.text("Blockchain Verification", margin, y);
  y += 7;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text("Not yet registered. Blockchain registration available in a future update.", margin, y);

  doc.save(`trustchain-report-${data.id}.pdf`);
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| jsPDF 2.x imperative API | jsPDF 4.x with ESM + TypeScript types | 2024-2025 | Clean dynamic imports, tree-shakeable |
| Server-side PDF (wkhtmltopdf) | Client-side jsPDF | Ongoing trend | No server dependency, instant generation |
| shadcn/ui v0 (copy-paste components) | shadcn/ui CLI (`npx shadcn@latest add`) | 2024 | Consistent installs, auto-resolves dependencies |
| React Router v6 | React Router v7 (installed in project) | 2024-2025 | Same API patterns, useParams/Link work identically |

**Deprecated/outdated:**
- `document.execCommand("copy")`: Deprecated. Use `navigator.clipboard.writeText()` instead.
- jsPDF `addHTML()`: Removed in jsPDF 2+. Use the `.text()` and `.line()` API for structured reports.

## Open Questions

1. **Empty state illustration**
   - What we know: User wants friendly illustration/icon + "No analyses yet" message
   - What's unclear: Whether to use a lucide-react icon composition or an SVG illustration
   - Recommendation: Use lucide-react `FileSearch` or `BarChart3` icon at large size (64px) -- consistent with existing icon usage, no additional asset needed

2. **Toast notification for clipboard copy**
   - What we know: Need feedback when "Share results link" is clicked
   - What's unclear: Whether to install shadcn Sonner/toast or use inline feedback
   - Recommendation: Use simple inline text swap ("Share link" -> "Copied!" for 2s) to avoid adding a toast library. Lighter weight for a single use case.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (backend), no frontend test framework configured |
| Config file | backend/pyproject.toml [tool.pytest.ini_options] |
| Quick run command | `cd backend && python -m pytest tests/ -x -q` |
| Full suite command | `cd backend && python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RSLT-01 | Results page shows verdict with confidence bar | manual-only | Visual UI -- no frontend test framework | N/A |
| RSLT-02 | Results page shows modality breakdown and decision basis | manual-only | Visual UI -- no frontend test framework | N/A |
| HIST-01 | GET /api/uploads returns paginated list with search/filter | unit | `cd backend && python -m pytest tests/test_uploads.py -x -q` | Yes (extend) |
| HIST-02 | Click history entry navigates to results | manual-only | Navigation -- no frontend test framework | N/A |
| EXPT-01 | PDF download for completed analysis | manual-only | Client-side jsPDF -- no frontend test framework | N/A |

### Sampling Rate
- **Per task commit:** `cd backend && python -m pytest tests/test_uploads.py -x -q`
- **Per wave merge:** `cd backend && python -m pytest tests/ -v`
- **Phase gate:** Full backend suite green before verify

### Wave 0 Gaps
- [ ] `tests/test_uploads.py` -- extend with tests for GET /api/uploads list endpoint (pagination, search, filter, stats)
- No frontend test framework configured -- all UI requirements are manual-only verification

## Sources

### Primary (HIGH confidence)
- Project codebase inspection: ResultsPage.tsx, HistoryPage.tsx, HomePage.tsx, api.ts, upload model/schema, detection.py
- jsPDF npm page (v4.2.0 confirmed): https://www.npmjs.com/package/jspdf
- shadcn/ui components.json in project (new-york style, zinc base color, lucide icons)

### Secondary (MEDIUM confidence)
- jsPDF GitHub releases for v4.x feature set: https://github.com/parallax/jsPDF/releases
- PDF library comparison (bundle size, feature tradeoffs): https://npm-compare.com/@react-pdf/renderer,jspdf,pdfmake,react-pdf

### Tertiary (LOW confidence)
- None -- all findings verified against codebase or official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - jsPDF is mature and well-documented; shadcn/ui already configured in project
- Architecture: HIGH - patterns derived from existing codebase conventions (Tailwind, lucide-react, fetch API)
- Pitfalls: HIGH - identified from actual codebase gaps (missing list endpoint, processing_time not in schema)
- Backend changes: HIGH - inspected actual model, schema, and route code to identify exact changes needed

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable domain, no fast-moving dependencies)
