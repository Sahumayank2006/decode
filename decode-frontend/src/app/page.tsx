"use client";

import { useReveal } from "@/hooks/useReveal";
import { Navbar } from "@/components/ui/Navbar";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { ProtocolLedger } from "@/components/landing/ProtocolLedger";
import { PrecisionGrid } from "@/components/landing/PrecisionGrid";
import { ComplySection } from "@/components/landing/ComplySection";
import { ClosingCTA } from "@/components/landing/ClosingCTA";

export default function LandingPage() {
  // Initialize the scroll reveal animations
  useReveal();

  return (
    <div className="min-h-screen bg-[var(--color-paper)] text-[var(--color-graphite)] font-[family-name:var(--font-body)]">
      <Navbar variant="dark" />
      
      <main>
        <Hero />
        <HowItWorks />
        <ProtocolLedger />
        <PrecisionGrid />
        <ComplySection />
        <ClosingCTA />
      </main>
    </div>
  );
}
