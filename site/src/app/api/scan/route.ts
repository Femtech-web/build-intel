import { NextRequest, NextResponse } from "next/server";
import { getAllSampleProjects } from "@/lib/mockData";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { file, url } = body;

    // This endpoint would handle file uploads (JSON/CSV) or URL scanning
    // For now, it's a placeholder for backend integration

    return NextResponse.json({
      success: true,
      message: "File/URL scan initiated",
      jobId: `scan-${Date.now()}`,
    });
  } catch (error) {
    console.error("Scan error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  // Return all available sample projects
  const projects = getAllSampleProjects();
  
  return NextResponse.json({
    success: true,
    data: projects.map((p) => ({
      name: p.projectName,
      url: p.url,
    })),
  });
}
