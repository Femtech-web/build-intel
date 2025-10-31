import type { Metadata } from "next";
import "./globals.css";
import VisualEditsMessenger from "../visual-edits/VisualEditsMessenger";
import ErrorReporter from "@/components/ErrorReporter";
import Script from "next/script";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "BuildIntel — Discover What Builders Are Really Using",
  description:
    "AI-powered truth engine for discovering what Web3 projects are built with — their tech stack, traction, and team activity. Built for founders, researchers, and builders.",
  keywords: [
    "Web3 intelligence",
    "crypto projects",
    "blockchain analytics",
    "AI insights",
    "DeFi projects",
    "crypto stack analysis",
    "builder tools",
    "open source",
  ],
  authors: [{ name: "BuildIntel Team" }],
  creator: "BuildIntel",
  publisher: "BuildIntel",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://build-intel-seven.vercel.app/",
    siteName: "BuildIntel",
    title: "BuildIntel — Discover What Projects Are Really Using",
    description:
      "Instantly analyze any Web3 project. See its real stack, traction, and on-chain presence — powered by AI and open data.",
    images: [
      {
        url: "/open-graph.png",
        width: 1200,
        height: 630,
        alt: "BuildIntel Dashboard Preview",
        type: "image/png",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@DefiPreacherr",
    creator: "@DefiPreacherr",
    title: "BuildIntel — Discover What Projects Are Really Using",
    description:
      "AI-powered truth engine for discovering what Web3 projects are built with — their tech stack, traction, and team activity.",
    images: ["/open-graph.png"],
  },
  alternates: {
    canonical: "https://build-intel-seven.vercel.app/",
  },
  category: "analytics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ErrorReporter />
        <Script
          src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/scripts//route-messenger.js"
          strategy="afterInteractive"
          data-target-origin="*"
          data-message-type="ROUTE_CHANGE"
          data-include-search-params="true"
          data-only-in-iframe="true"
          data-debug="true"
          data-custom-data='{"appName": "YourApp", "version": "1.0.0", "greeting": "hi"}'
        />
        {children}
        <Toaster position="top-right" theme="dark" />
        <VisualEditsMessenger />
      </body>
    </html>
  );
}
