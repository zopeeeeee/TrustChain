import { useState, useEffect } from "react";
import { getUploads } from "../lib/api";
import type { UploadListResponse } from "../lib/api";

export function useHistory(page: number, search: string, filter: string) {
  const [data, setData] = useState<UploadListResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const params: {
      page: number;
      per_page: number;
      search?: string;
      verdict?: string;
    } = { page, per_page: 10 };

    if (search) {
      params.search = search;
    }
    if (filter !== "all") {
      params.verdict = filter;
    }

    getUploads(params)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch(() => {
        // silently handle errors
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [page, search, filter]);

  return { data, loading };
}
