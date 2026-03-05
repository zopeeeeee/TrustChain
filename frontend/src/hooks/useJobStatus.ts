import { useState, useEffect } from "react";
import { getUploadStatus } from "../lib/api";
import type { UploadStatusResponse } from "../lib/api";

const POLL_INTERVAL = 2000;
const TERMINAL_STATES = ["completed", "failed"];

export function useJobStatus(jobId: string | undefined) {
  const [status, setStatus] = useState<UploadStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let intervalId: ReturnType<typeof setInterval>;

    const poll = async () => {
      try {
        const data = await getUploadStatus(jobId);
        setStatus(data);
        if (TERMINAL_STATES.includes(data.status)) {
          clearInterval(intervalId);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unknown error");
        clearInterval(intervalId);
      }
    };

    poll(); // immediate first call
    intervalId = setInterval(poll, POLL_INTERVAL);

    return () => clearInterval(intervalId);
  }, [jobId]);

  return { status, error };
}
