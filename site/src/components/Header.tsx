"use client";

import Link from "next/link";

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#111111]/80 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="text-xl font-semibold tracking-tight">
              <span className="text-white">Build</span>
              <span className="accent-glow">Intel</span>
            </div>
          </Link>
        </div>
      </div>
    </header>
  );
}
