"use client";

import { ProjectAnalysis } from "@/types";
import { Code, Server, Link, Cloud } from "lucide-react";

interface TechFingerprintCardProps {
  data: ProjectAnalysis | null;
}

export default function TechFingerprintCard({
  data,
}: TechFingerprintCardProps) {
  const categories = [
    {
      title: "Frontend",
      icon: Code,
      items: data?.techStack?.frontend,
      color: "#54FE6D",
    },
    {
      title: "Backend",
      icon: Server,
      items: data?.techStack?.backend,
      color: "#54FE6D",
    },
    {
      title: "Blockchain",
      icon: Link,
      items: data?.techStack?.blockchain,
      color: "#54FE6D",
    },
    {
      title: "Infrastructure",
      icon: Cloud,
      items: data?.techStack?.infrastructure,
      color: "#54FE6D",
    },
  ];

  return (
    <div className="data-card p-8 fade-up" style={{ animationDelay: "0.1s" }}>
      <h3 className="text-2xl font-semibold mb-6">Tech Fingerprint</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((category) => (
          <div key={category.title} className="space-y-3">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-lg bg-[#54FE6D]/10">
                <category.icon size={18} className="text-[#54FE6D]" />
              </div>
              <h4 className="font-semibold text-sm text-[#F7F6F7]/90">
                {category.title}
              </h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {category?.items?.map((item, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-md bg-[#232323] border border-white/5 text-sm text-[#F7F6F7]/80"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
