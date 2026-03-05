import { useState, useRef, useCallback } from "react";
import { UploadCloud, Loader2 } from "lucide-react";

const ALLOWED_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"];
const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

interface UploadCardProps {
  onFilesSelected: (files: File[]) => void;
  isUploading: boolean;
  error: string | null;
}

function validateFiles(files: File[]): string | null {
  for (const file of files) {
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Invalid format: "${file.name}". Supported: MP4, AVI, MOV, MKV`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File too large: "${file.name}" (${(file.size / (1024 * 1024)).toFixed(1)}MB). Max: 500MB`;
    }
  }
  return null;
}

export function UploadCard({
  onFilesSelected,
  isUploading,
  error,
}: UploadCardProps) {
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return;
      const files = Array.from(fileList);
      const err = validateFiles(files);
      if (err) {
        setValidationError(err);
        return;
      }
      setValidationError(null);
      onFilesSelected(files);
    },
    [onFilesSelected]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const displayError = validationError || error;

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative group overflow-hidden rounded-[2rem] border-2 border-dashed p-10 text-center transition-all duration-300 ease-out flex flex-col items-center justify-center min-h-[300px] ${dragOver
            ? "border-zinc-800 bg-zinc-50 scale-[1.01]"
            : "border-zinc-200 bg-white hover:border-zinc-300 hover:bg-zinc-50/50"
          }`}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/[0.01]" />

        <div className="relative z-10 flex flex-col items-center gap-5">
          <div className={`p-4 rounded-full transition-colors duration-300 ${dragOver ? "bg-zinc-200" : "bg-zinc-100 group-hover:bg-zinc-200"}`}>
            {isUploading ? (
              <Loader2 className="h-8 w-8 text-zinc-900 animate-spin" />
            ) : (
              <UploadCloud className="h-8 w-8 text-zinc-700" strokeWidth={1.5} />
            )}
          </div>

          <div className="space-y-1">
            <p className="text-base font-medium text-zinc-900">
              {isUploading ? "Processing media..." : "Drag & drop to analyze"}
            </p>
            <p className="text-sm text-zinc-500">
              or select files from your computer
            </p>
          </div>

          {!isUploading && (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-2 inline-flex items-center justify-center rounded-full bg-zinc-900 px-6 py-2.5 text-sm font-medium text-white shadow-md hover:bg-zinc-800 hover-scale focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2 transition-all"
            >
              Browse Files
            </button>
          )}

          <input
            ref={inputRef}
            type="file"
            accept=".mp4,.avi,.mov,.mkv"
            multiple
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>

      <div className="flex items-center justify-between mt-4 px-2">
        <p className="text-xs font-mono text-zinc-400">
          MP4, AVI, MOV, MKV (MAX 500MB)
        </p>
      </div>

      {displayError && (
        <p className="mt-3 px-2 text-sm text-red-500 font-medium fade-in-up">{displayError}</p>
      )}
    </div>
  );
}
