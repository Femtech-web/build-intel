import { NextRequest, NextResponse } from "next/server";
import { ProjectAnalysis } from "@/types";
import { getSampleProject } from "@/lib/mockData";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { projectName, url } = body;

    if (!projectName && !url) {
      return NextResponse.json(
        { error: "Project name or URL is required" },
        { status: 400 }
      );
    }

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // For now, return mock data
    const analysis = getSampleProject(projectName || url);

    if (!analysis) {
      return NextResponse.json(
        { error: "Project not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, data: analysis });
  } catch (error) {
    console.error("Analysis error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const projectName = searchParams.get("project");

  if (!projectName) {
    return NextResponse.json(
      { error: "Project name is required" },
      { status: 400 }
    );
  }

  const analysis = getSampleProject(projectName);

  if (!analysis) {
    return NextResponse.json(
      { error: "Project not found" },
      { status: 404 }
    );
  }

  return NextResponse.json({ success: true, data: analysis });
}
