import { mapBackendToProjectAnalysis } from "@/lib/utils";
import { ProjectAnalysis } from "@/types";
import { useState, useCallback } from "react";

interface AnalyzeResponse {
  // adjust fields to your API's actual output
  project_name?: string;
  summary?: string;
  funding?: any;
  metrics?: any;
  [key: string]: any;
}

export function useAnalyzeProject() {
  const [data, setData] = useState<ProjectAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (projectName: string) => {
    if (!projectName) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL ||
        "", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ project_name: projectName }),
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      const mapped = mapBackendToProjectAnalysis(data);
      setData(mapped);
    } catch (err: any) {
      console.error("❌ analyze error:", err);
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, analyze };
}
