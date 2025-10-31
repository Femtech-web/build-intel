"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import MatrixLoader from "@/components/MatrixLoader";
import TechFingerprintCard from "@/components/TechFingerprintCard";
import StatsCards from "@/components/StatsCards";
import AIInsightPanel from "@/components/AIInsightPanel";
import ExportButtons from "@/components/ExportButtons";
import { Search, Sparkles } from "lucide-react";
import { useAnalyzeProject } from "@/hooks/useAnalyzeProject";

export default function ScannerPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { data, loading, analyze } = useAnalyzeProject();

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    setError(null);

    await analyze(query);
  };

  const handleTrySample = (projectName: string) => {
    setSearchQuery(projectName);
    handleSearch(projectName);
  };

  return (
    <div className="min-h-screen bg-[#111111] overflow-x-hidden">
      <Header />

      <main className="pt-24 pb-20 ">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mx-auto mb-16">
            <div className="text-center mb-10">
              <h1 className="text-4xl md:text-5xl font-semibold mb-4 tracking-tight">
                BuildIntel <span className="accent-glow">Scanner</span>
              </h1>
              <p className="text-lg text-[#F7F6F7]/70">
                Enter project name to reveal its technology stack, funding and
                traction
              </p>
            </div>

            <div className="data-card p-6 space-y-4">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) =>
                      e.key === "Enter" && handleSearch(searchQuery)
                    }
                    placeholder="Enter ONLY project name..."
                    className="input-field w-full px-4 py-3 text-base"
                  />
                  <Search
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#F7F6F7]/40"
                    size={20}
                  />
                </div>
                <button
                  onClick={() => handleSearch(searchQuery)}
                  disabled={loading || !searchQuery.trim()}
                  className="btn-primary px-8 py-3 font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Scan
                </button>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <div className="text-[#F7F6F7]/50 text-sm">try:</div>

                {["Sentient", "Zora", "Base"].map((project) => (
                  <button
                    key={project}
                    onClick={() => handleTrySample(project.toLowerCase())}
                    className="px-3 py-1.5 rounded-md bg-[#54FE6D]/5 border border-[#54FE6D]/20 text-[#54FE6D] text-sm font-medium hover:bg-[#54FE6D]/10 transition-colors flex items-center gap-1.5"
                  >
                    <Sparkles size={14} />
                    {project}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {loading && (
            <div className="flex justify-center py-16">
              <MatrixLoader />
            </div>
          )}

          {error && (
            <div className="max-w-3xl mx-auto">
              <div className="data-card bg-red-500/5 border-red-500/20 p-6 text-center">
                <p className="text-[#F7F6F7]/90 font-medium">{error}</p>
              </div>
            </div>
          )}

          {data && !loading && (
            <div id="results-container" className="max-w-6xl mx-auto space-y-6">
              <div className="data-card p-6 fade-up">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <h2 className="text-3xl font-semibold mb-2">
                      {data.projectName}
                    </h2>

                    <div className="flex flex-col sm:flex-row sm:flex-wrap items-start sm:items-center gap-3 text-sm">
                      {data?.url?.map((url: string, idx: number) => (
                        <a
                          key={`web-${idx}`}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#54FE6D] hover:underline"
                        >
                          {url}
                        </a>
                      ))}
                      {data.url?.length > 3 && (
                        <span className="text-[#F7F6F7]/50">
                          +{data.url.length - 3} more
                        </span>
                      )}

                      {data?.discovery?.githubs
                        ?.slice(0, 2)
                        .map((gh: string, idx: number) => (
                          <a
                            key={`gh-${idx}`}
                            href={gh}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#54FE6D] hover:underline"
                          >
                            {gh.replace("https://", "").replace("www.", "")}
                          </a>
                        ))}
                      {data?.discovery?.githubs?.length > 2 && (
                        <span className="text-[#F7F6F7]/50">
                          +{data?.discovery?.githubs?.length - 2} more
                        </span>
                      )}

                      {data.discovery?.twitters
                        ?.slice(0, 2)
                        .map((tw: string, idx: number) => (
                          <a
                            key={`tw-${idx}`}
                            href={tw}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#54FE6D] hover:underline"
                          >
                            {tw.replace("https://twitter.com/", "@")}
                          </a>
                        ))}
                      {data.discovery?.twitters?.length > 2 && (
                        <span className="text-[#F7F6F7]/50">
                          +{data?.discovery?.twitters?.length - 2} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-left md:text-right">
                    <div className="text-xs text-[#F7F6F7]/50 mb-1">
                      Analyzed
                    </div>
                    <div className="font-medium text-sm">
                      {new Date(data.analyzedAt).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>

              <TechFingerprintCard data={data} />

              <StatsCards data={data} />

              <AIInsightPanel data={data} />

              <div className="flex justify-center pt-4">
                <ExportButtons data={data} />
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
