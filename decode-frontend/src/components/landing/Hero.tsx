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
    </section>
  );
}
