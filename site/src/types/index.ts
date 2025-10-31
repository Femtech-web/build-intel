export interface ProjectAnalysis {
  projectName: string;
  url: string[];

  // 💻 Stack inference
  techStack: {
    frontend: string[];
    backend: string[];
    blockchain: string[];
    infrastructure: any[];
    dominantLanguages?: string[];
  };

  // 🧠 Team / dev insights
  teamInsight: {
    teamSize: number;
    activityScore: number;
    locations: string[];
  };

  // 📊 GitHub stats
  githubStats: {
    stars: number;
    forks: number;
    commits: number;
    contributors: number;
    lastUpdated: string;
    repoCount?: number;
    topLanguages?: string[];
    lastCommitDate?: string;
  };

  // 💸 Funding
  crunchbase: {
    fundingStage: string;
    totalFunding: string;
    valuation?: string;
    investors: string[];
    notableBackers?: string[];
    founded?: string;
  };

  // 🐦 Twitter presence
  twitterActivity: {
    followers: number;
    engagement: number;
    tweetsPerWeek: number;
    verified: boolean;
    handles?: string[];
  };

  // 🧭 Discovery sources
  discovery?: {
    websites: string[] | any;
    githubs: string[] | any;
    twitters: string[] | any;
    fundings: string[] | any;
  };

  // 📈 Activity / health
  activityScore: {
    overall: number;
    github: number;
    twitter: number;
    community: number;
  };

  aiInsight: string;
  analyzedAt: string;
}
