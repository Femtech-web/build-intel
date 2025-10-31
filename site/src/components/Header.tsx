"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const pathname = usePathname();

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

          <nav className="flex items-center gap-8">
            <Link
              href="/"
              className={`text-sm font-medium transition-colors ${
                pathname === "/" ? "text-[#54FE6D]" : "text-[#F7F6F7] hover:text-white"
              }`}
            >
              Home
            </Link>
            <Link
              href="/scanner"
              className={`text-sm font-medium transition-colors ${
                pathname === "/scanner" ? "text-[#54FE6D]" : "text-[#F7F6F7] hover:text-white"
              }`}
            >
              Scanner
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}