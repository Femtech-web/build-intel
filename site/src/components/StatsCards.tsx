"use client";

import { ProjectAnalysis } from "@/types";
import { Github, Users, DollarSign, Twitter, BarChart3 } from "lucide-react";

interface StatsCardsProps {
  data: ProjectAnalysis | null;
}

export default function StatsCards({ data }: StatsCardsProps) {
  const githubAndOverall = [
    {
      label: "Stars",
      value: data?.githubStats?.stars?.toLocaleString() || "—",
    },
    {
      label: "Forks",
      value: data?.githubStats?.forks?.toLocaleString() || "—",
    },
    {
      label: "Commits",
      value: data?.githubStats?.commits?.toLocaleString() || "—",
    },
    {
      label: "Contributors",
      value: data?.githubStats?.contributors?.toLocaleString() || "—",
    },
    {
      label: "Top Language",
      value: data?.githubStats?.topLanguages?.[0] || "—",
    },
    {
      label: "Overall Score",
      value: `${data?.activityScore?.overall || "—"}/100`,
    },
    {
      label: "GitHub Score",
      value: `${data?.activityScore?.github || "—"}/100`,
    },
    {
      label: "Community Score",
      value: `${data?.activityScore?.community || "—"}/100`,
    },
  ];

  const smallCards = [
    {
      title: "Team Insights",
      icon: Users,
      items: [
        {
          label: "Team Size",
          value: data?.teamInsight?.teamSize?.toString() || "—",
        },
        {
          label: "Activity Score",
          value: data?.teamInsight?.activityScore
            ? `${data.teamInsight.activityScore}/100`
            : "—",
        },
        {
          label: "Locations",
          value: data?.teamInsight?.locations?.join(", ") || "—",
        },
      ],
    },
    {
      title: "Funding & Valuation",
      icon: DollarSign,
      items: [
        { label: "Stage", value: data?.crunchbase?.fundingStage || "—" },
        {
          label: "Total Funding",
          value: data?.crunchbase?.totalFunding || "—",
        },
        { label: "Valuation", value: data?.crunchbase?.valuation || "—" },
        {
          label: "Investors",
          value: data?.crunchbase?.investors?.length?.toString() || "—",
        },
      ],
    },
    {
      title: "Social Presence",
      icon: Twitter,
      items: [
        {
          label: "Followers",
          value: data?.twitterActivity?.followers?.toLocaleString() || "—",
        },
        {
          label: "Engagement",
          value: data?.twitterActivity?.engagement
            ? `${data.twitterActivity.engagement}%`
            : "—",
        },
        {
          label: "Tweets/Week",
          value: data?.twitterActivity?.tweetsPerWeek?.toString() || "—",
        },
        {
          label: "Verified",
          value: data?.twitterActivity?.verified ? "Yes" : "No",
        },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      {/* GitHub + Overall combined card */}
      <div className="data-card p-6 fade-up" style={{ animationDelay: "0.2s" }}>
        <div className="flex items-center gap-3 mb-5">
          <div className="p-2 rounded-lg bg-[#54FE6D]/10">
            <Github size={20} className="text-[#54FE6D]" />
          </div>
          <h4 className="text-lg font-semibold">GitHub & Overall Metrics</h4>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {githubAndOverall.map((item, idx) => (
            <div
              key={idx}
              className="flex justify-between items-center bg-[#1b1b1b]/50 rounded-md px-3 py-2 border border-white/5"
            >
              <span className="text-sm text-[#F7F6F7]/60">{item.label}</span>
              <span className="text-sm font-semibold text-white text-right">
                {item.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* The smaller metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {smallCards.map((card, idx) => (
          <div
            key={card.title}
            className="data-card p-6 fade-up"
            style={{ animationDelay: `${0.3 + idx * 0.1}s` }}
          >
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 rounded-lg bg-[#54FE6D]/10">
                <card.icon size={20} className="text-[#54FE6D]" />
              </div>
              <h4 className="text-lg font-semibold">{card.title}</h4>
            </div>

            <div className="space-y-3">
              {card.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  className="flex justify-between items-center"
                >
                  <span className="text-sm text-[#F7F6F7]/60">
                    {item.label}
                  </span>
                  <span className="text-sm font-semibold text-white text-right">
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
