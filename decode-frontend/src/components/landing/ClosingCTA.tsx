"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";

export function ClosingCTA() {
  const router = useRouter();

  return (
    <section id="access" className="bg-[var(--color-ink)] text-[var(--color-paper)] min-h-[80svh] flex flex-col justify-center py-24 text-center">
      <div className="mx-auto w-full max-w-[1800px] px-6 sm:px-8 md:px-16 flex flex-col justify-between h-full">
        <div className="flex-1 flex flex-col items-center justify-center my-12 lg:my-24">
          <div className="flex items-center justify-center gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--color-brass-light)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--color-brass-light)]">
            READY WHEN YOU ARE
          </div>
          
          <h2 className="reveal mt-6 font-[family-name:var(--font-display)] text-[clamp(3rem,6vw,5.5rem)] font-medium leading-[1.05] text-[var(--color-paper)] max-w-[20ch]">
            Turn Research Figures Into<br />Certified Intelligence.
          </h2>
          
          <div className="reveal mt-12">
            <Button variant="seal" onClick={() => router.push("/dashboard")}>
              Begin Verification →
            </Button>
          </div>
        </div>

        <footer className="mt-16 flex flex-col lg:flex-row items-center justify-between gap-6 border-t border-[rgba(216,190,142,0.16)] pt-8 font-mono text-[12px] lg:text-[13px] text-[rgba(247,244,236,0.4)]">
          <span>© 2026 DECODE · Scientific Data Extraction Protocol</span>
          <span className="flex gap-8">
            <a href="#overview" className="text-[rgba(247,244,236,0.55)] no-underline hover:text-[var(--color-brass-light)] transition-colors">Overview</a>
            <a href="#protocol" className="text-[rgba(247,244,236,0.55)] no-underline hover:text-[var(--color-brass-light)] transition-colors">Pipeline</a>
            <a href="#comply" className="text-[rgba(247,244,236,0.55)] no-underline hover:text-[var(--color-brass-light)] transition-colors">Compliance</a>
          </span>
        </footer>
        
        <div className="mt-6 font-mono text-[11px] text-[rgba(247,244,236,0.32)]">
          Built by Mayank &amp; Vaibhav
        </div>
      </div>
    </section>
  );
}
