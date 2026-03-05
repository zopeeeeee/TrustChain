import type { UploadStatusResponse } from "./api";

export async function generateReport(data: UploadStatusResponse): Promise<void> {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;

  let y = margin;

  // Header Background
  doc.setFillColor(24, 24, 27); // zinc-900
  doc.rect(0, 0, pageWidth, 40, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(22);
  doc.setFont("helvetica", "bold");
  doc.text("TRUSTCHAIN", margin, 20);
  doc.setFontSize(22);
  doc.setFont("helvetica", "normal");
  doc.text("- AV", margin + doc.getTextWidth("TRUSTCHAIN") + 2, 20);

  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(161, 161, 170); // zinc-400
  doc.text("Cryptographic Verification Report", margin, 28);

  // Reset text color for body
  doc.setTextColor(24, 24, 27); // zinc-900

  y = 55;

  // Title
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.text("Analysis Summary", margin, y);
  y += 10;

  // Verdict Section
  const isReal = data.verdict === "REAL";
  const verdictColor = isReal ? [22, 163, 74] : (data.verdict === "FAKE" ? [220, 38, 38] : [113, 113, 122]);

  // Verdict Box
  doc.setDrawColor(228, 228, 231); // zinc-200
  doc.setFillColor(250, 250, 250); // zinc-50
  doc.roundedRect(margin, y, pageWidth - 2 * margin, 35, 3, 3, 'FD');

  doc.setFontSize(10);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(113, 113, 122); // zinc-500
  doc.text("FINAL VERDICT", margin + 8, y + 10);

  doc.setFontSize(22);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(verdictColor[0], verdictColor[1], verdictColor[2]);
  doc.text(data.verdict || "UNKNOWN", margin + 8, y + 22);

  if (data.confidence !== null) {
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(113, 113, 122); // zinc-500
    const confTitle = "SYSTEM CONFIDENCE";
    doc.text(confTitle, pageWidth - margin - 8 - doc.getTextWidth(confTitle), y + 10);

    doc.setFontSize(24);
    doc.setTextColor(24, 24, 27); // zinc-900
    const confStr = `${Math.round(data.confidence * 100)}%`;
    doc.text(confStr, pageWidth - margin - 8 - doc.getTextWidth(confStr), y + 23);
  }

  y += 50;

  // Table Data helper
  const renderRow = (label: string, value: string, rowY: number, fullWidth: boolean = false) => {
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(113, 113, 122); // zinc-500
    doc.text(label, margin, rowY);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(24, 24, 27); // zinc-900
    if (fullWidth) {
      const splitValue = doc.splitTextToSize(value, pageWidth - 2 * margin - 50);
      doc.text(splitValue, margin + 45, rowY);
      return rowY + (splitValue.length * 5) + 3;
    } else {
      doc.text(value, margin + 45, rowY);
      return rowY + 9;
    }
  };

  // Diagnostics
  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(24, 24, 27); // zinc-900
  doc.text("Engine Diagnostics", margin, y);
  y += 6;

  doc.setDrawColor(228, 228, 231);
  doc.line(margin, y, pageWidth - margin, y);
  y += 8;

  y = renderRow("Visual Score", data.visual_score !== null ? `${Math.round(data.visual_score * 100)}%` : "N/A", y);
  y = renderRow("Audio Score", data.audio_score !== null && data.audio_score > 0 ? `${Math.round(data.audio_score * 100)}%` : "N/A", y);
  y = renderRow("Speech Detected", data.speech_detected ? `Yes (Weight: ${data.audio_weight})` : "No", y);

  y += 6;

  // Metadata
  doc.setFontSize(14);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(24, 24, 27); // zinc-900
  doc.text("Cryptographic Metadata", margin, y);
  y += 6;

  doc.setDrawColor(228, 228, 231);
  doc.line(margin, y, pageWidth - margin, y);
  y += 8;

  y = renderRow("Job ID", data.id, y);
  y = renderRow("Filename", data.filename, y, true);
  y = renderRow("Submitted", new Date(data.created_at).toLocaleString(), y);
  y = renderRow("Time Taken", data.processing_time ? `${data.processing_time.toFixed(2)}s` : "N/A", y);

  if (data.file_hash) {
    doc.setFontSize(10);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(113, 113, 122);
    doc.text("SHA-256 Hash", margin, y);

    doc.setFont("courier", "normal");
    doc.setTextColor(24, 24, 27);
    const splitHash = doc.splitTextToSize(data.file_hash, pageWidth - 2 * margin - 45);
    doc.text(splitHash, margin + 45, y);
    y += Math.max(9, splitHash.length * 5 + 3);
  }

  y += 6;
  doc.setFontSize(9);
  doc.setFont("helvetica", "italic");
  doc.setTextColor(161, 161, 170); // zinc-400
  doc.text(
    "* Prototype model. Blockchain registration available in a future update.",
    margin,
    y
  );

  // Footer
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setDrawColor(228, 228, 231);
    doc.line(margin, pageHeight - 20, pageWidth - margin, pageHeight - 20);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(161, 161, 170);

    const footerText = `TrustChain-AV | Generated: ${new Date().toLocaleString()}`;
    doc.text(footerText, margin, pageHeight - 12);

    const pageString = `Page ${i} of ${pageCount}`;
    doc.text(pageString, pageWidth - margin - doc.getTextWidth(pageString), pageHeight - 12);
  }

  doc.save(`trustchain-report-${data.id}.pdf`);
}
