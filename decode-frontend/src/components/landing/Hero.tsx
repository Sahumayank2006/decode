"use client";
/* eslint-disable */

import { useRouter } from "next/navigation";
import Image from "next/image";
import { ArrowRight, Sparkles } from "lucide-react";

export function Hero() {
  const router = useRouter();

  return (
    <section 
      className="relative w-full min-h-[100svh] bg-black flex flex-col items-center justify-end pb-72 lg:pb-[30vh] overflow-hidden"
      id="overview"
    >
      {/* Full width background image */}
      <div className="absolute inset-0 w-full h-full">
        <Image 
          src="/1.png" 
          alt="Hero Background" 
          fill
          priority
          className="object-cover object-center w-full h-full opacity-95"
        />
        {/* Subtle contrast gradient at the bottom for crystal-clear CTA visibility */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent pointer-events-none" />
      </div>
      
      {/* Professional Premium Golden Animated Shining CTA Button */}
      <div className="relative z-10 w-full flex flex-col items-center justify-center px-4">
        <a
          href="/demo"
          className="group relative inline-flex items-center justify-center rounded-2xl p-[2px] transition-all duration-500 hover:scale-[1.04] active:scale-[0.98] animate-gold-pulse no-underline cursor-pointer"
        >
          {/* Radiant gold halo ambient background */}
          <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-[#FFE8A3] via-[#D4AF37] to-[#B8860B] opacity-60 blur-md transition-all duration-500 group-hover:opacity-100 group-hover:blur-lg" />

          {/* Outer golden rim border */}
          <div className="relative flex items-center justify-center gap-3 overflow-hidden rounded-[14px] bg-gradient-to-b from-[#FFF2B2] via-[#E8C26E] via-[45%] to-[#B8860B] px-8 py-3.5 sm:px-10 sm:py-4 shadow-[inset_0_1px_2px_rgba(255,255,255,0.95),inset_0_-2px_4px_rgba(120,80,15,0.45),0_12px_32px_rgba(0,0,0,0.5)] border border-[#FFF8DC]/60">
            
            {/* Animated continuous sweeping gold shine light reflection */}
            <div className="pointer-events-none absolute inset-0 -translate-x-full animate-gold-shine bg-gradient-to-r from-transparent via-white/80 to-transparent opacity-85" />

            {/* Sparkle Icon */}
            <Sparkles className="relative z-10 h-5 w-5 text-[#0B1E33] transition-transform duration-300 group-hover:rotate-12 group-hover:scale-110" />

            {/* CTA Label */}
            <span className="relative z-10 font-mono text-sm sm:text-base font-bold uppercase tracking-[0.14em] text-[#0B1E33] drop-shadow-[0_1px_0_rgba(255,255,255,0.5)]">
              Try DECODE
            </span>

            {/* Interactive Arrow Icon */}
            <ArrowRight className="relative z-10 h-5 w-5 text-[#0B1E33] transition-transform duration-300 ease-out group-hover:translate-x-1.5" />
          </div>
        </a>
      </div>

      {/* Subtle Team Roster at bottom of Hero */}
      <div className="absolute bottom-10 lg:bottom-12 left-0 right-0 w-full px-6 flex justify-center z-20">
        <div className="flex flex-col items-center gap-5">
          <div className="font-mono text-[9px] font-bold uppercase tracking-[0.4em] text-white/50 mb-1 flex items-center gap-3">
             <div className="w-4 h-px bg-white/20"/> THE PROTOCOL TEAM <div className="w-4 h-px bg-white/20"/>
          </div>
          
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 font-mono text-[11px] lg:text-[12px] tracking-[0.25em] text-white/80 uppercase drop-shadow-md">
            <span className="text-white font-bold drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] flex items-center gap-2">MAYANK SAHU <span className="text-[var(--decode-green)] text-[9px] border border-[var(--decode-green)]/30 px-1.5 rounded bg-[var(--decode-green)]/10">LEAD</span></span>
            <span className="hidden sm:inline w-1 h-1 bg-[var(--decode-green)]/50 rounded-full" />
            <span>JYOTIMA TOMAR</span>
            <span className="hidden sm:inline w-1 h-1 bg-[var(--decode-green)]/50 rounded-full" />
            <span>VAIBHAV</span>
            <span className="hidden sm:inline w-1 h-1 bg-[var(--decode-green)]/50 rounded-full" />
            <span>ANSHUL</span>
            <span className="hidden sm:inline w-1 h-1 bg-[var(--decode-green)]/50 rounded-full" />
            <span>MUVEEN SHAH</span>
          </div>
          
          <div className="mt-2 flex items-center gap-3 font-mono text-[9px] lg:text-[10px] tracking-[0.3em] text-[var(--decode-green)]/90 font-bold uppercase bg-[var(--decode-green)]/5 px-4 py-1.5 rounded-full border border-[var(--decode-green)]/20 shadow-[0_0_15px_rgba(57,217,120,0.1)]">
             <span>MENTOR: DR. RAJEEV GOYAL</span>
          </div>
        </div>
      </div>
    </section>
  );
}
