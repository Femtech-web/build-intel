import { ProjectAnalysis } from '@/types';

export const mockProjects: Record<string, ProjectAnalysis> = {
  zora: {
    projectName: "Zora",
    url: ["https://zora.co"],
    techStack: {
      frontend: ["React", "Next.js", "TypeScript", "Tailwind CSS"],
      backend: ["Node.js", "PostgreSQL", "Redis"],
      blockchain: ["Ethereum", "Optimism", "Zora Network", "ERC-721"],
      infrastructure: ["Vercel", "AWS", "IPFS", "The Graph"]
    },
    teamInsight: {
      teamSize: 28,
      activityScore: 94,
      locations: ["San Francisco", "New York", "Remote"]
    },
    githubStats: {
      stars: 1247,
      forks: 189,
      commits: 3421,
      contributors: 24,
      lastUpdated: "2 hours ago"
    },
    crunchbase: {
      fundingStage: "Series A",
      totalFunding: "$50M",
      investors: ["Paradigm", "Coinbase Ventures", "Kindred Ventures"],
      founded: "2020"
    },
    twitterActivity: {
      followers: 142000,
      engagement: 4.2,
      tweetsPerWeek: 12,
      verified: true
    },
    activityScore: {
      overall: 92,
      github: 88,
      twitter: 95,
      community: 93
    },
    aiInsight: "Zora demonstrates strong technical execution with a modern React/Next.js frontend and robust blockchain infrastructure. The team is highly active across GitHub and Twitter, indicating strong community engagement. Their use of Optimism and custom Zora Network shows deep blockchain expertise. Funding and growth metrics suggest product-market fit in the NFT creator economy space.",
    analyzedAt: new Date().toISOString()
  },
  base: {
    projectName: "Base",
    url: ["https://base.org"],
    techStack: {
      frontend: ["React", "Next.js", "TypeScript", "wagmi", "viem"],
      backend: ["Go", "Rust", "PostgreSQL"],
      blockchain: ["Ethereum L2", "OP Stack", "EVM Compatible"],
      infrastructure: ["Coinbase Cloud", "Kubernetes", "Grafana"]
    },
    teamInsight: {
      teamSize: 45,
      activityScore: 98,
      locations: ["San Francisco", "New York", "Austin"]
    },
    githubStats: {
      stars: 2891,
      forks: 432,
      commits: 8234,
      contributors: 38,
      lastUpdated: "1 hour ago"
    },
    crunchbase: {
      fundingStage: "Corporate",
      totalFunding: "N/A (Coinbase)",
      investors: ["Coinbase"],
      founded: "2023"
    },
    twitterActivity: {
      followers: 876000,
      engagement: 6.8,
      tweetsPerWeek: 18,
      verified: true
    },
    activityScore: {
      overall: 97,
      github: 96,
      twitter: 98,
      community: 97
    },
    aiInsight: "Base represents enterprise-grade blockchain infrastructure backed by Coinbase. Built on the OP Stack with Ethereum compatibility, they're leveraging battle-tested L2 technology. The team shows exceptional velocity with high commit frequency and large contributor base. Strong developer relations evident from high Twitter engagement and verified status. This is institutional-grade execution with startup agility.",
    analyzedAt: new Date().toISOString()
  },
  "friend.tech": {
    projectName: "Friend.Tech",
    url: ["https://friend.tech"],
    techStack: {
      frontend: ["React", "TypeScript", "Web3.js"],
      backend: ["Node.js", "Express", "MongoDB"],
      blockchain: ["Base", "ERC-1155", "Smart Contracts"],
      infrastructure: ["Vercel", "AWS Lambda", "CloudFlare"]
    },
    teamInsight: {
      teamSize: 8,
      activityScore: 86,
      locations: ["Remote", "Miami"]
    },
    githubStats: {
      stars: 892,
      forks: 234,
      commits: 1876,
      contributors: 6,
      lastUpdated: "3 hours ago"
    },
    crunchbase: {
      fundingStage: "Bootstrapped",
      totalFunding: "Self-funded",
      investors: [],
      founded: "2023"
    },
    twitterActivity: {
      followers: 289000,
      engagement: 8.4,
      tweetsPerWeek: 24,
      verified: false
    },
    activityScore: {
      overall: 88,
      github: 82,
      twitter: 94,
      community: 89
    },
    aiInsight: "Friend.Tech shows aggressive iteration velocity with a lean team. Built on Base for low gas fees, using ERC-1155 for social tokens. The Twitter engagement rate is exceptionally high (8.4%), suggesting viral growth mechanics. Small team size but high activity score indicates focused execution. Bootstrapped approach with strong organic traction - classic crypto product-market fit pattern.",
    analyzedAt: new Date().toISOString()
  }
};

export const getSampleProject = (name: string): ProjectAnalysis | null => {
  return mockProjects[name.toLowerCase()] || null;
};

export const getAllSampleProjects = (): ProjectAnalysis[] => {
  return Object.values(mockProjects);
};
