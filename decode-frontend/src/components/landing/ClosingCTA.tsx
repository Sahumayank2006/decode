"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, Sparkles } from "lucide-react";

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
            <button
              onClick={() => router.push("/demo")}
              className="group relative inline-flex items-center justify-center gap-3 overflow-hidden rounded-full p-[2px] transition-all duration-400 hover:scale-[1.04] active:scale-[0.98] animate-gold-pulse cursor-pointer shadow-[0_12px_40px_rgba(0,0,0,0.6)]"
            >
              {/* Outer gold glow wrapper */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#FFE8A3] via-[#D4AF37] to-[#9A7842] opacity-90 transition-opacity duration-300 group-hover:opacity-100" />
              
              {/* Inner button body */}
              <div className="relative flex items-center justify-center gap-3 rounded-full bg-gradient-to-b from-[#FFF2B2] via-[#E8C26E] via-[40%] to-[#B8860B] px-9 py-4 font-mono text-sm md:text-base font-bold uppercase tracking-[0.12em] text-[#0B1E33] shadow-[inset_0_1px_2px_rgba(255,255,255,0.95),inset_0_-2px_4px_rgba(110,70,10,0.4)]">
                {/* Continuous shine sweep */}
                <div className="pointer-events-none absolute inset-0 -translate-x-full animate-gold-shine bg-gradient-to-r from-transparent via-white/75 to-transparent opacity-85" />
                
                <Sparkles className="h-4 w-4 text-[#0B1E33] transition-transform duration-300 group-hover:rotate-12" />
                <span>Begin Verification</span>
                <ArrowRight className="h-4 w-4 text-[#0B1E33] transition-transform duration-300 ease-out group-hover:translate-x-1" />
              </div>
            </button>
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
