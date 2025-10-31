import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { ProjectAnalysis } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function mapBackendToProjectAnalysis(raw: any): ProjectAnalysis {
  const content = raw?.data?.CACHED_RESULT?.content || raw?.data;
  if (!content) throw new Error("Invalid response format");

  const project = content.project;
  const github = content.aggregation.github;
  const funding = content.aggregation.funding?.funding_details;
  const serpSnippets = content.aggregation.funding?.raw_data?.serpapi?.results || [];
  const twitter = content.aggregation.twitter || [];
  const insight = content.insight;
  const discovery = content.discovery;

  // --- GitHub Insights ---
  const repos = github?.repos ?? [];
  const totalStars = github?.total_stars ?? 0;
  const totalCommits = github?.total_commits ?? 0;
  const repoCount = repos.length;

  // Dominant languages
  const langCount: Record<string, number> = {};
  for (const repo of repos) {
    for (const [lang, bytes] of Object.entries(repo.languages || {})) {
      langCount[lang] = (langCount[lang] || 0) + Number(bytes);
    }
  }
  const dominantLanguages = Object.entries(langCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([lang]) => lang);

  // Infer stack heuristically
  const techStack = {
    frontend: dominantLanguages.includes("JavaScript") || dominantLanguages.includes("TypeScript")
      ? ["React", "Next.js", "TypeScript"]
      : [],
    backend: dominantLanguages.includes("Go")
      ? ["Go", "Node.js"]
      : ["Node.js", "Python"],
    blockchain: dominantLanguages.includes("Solidity")
      ? ["Ethereum", "Solidity"]
      : [],
    infrastructure: Array.from(new Set(
      repos.flatMap((r: any) => r.infrastructure || [])
    )),
    dominantLanguages
  };

  // Get last commit date across all repos
  const lastCommitDate = repos
    .map((r: any) => new Date(r.activity?.last_commit?.date || 0).getTime())
    .filter(Boolean)
    .sort((a: any, b: any) => b - a)[0];
  const formattedLastCommit =
    lastCommitDate ? new Date(lastCommitDate).toLocaleString() : "Unknown";

  // --- Funding Insights ---
  const totalFunding = funding?.details?.total_funding ?? "N/A";
  const investors = funding?.details?.investors ?? [];
  const notableBackers = funding?.details?.notable_backers ?? [];
  const fundingStage = funding?.details?.last_round ?? "Unknown";
  const totalFundingUSD = funding?.details?.total_funding_usd ?? null;

  // Extract valuation from snippets
  const valuationMatch = serpSnippets.find((r: any) =>
    r.snippet?.match(/\$[0-9.,]+ ?(million|billion)/i)
  );
  const valuation = valuationMatch?.snippet?.match(/\$[0-9.,]+ ?(million|billion)/i)?.[0];

  // --- Twitter ---
  const twitterHandles = twitter.map((t: any) => t.username);
  const followers = twitter.reduce((sum: any, t: any) => sum + (t.followers || 0), 0);
  const avgFollowers = twitter.length ? Math.round(followers / twitter.length) : 0;

  // --- Activity Scores ---
  const githubScore = content.activity_metrics.github_score;
  const overallScore = content.activity_metrics.overall_score;
  const twitterScore = content.activity_metrics.twitter_score;
  const communityScore = content.activity_metrics.community_score;

  // Determine Twitter verification
  const verified =
    twitter.some((t: any) => t.verified) ||
    (followers > 50000 && twitter.some((t: any) => t.source === "twitter-api"));

  return {
    projectName: project,
    url: discovery?.websites?.slice(0, 3) || "N/A",

    techStack,

    teamInsight: {
      teamSize: repoCount,
      activityScore: githubScore,
      locations: ["Global"]
    },

    githubStats: {
      stars: totalStars,
      forks: repos.reduce((sum: any, r: any) => sum + (r.forks || 0), 0),
      commits: totalCommits,
      contributors: repos.reduce((sum: any, r: any) => sum + (r.activity?.contributors || 0), 0),
      lastUpdated: formattedLastCommit,
      repoCount,
      topLanguages: dominantLanguages,
      lastCommitDate: formattedLastCommit
    },

    crunchbase: {
      fundingStage,
      totalFunding,
      valuation,
      investors,
      notableBackers
    },

    twitterActivity: {
      followers,
      engagement: 3.8,
      tweetsPerWeek: 10,
      verified: verified,
      handles: twitterHandles
    },

    discovery: {
      websites: discovery?.websites || [],
      githubs:
        discovery?.githubs?.length
          ? discovery.githubs
          : github?.repos?.map((r: any) => r.url).filter(Boolean) || [],
      twitters:
        discovery?.twitters?.length
          ? discovery.twitters
          : twitter?.map((t: any) =>
            t.url || (t.username ? `https://twitter.com/${t.username}` : null)
          ).filter(Boolean) || [],
      fundings: discovery?.fundings || []
    },


    activityScore: {
      overall: overallScore,
      github: githubScore,
      twitter: twitterScore,
      community: communityScore
    },

    aiInsight: insight || "No insight available.",
    analyzedAt: new Date().toISOString()
  };
}
