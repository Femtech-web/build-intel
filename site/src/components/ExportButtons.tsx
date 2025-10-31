"use client";

import { ProjectAnalysis } from "@/types";
import { Download, Share2, FileText } from "lucide-react";
import html2canvas from "html2canvas-pro";
import jsPDF from "jspdf";
import { toast } from "sonner";

interface ExportButtonsProps {
  data: ProjectAnalysis | null;
}

export default function ExportButtons({ data }: ExportButtonsProps) {
  const handleExportPNG = async () => {
    try {
      toast.loading("Generating PNG...");

      const resultsElement = document.getElementById(
        "results-container"
      ) as HTMLElement;
      if (!resultsElement) {
        toast.error("Could not find results to export");
        return;
      }

      const canvas = await html2canvas(resultsElement, {
        backgroundColor: "#111111",
        scale: 2,
        useCORS: true,
        allowTaint: true,
        logging: false,
        windowWidth: document.documentElement.scrollWidth,
      });

      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve)
      );

      if (!blob) throw new Error("Blob generation failed");

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${data?.projectName.replace(/\s+/g, "-")}-analysis.png`;
      link.click();
      URL.revokeObjectURL(url);

      toast.success("PNG exported successfully!");
    } catch (error) {
      console.error("PNG export error:", error);
      toast.error("Failed to export PNG");
    } finally {
      toast.dismiss();
    }
  };

  const handleExportPDF = async () => {
    try {
      toast.loading("Generating PDF...");

      // Find the results container
      const resultsElement = document.querySelector(
        ".max-w-6xl.mx-auto.space-y-6"
      ) as HTMLElement;

      if (!resultsElement) {
        toast.error("Could not find results to export");
        return;
      }

      // Generate canvas from the element
      const canvas = await html2canvas(resultsElement, {
        backgroundColor: "#111111",
        scale: 2,
        logging: false,
        useCORS: true,
      });

      const imgData = canvas.toDataURL("image/png");

      // Calculate PDF dimensions
      const pdf = new jsPDF({
        orientation: canvas.width > canvas.height ? "landscape" : "portrait",
        unit: "px",
        format: [canvas.width, canvas.height],
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
      pdf.save(`${data?.projectName.replace(/\s+/g, "-")}-analysis.pdf`);

      toast.success("PDF exported successfully!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF");
    } finally {
      toast.dismiss();
    }
  };

  const handleShare = async () => {
    try {
      const url = `${window.location.origin}/scanner?project=${encodeURIComponent(data?.projectName ?? "scanner")}`;

      if (navigator.share) {
        await navigator.share({
          title: `${data?.projectName} - BuildIntel Analysis`,
          text: `Check out the technology analysis for ${data?.projectName}`,
          url: url,
        });
        toast.success("Shared successfully!");
      } else {
        await navigator.clipboard.writeText(url);
        toast.success("Link copied to clipboard!");
      }
    } catch (error) {
      try {
        const url = `${window.location.origin}/scanner?project=${encodeURIComponent(data?.projectName ?? "scanner")}`;
        await navigator.clipboard.writeText(url);
        toast.success("Link copied to clipboard!");
      } catch (clipboardError) {
        console.error("Share error:", error);
        toast.error("Failed to share result");
      }
    } finally {
      toast.dismiss();
    }
  };

  return (
    <div
      className="flex flex-wrap items-center gap-3 fade-up"
      style={{ animationDelay: "0.7s" }}
    >
      <button
        onClick={handleExportPNG}
        className="btn-secondary px-5 py-2.5 font-medium flex items-center gap-2 text-sm"
      >
        <Download size={16} />
        Export PNG
      </button>
      <button
        onClick={handleExportPDF}
        className="btn-secondary px-5 py-2.5 font-medium flex items-center gap-2 text-sm"
      >
        <FileText size={16} />
        Export PDF
      </button>
      <button
        onClick={handleShare}
        className="btn-primary px-5 py-2.5 font-semibold flex items-center gap-2 text-sm"
      >
        <Share2 size={16} />
        Share Result
      </button>
    </div>
  );
}
