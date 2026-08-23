import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DECODE — AI-Powered Chart Intelligence",
  description:
    "Detection, Extraction, Compliance-verification, Output-generation, Diagram-reconstruction, and Evaluation. Transform research paper charts into editable, copyright-safe visualizations.",
  keywords: ["chart extraction", "PDF analysis", "copyright compliance", "data visualization", "OCR"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
