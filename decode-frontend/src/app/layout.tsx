import type { Metadata } from "next";
import { Newsreader, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const newsreader = Newsreader({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-display",
});

const ibmPlexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
});

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
      <body className={`antialiased min-h-screen ${newsreader.variable} ${ibmPlexSans.variable} ${ibmPlexMono.variable}`}>
        {children}
      </body>
    </html>
  );
}
