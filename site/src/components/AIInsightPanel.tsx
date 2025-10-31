"use client";

import { ProjectAnalysis } from "@/types";
import { Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface AIInsightPanelProps {
  data: ProjectAnalysis | null;
}

export default function AIInsightPanel({ data }: AIInsightPanelProps) {
  return (
    <div className="data-card p-8 fade-up" style={{ animationDelay: "0.6s" }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-[#54FE6D]/10">
          <Sparkles size={20} className="text-[#54FE6D]" />
        </div>
        <h3 className="text-xl font-semibold">AI Analysis</h3>
      </div>

      <div className="prose prose-invert max-w-none whitespace-pre-wrap">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data?.aiInsight}
        </ReactMarkdown>
      </div>

      <div className="mt-6 pt-6 border-t border-white/5">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold accent-glow mb-1">
              {data?.activityScore.overall}
            </div>
            <div className="text-xs text-[#F7F6F7]/50">Overall Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">
              {data?.activityScore.github}
            </div>
            <div className="text-xs text-[#F7F6F7]/50">GitHub</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">
              {data?.activityScore.twitter}
            </div>
            <div className="text-xs text-[#F7F6F7]/50">Twitter</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">
              {data?.activityScore.community}
            </div>
            <div className="text-xs text-[#F7F6F7]/50">Community</div>
          </div>
        </div>
      </div>
    </div>
  );
}
