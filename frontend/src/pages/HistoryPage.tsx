import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  FileSearch,
  Loader2,
  ChevronDown,
  ChevronUp,
  Eye,
  Ear,
  FileDown,
  Search,
  Filter
} from "lucide-react";
import { useHistory } from "../hooks/useHistory";
import { generateReport } from "../lib/pdf";
import type { UploadStatusResponse } from "../lib/api";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [filter, setFilter] = useState("all");
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const { data, loading } = useHistory(page, search, filter);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSearch(searchInput);
      setPage(1);
    }, 300);
    return () => clearTimeout(timeout);
  }, [searchInput]);

  useEffect(() => {
    setPage(1);
  }, [filter]);

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 md:py-20 fade-in-up">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-zinc-900 mb-2">
            History
          </h1>
          <p className="text-zinc-500 font-medium">Your cryptographic audit trail.</p>
        </div>

        {/* Sleek controls */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
            <input
              type="text"
              placeholder="Search hashes or names..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full sm:w-64 rounded-full border border-zinc-200 bg-white pl-10 pr-4 py-2.5 text-sm outline-none focus:border-zinc-400 focus:ring-4 focus:ring-zinc-100 transition-all font-medium placeholder:text-zinc-400 placeholder:font-normal"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="appearance-none w-full sm:w-40 rounded-full border border-zinc-200 bg-white pl-10 pr-10 py-2.5 text-sm outline-none focus:border-zinc-400 focus:ring-4 focus:ring-zinc-100 transition-all font-medium text-zinc-700"
            >
              <option value="all">All Status</option>
              <option value="REAL">Verified Real</option>
              <option value="FAKE">Detected Fake</option>
              <option value="failed">Failed</option>
            </select>
            <ChevronDown className="absolute right-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400 pointer-events-none" />
          </div>
        </div>
      </div>

      <div className="rounded-[2rem] border border-zinc-200/60 bg-white shadow-xl shadow-zinc-200/10 overflow-hidden delay-100 fade-in-up">
        {loading && (
          <div className="flex justify-center items-center py-32">
            <Loader2 className="h-6 w-6 text-zinc-400 animate-spin" />
          </div>
        )}

        {!loading && data && data.items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 text-center px-4">
            <div className="h-16 w-16 rounded-full bg-zinc-50 flex items-center justify-center mb-4 border border-zinc-100">
              <FileSearch className="h-6 w-6 text-zinc-400" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-900 mb-1">No records found</h3>
            <p className="text-sm text-zinc-500 max-w-sm mb-6">
              You haven't run any deepfake analyses yet, or no files match your search criteria.
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center justify-center rounded-full bg-zinc-900 px-6 py-2.5 text-sm font-medium text-white hover-scale transition-all"
            >
              Upload media
            </Link>
          </div>
        )}

        {!loading && data && data.items.length > 0 && (
          <div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left align-middle">
                <thead>
                  <tr className="border-b border-zinc-100 bg-zinc-50/50">
                    <th className="py-4 pl-6 pr-4 font-semibold text-zinc-500 uppercase tracking-widest text-[10px]">File & ID</th>
                    <th className="py-4 px-4 font-semibold text-zinc-500 uppercase tracking-widest text-[10px]">Date</th>
                    <th className="py-4 px-4 font-semibold text-zinc-500 uppercase tracking-widest text-[10px]">Verdict</th>
                    <th className="py-4 px-4 font-semibold text-zinc-500 uppercase tracking-widest text-[10px]">Status</th>
                    <th className="py-4 pr-6 pl-4 font-semibold text-zinc-500 uppercase tracking-widest text-[10px] text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                  {data.items.map((item) => (
                    <TableRow
                      key={item.id}
                      item={item}
                      expanded={expandedIds.has(item.id)}
                      onToggle={() => toggleExpanded(item.id)}
                    />
                  ))}
                </tbody>
              </table>
            </div>

            {data.pages > 1 && (
              <div className="flex items-center justify-between border-t border-zinc-100 px-6 py-4 bg-zinc-50/30">
                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">
                  Page {data.page} of {data.pages}
                </span>
                <div className="flex gap-2">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((p) => p - 1)}
                    className="rounded-full border border-zinc-200 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-wide disabled:opacity-40 disabled:pointer-events-none hover:bg-zinc-50 transition-colors"
                  >
                    Prev
                  </button>
                  <button
                    disabled={page === data.pages}
                    onClick={() => setPage((p) => p + 1)}
                    className="rounded-full border border-zinc-200 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-wide disabled:opacity-40 disabled:pointer-events-none hover:bg-zinc-50 transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function TableRow({
  item,
  expanded,
  onToggle,
}: {
  item: UploadStatusResponse;
  expanded: boolean;
  onToggle: () => void;
}) {
  const [pdfLoading, setPdfLoading] = useState(false);

  const handleDownloadPdf = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setPdfLoading(true);
    try {
      await generateReport(item);
    } finally {
      setPdfLoading(false);
    }
  };

  const isReal = item.verdict === "REAL";
  const isFake = item.verdict === "FAKE";

  return (
    <>
      <tr
        onClick={onToggle}
        className="group cursor-pointer hover:bg-zinc-50/80 transition-colors"
      >
        <td className="py-4 pl-6 pr-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg transition-colors ${expanded ? 'bg-zinc-200/50 text-zinc-900' : 'bg-zinc-100 text-zinc-500 group-hover:bg-zinc-200/50'}`}>
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </div>
            <div>
              <p className="font-medium text-zinc-900 truncate max-w-[200px] md:max-w-xs">{item.filename}</p>
              <p className="text-[10px] font-mono text-zinc-400 mt-0.5">{item.id.slice(0, 8)}</p>
            </div>
          </div>
        </td>
        <td className="py-4 px-4 text-zinc-500 font-medium">
          {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
        </td>
        <td className="py-4 px-4">
          {item.verdict ? (
            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${isReal ? "bg-green-100 text-green-700" : isFake ? "bg-red-100 text-red-700" : "bg-zinc-100 text-zinc-600"
              }`}>
              {item.verdict}
            </span>
          ) : (
            <span className="text-zinc-300">--</span>
          )}
        </td>
        <td className="py-4 px-4">
          <span className={`capitalize font-medium ${item.status === 'completed' ? 'text-zinc-900' : item.status === 'failed' ? 'text-red-500' : 'text-zinc-500'
            }`}>
            {item.status}
          </span>
        </td>
        <td className="py-4 pr-6 pl-4 text-right">
          <Link
            to={`/results/${item.id}`}
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center text-xs font-semibold uppercase tracking-wide text-zinc-900 hover:text-zinc-600 transition-colors"
          >
            View
          </Link>
        </td>
      </tr>

      {expanded && (
        <tr className="bg-zinc-50/50 border-t border-zinc-100">
          <td colSpan={5} className="py-6 px-6 md:px-16">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Deep Dive Details */}
              <div className="space-y-4">
                <h4 className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">Diagnostic Breakdown</h4>

                {item.confidence !== null && (
                  <div>
                    <div className="flex justify-between text-xs font-medium mb-1">
                      <span className="text-zinc-600">Total Confidence</span>
                      <span className="text-zinc-900">{Math.round(item.confidence * 100)}%</span>
                    </div>
                    <div className="w-full bg-zinc-200/60 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full ${isReal ? "bg-green-500" : "bg-red-500"}`}
                        style={{ width: `${Math.round(item.confidence * 100)}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="bg-white border border-zinc-100 p-3 rounded-xl shadow-sm shadow-zinc-200/10">
                    <div className="flex items-center gap-1.5 mb-1.5 text-zinc-500">
                      <Eye className="h-3.5 w-3.5" />
                      <span className="text-[10px] uppercase font-semibold tracking-wider">Visual</span>
                    </div>
                    <span className="text-base font-semibold text-zinc-900">
                      {item.visual_score !== null ? `${Math.round(item.visual_score * 100)}%` : "N/A"}
                    </span>
                  </div>
                  <div className="bg-white border border-zinc-100 p-3 rounded-xl shadow-sm shadow-zinc-200/10">
                    <div className="flex items-center gap-1.5 mb-1.5 text-zinc-500">
                      <Ear className="h-3.5 w-3.5" />
                      <span className="text-[10px] uppercase font-semibold tracking-wider">Audio</span>
                    </div>
                    <span className="text-base font-semibold text-zinc-900">
                      {item.audio_score !== null && item.audio_score > 0 ? `${Math.round(item.audio_score * 100)}%` : "N/A"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Metadata Action Area */}
              <div className="flex flex-col justify-between">
                <div>
                  <h4 className="text-[10px] font-semibold text-zinc-400 uppercase tracking-widest mb-3">Blockchain Verification</h4>
                  <div className="bg-white border border-zinc-100 p-3 rounded-xl shadow-sm shadow-zinc-200/10">
                    <p className="text-[10px] font-mono text-zinc-500 break-all leading-relaxed">
                      {item.file_hash ? item.file_hash : "Awaiting compute..."}
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 justify-end mt-6">
                  <button
                    onClick={handleDownloadPdf}
                    disabled={pdfLoading}
                    className="inline-flex items-center gap-1.5 rounded-full bg-white border border-zinc-200 px-4 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-50 transition-colors disabled:opacity-50"
                  >
                    {pdfLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileDown className="h-3.5 w-3.5" />}
                    Save Details
                  </button>
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
