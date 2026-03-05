import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useJobStatus } from "../hooks/useJobStatus";
import { generateReport } from "../lib/pdf";
import {
  Loader2,
  AlertCircle,
  Activity,
  Eye,
  Ear,
  Upload,
  Share2,
  FileDown,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";

const STATUS_LABELS: Record<string, string> = {
  uploading: "Uploading video...",
  extracting_frames: "Extracting video frames...",
  extracting_audio: "Extracting audio track...",
  visual_analysis: "Running visual analysis...",
  audio_analysis: "Running audio analysis...",
  computing_fusion: "Computing fusion verdict...",
  completed: "Analysis complete",
  failed: "Processing failed",
};

const ANALYSIS_STATES = [
  "visual_analysis",
  "audio_analysis",
  "computing_fusion",
];

const TERMINAL_STATES = ["completed", "failed"];

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { status, error } = useJobStatus(id);
  const [copied, setCopied] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);

  const handleDownloadPdf = async () => {
    if (!status) return;
    setPdfLoading(true);
    try {
      await generateReport(status);
    } finally {
      setPdfLoading(false);
    }
  };

  const isTerminal = status ? TERMINAL_STATES.includes(status.status) : false;
  const isFailed = status?.status === "failed";
  const isCompleted = status?.status === "completed";
  const isAnalyzing = status
    ? ANALYSIS_STATES.includes(status.status)
    : false;

  const handleShareLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API may not be available
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-12 md:py-20 fade-in-up">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-zinc-900">
          Analysis Results
        </h1>
        {isCompleted && (
          <div className="flex gap-2">
            <button
              onClick={handleShareLink}
              className="inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-wide text-zinc-700 hover:bg-zinc-50 hover-scale transition-all"
            >
              <Share2 className="h-3.5 w-3.5" />
              {copied ? "Copied" : "Share"}
            </button>
          </div>
        )}
      </div>

      {error && !status && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6 flex flex-col items-center justify-center text-center fade-in-up">
          <AlertCircle className="h-10 w-10 text-red-500 mb-3" />
          <h3 className="text-lg font-semibold text-red-900 mb-1">Retrieval Failed</h3>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!status && !error && (
        <div className="flex flex-col items-center justify-center py-24 space-y-4">
          <Loader2 className="h-8 w-8 text-zinc-400 animate-spin" />
          <span className="text-sm font-medium text-zinc-500 tracking-wide uppercase">Connecting to ledger...</span>
        </div>
      )}

      {/* Non-completed states: minimal card layout */}
      {status && !isCompleted && (
        <div className="rounded-3xl border border-zinc-200/60 bg-white shadow-xl shadow-zinc-200/20 p-8 space-y-8 fade-in-up">

          <div className="flex items-center justify-between pb-6 border-b border-zinc-100">
            <div>
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-1">
                Status
              </p>
              <div className="flex items-center gap-3">
                {!isTerminal && !isAnalyzing && (
                  <Loader2 className="h-5 w-5 text-zinc-400 animate-spin shrink-0" />
                )}
                {isAnalyzing && (
                  <Activity className="h-5 w-5 text-zinc-800 animate-pulse shrink-0" />
                )}
                {isFailed && (
                  <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
                )}
                <span
                  className={`text-2xl font-semibold tracking-tight ${isFailed ? "text-red-600" : "text-zinc-900"
                    }`}
                >
                  {STATUS_LABELS[status.status] || status.status}
                </span>
              </div>
            </div>
            {!isFailed && (
              <div className="h-12 w-12 rounded-full border-4 border-zinc-100 border-t-zinc-900 animate-spin" />
            )}
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">
                File
              </p>
              <p className="text-sm font-medium text-zinc-800 truncate">{status.filename}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">
                Started
              </p>
              <p className="text-sm font-medium text-zinc-800">
                {new Date(status.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-1.5">
                Job ID
              </p>
              <p className="font-mono text-xs text-zinc-500 bg-zinc-50 p-2 rounded-lg break-all border border-zinc-100">
                {status.id}
              </p>
            </div>
          </div>

          {isFailed && status.error_message && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 mt-6">
              <p className="text-sm text-red-700">{status.error_message}</p>
            </div>
          )}
        </div>
      )}

      {/* Completed analysis: multi-card layout */}
      {isCompleted && status && status.verdict && (
        <div className="space-y-6">
          {/* Main Verdict Card */}
          <div className={`relative overflow-hidden rounded-3xl border p-8 md:p-10 fade-in-up ${status.verdict === "REAL"
            ? "bg-gradient-to-br from-green-50 to-white border-green-100"
            : "bg-gradient-to-br from-red-50 to-white border-red-100"
            }`}
          >
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
              <div className="flex items-center gap-5">
                <div className={`p-4 rounded-full ${status.verdict === "REAL" ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"}`}>
                  {status.verdict === "REAL" ? <ShieldCheck className="h-8 w-8" strokeWidth={1.5} /> : <ShieldAlert className="h-8 w-8" strokeWidth={1.5} />}
                </div>
                <div>
                  <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-1">
                    Final Verdict
                  </p>
                  <h2 className={`text-4xl md:text-5xl font-extrabold tracking-tighter uppercase ${status.verdict === "REAL" ? "text-green-700" : "text-red-700"
                    }`}>
                    {status.verdict}
                  </h2>
                </div>
              </div>

              {/* High-end Confidence Ring / Display */}
              {status.confidence !== null && (
                <div className="text-left md:text-right">
                  <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-1">
                    Confidence
                  </p>
                  <p className="text-4xl md:text-5xl font-light tracking-tighter text-zinc-900">
                    {Math.round(status.confidence * 100)}<span className="text-2xl text-zinc-400">%</span>
                  </p>
                </div>
              )}
            </div>

            {/* Subtle background glow */}
            <div className={`absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl opacity-20 -mr-20 -mt-20 pointer-events-none ${status.verdict === "REAL" ? "bg-green-500" : "bg-red-500"
              }`} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Modality Breakdown */}
            <div className="rounded-3xl border border-zinc-200/60 bg-white shadow-xl shadow-zinc-200/10 p-8 delay-100 fade-in-up">
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-6">
                Engine Diagnostics
              </p>

              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Eye className="h-4 w-4 text-zinc-700" />
                      <span className="text-sm font-medium text-zinc-800">Spatial/Visual</span>
                    </div>
                    <span className="text-sm font-semibold text-zinc-900">
                      {status.visual_score !== null ? `${Math.round(status.visual_score * 100)}%` : "N/A"}
                    </span>
                  </div>
                  <div className="w-full bg-zinc-100 rounded-full h-1.5">
                    <div className="bg-zinc-800 h-1.5 rounded-full transition-all duration-1000" style={{ width: status.visual_score ? `${status.visual_score * 100}%` : '0%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Ear className="h-4 w-4 text-zinc-700" />
                      <span className="text-sm font-medium text-zinc-800">Temporal/Audio</span>
                    </div>
                    <span className="text-sm font-semibold text-zinc-900">
                      {status.audio_score !== null && status.audio_score > 0 ? `${Math.round(status.audio_score * 100)}%` : "N/A"}
                    </span>
                  </div>
                  <div className="w-full bg-zinc-100 rounded-full h-1.5 mb-2">
                    <div className="bg-zinc-500 h-1.5 rounded-full transition-all duration-1000" style={{ width: status.audio_score ? `${status.audio_score * 100}%` : '0%' }} />
                  </div>
                  <p className="text-[11px] font-mono text-zinc-400">
                    {status.speech_detected ? `SPEECH_FOUND (W=${status.audio_weight})` : "NO_SPEECH"}
                  </p>
                </div>
              </div>
            </div>

            {/* Metadata */}
            <div className="rounded-3xl border border-zinc-200/60 bg-white shadow-xl shadow-zinc-200/10 p-8 delay-200 fade-in-up">
              <p className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-6">
                Cryptographic Metadata
              </p>

              <div className="space-y-5">
                <div className="flex justify-between items-center pb-3 border-b border-zinc-50">
                  <span className="text-sm text-zinc-500">File</span>
                  <span className="text-sm font-medium text-zinc-900 truncate max-w-[150px]">{status.filename}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-zinc-50">
                  <span className="text-sm text-zinc-500">Time</span>
                  <span className="text-sm font-medium text-zinc-900">{status.processing_time ? `${status.processing_time.toFixed(2)}s` : "N/A"}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-zinc-50">
                  <span className="text-sm text-zinc-500">Date</span>
                  <span className="text-sm font-medium text-zinc-900">{new Date(status.created_at).toLocaleDateString()}</span>
                </div>
                {status.file_hash && (
                  <div>
                    <span className="text-sm text-zinc-500 block mb-1">SHA-256 Checksum</span>
                    <span className="text-[11px] font-mono bg-zinc-50 p-2 rounded-lg block break-all text-zinc-600 border border-zinc-100">
                      {status.file_hash}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8 delay-300 fade-in-up">
            <Link
              to="/upload"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 py-3.5 text-sm font-medium text-white shadow-md hover:bg-zinc-800 hover-scale transition-all focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2"
            >
              <Upload className="h-4 w-4" />
              Analyze Another
            </Link>
            <button
              onClick={handleDownloadPdf}
              disabled={pdfLoading}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full border border-zinc-200 bg-white px-8 py-3.5 text-sm font-medium text-zinc-800 shadow-sm hover:bg-zinc-50 hover-scale transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
              {pdfLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
              {pdfLoading ? "Generating..." : "Download Report"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
