import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCard } from "../components/UploadCard";
import { uploadVideo } from "../lib/api";
import { Loader2, CheckCircle2, Circle } from "lucide-react";

interface QueueItem {
  file: File;
  status: "pending" | "uploading" | "done" | "error";
}

export default function UploadPage() {
  const navigate = useNavigate();
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processQueue = useCallback(
    async (files: File[]) => {
      const items: QueueItem[] = files.map((file) => ({
        file,
        status: "pending" as const,
      }));
      setQueue(items);
      setError(null);
      setIsUploading(true);

      for (let i = 0; i < items.length; i++) {
        setQueue((prev) =>
          prev.map((item, idx) =>
            idx === i ? { ...item, status: "uploading" } : item
          )
        );

        try {
          const response = await uploadVideo(items[i].file);
          setQueue((prev) =>
            prev.map((item, idx) =>
              idx === i ? { ...item, status: "done" } : item
            )
          );
          setIsUploading(false);
          // Small delay for smooth visual transition before redirect
          setTimeout(() => navigate(`/results/${response.id}`), 400);
          return;
        } catch (e) {
          setQueue((prev) =>
            prev.map((item, idx) =>
              idx === i ? { ...item, status: "error" } : item
            )
          );
          setError(e instanceof Error ? e.message : "Upload failed");
          setIsUploading(false);
          return;
        }
      }

      setIsUploading(false);
    },
    [navigate]
  );

  const handleFilesSelected = useCallback(
    (files: File[]) => {
      if (isUploading) return;
      processQueue(files);
    },
    [isUploading, processQueue]
  );

  return (
    <div className="max-w-3xl mx-auto px-6 py-20 fade-in-up">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-zinc-900 mb-4">
          Initiate Analysis
        </h1>
        <p className="text-lg text-zinc-500 font-light max-w-xl mx-auto">
          Securely submit your media. Our dual-stream protocol will extract and compute spatial and temporal artifacts for cryptographic verification.
        </p>
      </div>

      <div className="delay-100 fade-in-up">
        <UploadCard
          onFilesSelected={handleFilesSelected}
          isUploading={isUploading}
          error={error}
        />
      </div>

      {queue.length > 0 && (
        <div className="mt-8 max-w-xl mx-auto delay-200 fade-in-up">
          <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-4 px-2">
            Transmission Queue
          </h2>
          <ul className="space-y-2">
            {queue.map((item, idx) => (
              <li
                key={idx}
                className="flex items-center gap-4 px-4 py-3 rounded-xl bg-white border border-zinc-100 shadow-sm shadow-zinc-200/20"
              >
                {item.status === "uploading" && (
                  <Loader2 className="h-5 w-5 text-zinc-900 animate-spin shrink-0" />
                )}
                {item.status === "done" && (
                  <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                )}
                {item.status === "pending" && (
                  <Circle className="h-5 w-5 text-zinc-300 shrink-0" />
                )}
                {item.status === "error" && (
                  <Circle className="h-5 w-5 text-red-500 shrink-0" />
                )}

                <div className="flex-1 truncate">
                  <p className={cn("text-sm font-medium truncate", item.status === "error" ? "text-red-600" : "text-zinc-900")}>
                    {item.file.name}
                  </p>
                  <p className="text-xs text-zinc-400">
                    {(item.file.size / (1024 * 1024)).toFixed(1)} MB
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// Inline helper exactly mapped for the upload page
function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(" ");
}
