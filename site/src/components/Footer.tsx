import Link from "next/link";
import { Twitter, Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#111111] py-12 mt-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="text-center md:text-left">
            <p className="text-[#F7F6F7] font-medium">
              Powered by <span className="accent-glow">Sentient ROMA</span> + BuildIntel
            </p>
            <p className="text-sm text-[#F7F6F7]/60 mt-2">
              AI-powered intelligence for crypto and web projects
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="https://twitter.com/buildintel"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary px-4 py-2 flex items-center gap-2 hover:border-[#54FE6D]/30"
            >
              <Twitter size={18} />
              <span className="text-sm">Twitter</span>
            </Link>
            <Link
              href="https://github.com/buildintel"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary px-4 py-2 flex items-center gap-2 hover:border-[#54FE6D]/30"
            >
              <Github size={18} />
              <span className="text-sm">GitHub</span>
            </Link>
          </div>
        </div>

        <div className="text-center text-[#F7F6F7]/50 text-sm mt-8 pt-8 border-t border-white/5">
          © {new Date().getFullYear()} BuildIntel. All rights reserved.
        </div>
      </div>
    </footer>
  );
}