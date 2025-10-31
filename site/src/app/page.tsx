"use client";

import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { ArrowRight, Zap, Database, Users } from "lucide-react";

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#111111]">
      <Header />
      
      <main className="pt-24">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 py-32 md:py-40">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#54FE6D]/10 border border-[#54FE6D]/20 mb-8">
              <span className="accent-glow text-sm font-medium tracking-wide">
                AI-POWERED INTELLIGENCE
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-semibold mb-6 leading-tight tracking-tight">
              Discover What Builders
              <br />
              <span className="accent-glow">Are Really Using.</span>
            </h1>

            <p className="text-xl md:text-2xl text-[#F7F6F7]/80 mb-12 max-w-2xl mx-auto font-light">
              AI-powered tool that reveals technology stacks, teams, and traction
              of crypto and web projects.
            </p>

            <button
              onClick={() => router.push("/scanner")}
              className="btn-primary px-8 py-4 text-lg font-semibold inline-flex items-center gap-3"
            >
              Scan a Project
              <ArrowRight size={20} />
            </button>

            <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="data-card p-8 text-left">
                <div className="bg-[#54FE6D]/10 text-[#54FE6D] p-3 inline-flex rounded-lg mb-4">
                  <Zap size={24} />
                </div>
                <h3 className="text-lg font-semibold mb-2">Tech Stack Analysis</h3>
                <p className="text-[#F7F6F7]/70 text-sm leading-relaxed">
                  Reveal frontend, backend, blockchain, and infrastructure choices
                </p>
              </div>

              <div className="data-card p-8 text-left">
                <div className="bg-[#54FE6D]/10 text-[#54FE6D] p-3 inline-flex rounded-lg mb-4">
                  <Users size={24} />
                </div>
                <h3 className="text-lg font-semibold mb-2">Team Insights</h3>
                <p className="text-[#F7F6F7]/70 text-sm leading-relaxed">
                  Discover team size, activity, and contributor metrics
                </p>
              </div>

              <div className="data-card p-8 text-left">
                <div className="bg-[#54FE6D]/10 text-[#54FE6D] p-3 inline-flex rounded-lg mb-4">
                  <Database size={24} />
                </div>
                <h3 className="text-lg font-semibold mb-2">Traction Data</h3>
                <p className="text-[#F7F6F7]/70 text-sm leading-relaxed">
                  GitHub stats, funding info, and social engagement
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="max-w-7xl mx-auto px-6 pb-32">
          <div className="data-card p-12 md:p-16 text-center max-w-3xl mx-auto bg-gradient-to-br from-[#232323] to-[#1a1a1a]">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              Ready to see behind the scenes?
            </h2>
            <p className="text-lg text-[#F7F6F7]/70 mb-8">
              Get instant insights powered by Sentient ROMA
            </p>
            <button
              onClick={() => router.push("/scanner")}
              className="btn-primary px-8 py-3 text-base font-semibold"
            >
              Start Scanning Now
            </button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}