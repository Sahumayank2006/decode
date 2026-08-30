import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DECODE — Document Intelligence",
  description:
    "Transform complex documents into reliable, editable and presentation-ready visual intelligence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
