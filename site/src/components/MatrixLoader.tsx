"use client";

export default function MatrixLoader() {
  return (
    <div className="flex flex-col items-center gap-6">
      <div className="relative">
        <div className="w-16 h-16 border-2 border-[#54FE6D]/20 border-t-[#54FE6D] rounded-full animate-spin" />
        <div className="absolute inset-0 w-16 h-16 border-2 border-[#54FE6D]/10 border-b-[#54FE6D]/50 rounded-full animate-spin" style={{ animationDuration: "1.5s", animationDirection: "reverse" }} />
      </div>
      
      <div className="text-center">
        <p className="text-lg font-semibold text-white mb-2 shimmer">Analyzing Project...</p>
        <p className="text-sm text-[#F7F6F7]/60">Scanning tech stack, team data, and traction metrics</p>
      </div>
    </div>
  );
}