"use client";

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import AnimatedBackground from "@/components/AnimatedBackground";
import { Brain, Zap, Target, GitBranch, Users, Shield } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />
      <Header />

      <main className="relative z-10 pt-24 pb-20">
        <div className="container mx-auto px-4">
          {/* Hero */}
          <div className="max-w-5xl mx-auto text-center mb-20">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              About <span className="text-cyan glow-cyan">Build</span>
              <span className="text-lime glow-lime">Intel</span>
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              The AI-powered truth engine that reveals what builders are really using.
              Built on Sentient ROMA for multi-agent intelligence.
            </p>
          </div>

          {/* Mission */}
          <div className="max-w-4xl mx-auto mb-20">
            <div className="brutal-card bg-gradient-to-br from-cyan/20 to-magenta/20 p-8 md:p-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="bg-cyan text-navy p-4 border-2 border-brutal-border">
                  <Target size={32} />
                </div>
                <h2 className="text-3xl font-bold">Our Mission</h2>
              </div>
              <p className="text-lg leading-relaxed mb-4">
                In the fast-moving world of Web3, it's hard to separate signal from noise. 
                BuildIntel cuts through the hype to reveal the real technology, team composition, 
                and traction behind crypto and web projects.
              </p>
              <p className="text-lg leading-relaxed">
                We believe transparency drives better decision-making. Whether you're an investor, 
                developer, or researcher, BuildIntel gives you the data-driven insights you need.
              </p>
            </div>
          </div>

          {/* How ROMA Works */}
          <div className="max-w-6xl mx-auto mb-20">
            <h2 className="text-4xl font-bold text-center mb-12">
              Powered by <span className="text-magenta glow-magenta">Sentient ROMA</span>
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="brutal-card bg-muted p-6">
                <div className="bg-cyan text-navy p-3 inline-block mb-4 border-2 border-brutal-border">
                  <Brain size={28} />
                </div>
                <h3 className="text-xl font-bold mb-3">Multi-Agent Intelligence</h3>
                <p className="text-text-secondary">
                  ROMA orchestrates specialized AI agents that analyze different aspects: 
                  code repositories, social signals, funding data, and community engagement.
                </p>
              </div>

              <div className="brutal-card bg-muted p-6">
                <div className="bg-magenta text-white p-3 inline-block mb-4 border-2 border-brutal-border">
                  <Zap size={28} />
                </div>
                <h3 className="text-xl font-bold mb-3">Real-Time Analysis</h3>
                <p className="text-text-secondary">
                  Our system continuously monitors GitHub commits, Twitter activity, 
                  and blockchain transactions to provide up-to-the-minute insights.
                </p>
              </div>

              <div className="brutal-card bg-muted p-6">
                <div className="bg-lime text-navy p-3 inline-block mb-4 border-2 border-brutal-border">
                  <GitBranch size={28} />
                </div>
                <h3 className="text-xl font-bold mb-3">Pattern Recognition</h3>
                <p className="text-text-secondary">
                  Machine learning models identify tech stack patterns, team dynamics, 
                  and growth trajectories based on thousands of analyzed projects.
                </p>
              </div>
            </div>
          </div>

          {/* ROMA Workflow Diagram */}
          <div className="max-w-5xl mx-auto mb-20">
            <div className="brutal-card bg-muted p-8">
              <h3 className="text-2xl font-bold mb-8 text-center">How ROMA Orchestrates Analysis</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
                <div className="brutal-card bg-navy p-4 text-center">
                  <div className="bg-cyan text-navy p-2 inline-block mb-2 border-2 border-brutal-border">
                    <Users size={24} />
                  </div>
                  <div className="font-bold text-sm">Input Query</div>
                  <div className="text-xs text-text-secondary mt-1">Project name or URL</div>
                </div>

                <div className="text-cyan text-center hidden md:block">→</div>

                <div className="brutal-card bg-navy p-4 text-center">
                  <div className="bg-magenta text-white p-2 inline-block mb-2 border-2 border-brutal-border">
                    <GitBranch size={24} />
                  </div>
                  <div className="font-bold text-sm">Agent Dispatch</div>
                  <div className="text-xs text-text-secondary mt-1">ROMA coordinates agents</div>
                </div>

                <div className="text-magenta text-center hidden md:block">→</div>

                <div className="brutal-card bg-navy p-4 text-center">
                  <div className="bg-lime text-navy p-2 inline-block mb-2 border-2 border-brutal-border">
                    <Brain size={24} />
                  </div>
                  <div className="font-bold text-sm">AI Synthesis</div>
                  <div className="text-xs text-text-secondary mt-1">Generate insights</div>
                </div>
              </div>

              <div className="mt-6 text-center text-text-secondary text-sm">
                Each agent specializes in: GitHub analysis, funding research, social monitoring, or tech stack detection
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="max-w-6xl mx-auto mb-20">
            <h2 className="text-4xl font-bold text-center mb-12">What We Analyze</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="brutal-card bg-muted p-6">
                <h3 className="text-xl font-bold mb-3 text-cyan">🔧 Tech Stack Fingerprinting</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• Frontend frameworks and libraries</li>
                  <li>• Backend languages and databases</li>
                  <li>• Blockchain networks and protocols</li>
                  <li>• Infrastructure and deployment tools</li>
                </ul>
              </div>

              <div className="brutal-card bg-muted p-6">
                <h3 className="text-xl font-bold mb-3 text-magenta">👥 Team Intelligence</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• Team size and growth rate</li>
                  <li>• Geographic distribution</li>
                  <li>• Contributor activity patterns</li>
                  <li>• Developer expertise levels</li>
                </ul>
              </div>

              <div className="brutal-card bg-muted p-6">
                <h3 className="text-xl font-bold mb-3 text-lime">📊 Traction Metrics</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• GitHub stars, forks, and commits</li>
                  <li>• Funding stages and investors</li>
                  <li>• Social media engagement</li>
                  <li>• Community size and activity</li>
                </ul>
              </div>

              <div className="brutal-card bg-muted p-6">
                <h3 className="text-xl font-bold mb-3 text-white">🧠 AI-Powered Insights</h3>
                <ul className="space-y-2 text-text-secondary">
                  <li>• Pattern matching against successful projects</li>
                  <li>• Risk and opportunity identification</li>
                  <li>• Technology maturity assessment</li>
                  <li>• Growth trajectory predictions</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Team */}
          <div className="max-w-4xl mx-auto mb-20">
            <div className="brutal-card bg-gradient-to-br from-lime/20 to-cyan/20 p-8 md:p-12">
              <div className="flex items-center gap-4 mb-6">
                <div className="bg-lime text-navy p-4 border-2 border-brutal-border">
                  <Shield size={32} />
                </div>
                <h2 className="text-3xl font-bold">Built with Transparency</h2>
              </div>
              <p className="text-lg leading-relaxed mb-4">
                BuildIntel is developed by a team passionate about bringing clarity to the Web3 
                ecosystem. We're builders analyzing builders, using the same open-source tools 
                and decentralized principles we believe in.
              </p>
              <p className="text-lg leading-relaxed">
                All our analysis methodologies are transparent, and we're committed to 
                continuously improving our AI models based on community feedback.
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="max-w-3xl mx-auto text-center">
            <div className="brutal-card bg-muted p-8">
              <h2 className="text-3xl font-bold mb-4">Ready to Uncover the Truth?</h2>
              <p className="text-lg text-text-secondary mb-6">
                Start analyzing Web3 projects with AI-powered intelligence
              </p>
              <a
                href="/scanner"
                className="brutal-button bg-cyan text-navy px-8 py-4 text-lg font-bold inline-block"
              >
                Try BuildIntel Scanner
              </a>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
