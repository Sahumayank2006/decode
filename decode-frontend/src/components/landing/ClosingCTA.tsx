"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, ShieldCheck } from "lucide-react";
import { useState } from "react";

const TEAM = [
  { num: "01", name: "MAYANK SAHU", role: "TEAM LEAD" },
  { num: "02", name: "JYOTIMA TOMAR" },
  { num: "03", name: "VAIBHAV" },
  { num: "04", name: "ANSHUL" },
  { num: "05", name: "MUVEEN SHAH" }
];

export function ClosingCTA() {
  const router = useRouter();
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="access" className="relative bg-[#020504] text-white min-h-[100svh] flex flex-col pt-32 overflow-hidden">
      
      {/* 02 - CALIBRATION RING BACKGROUND */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] lg:w-[1200px] lg:h-[1200px] pointer-events-none opacity-20 mix-blend-screen z-0">
         <motion.div animate={{ rotate: 360 }} transition={{ duration: 180, repeat: Infinity, ease: "linear" }} className="absolute inset-0 rounded-full border border-dashed border-white/20" />
         <motion.div animate={{ rotate: -360 }} transition={{ duration: 120, repeat: Infinity, ease: "linear" }} className="absolute inset-16 rounded-full border border-[var(--decode-green)]/15" />
         <div className="absolute inset-32 rounded-full border border-dashed border-white/5" />
         
         <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative flex flex-col items-center">
               <div className="w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full animate-pulse shadow-[0_0_15px_var(--decode-green)]" />
               <div className="absolute top-4 font-mono text-[7px] tracking-[0.5em] text-[var(--decode-green)]">VERIFIED</div>
            </div>
         </div>
      </div>

      <div className="relative mx-auto w-full max-w-[1400px] px-6 lg:px-12 flex flex-col flex-1 z-10">
        
        {/* 01 - CINEMATIC "PROTOCOL COMPLETE" AREA */}
        <div className="flex flex-col items-center justify-center text-center mt-12 lg:mt-24 mb-32">
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="font-mono text-[9px] lg:text-[11px] font-bold uppercase tracking-[0.3em] text-white/40 mb-8 flex items-center gap-4"
          >
            <div className="w-8 h-px bg-white/20" />
            PROTOCOL COMPLETE
            <div className="w-8 h-px bg-white/20" />
          </motion.div>
          
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="font-display text-[clamp(2.5rem,5vw,5rem)] font-medium leading-[1.05] tracking-tight text-white max-w-4xl drop-shadow-sm"
          >
            Ready to verify what matters.
          </motion.h2>
          
          <motion.p 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-6 font-mono text-[13px] lg:text-[15px] tracking-widest text-white/40 max-w-2xl leading-relaxed"
          >
            Turn locked scientific figures into structured, traceable, and responsibly verified records.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="mt-16"
          >
            <button
              onClick={() => router.push("/demo")}
              className="group relative inline-flex items-center justify-center overflow-hidden rounded-full p-[1px] transition-transform duration-700 hover:-translate-y-1 focus:outline-none shadow-[0_20px_50px_rgba(212,175,55,0.08)] hover:shadow-[0_20px_50px_rgba(212,175,55,0.15)]"
            >
              {/* Outer gold glow ring */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#FFE8A3]/50 via-[#D4AF37]/80 to-[#9A7842]/50 opacity-70 group-hover:opacity-100 transition-opacity duration-700" />
              
              {/* Inner button body */}
              <div className="relative flex items-center justify-center gap-4 rounded-full bg-gradient-to-b from-[#16140e] to-[#0a0906] border border-[#D4AF37]/40 px-10 py-5 shadow-[inset_0_1px_1px_rgba(255,232,163,0.15)] group-hover:bg-gradient-to-b group-hover:from-[#1f1a10] group-hover:to-[#0d0a06] transition-all duration-700">
                {/* Continuous shine sweep */}
                <div className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-[#FFE8A3]/10 to-transparent opacity-0 group-hover:animate-[gold-shine_2.5s_ease-in-out_infinite] group-hover:opacity-100 transition-opacity" />
                
                <Sparkles className="h-4 w-4 text-[#FFE8A3] transition-all duration-700 group-hover:rotate-12 group-hover:scale-110 drop-shadow-[0_0_8px_rgba(255,232,163,0.4)]" />
                <span className="font-mono text-[13px] font-bold uppercase tracking-[0.2em] text-[#FFE8A3] drop-shadow-[0_0_8px_rgba(255,232,163,0.3)]">Begin Verification</span>
                <ArrowRight className="h-4 w-4 text-[#FFE8A3] transition-transform duration-700 ease-out group-hover:translate-x-1.5" />
              </div>
            </button>
          </motion.div>
        </div>

        {/* 03 - TEAM REVEAL */}
        <div className="w-full max-w-4xl mx-auto mt-24 mb-32">
           <div className="flex flex-col items-center text-center mb-16">
             <div className="font-mono text-[9px] font-bold uppercase tracking-[0.3em] text-white/30 mb-5">THE PEOPLE BEHIND THE PROTOCOL</div>
             <h3 className="font-display text-2xl lg:text-3xl font-medium tracking-wide text-white/80">Built with precision. Built together.</h3>
           </div>

           {/* Team Roster */}
           <div className="flex flex-col border-t border-white/10" onMouseLeave={() => setHoveredIndex(null)}>
             {TEAM.map((member, idx) => {
               const isHovered = hoveredIndex === idx;
               const anyHovered = hoveredIndex !== null;
               const isLead = member.role === "TEAM LEAD";

               return (
                 <motion.div
                   key={idx}
                   onMouseEnter={() => setHoveredIndex(idx)}
                   initial={{ opacity: 0, x: -20 }}
                   whileInView={{ opacity: 1, x: 0 }}
                   viewport={{ once: true }}
                   transition={{ delay: idx * 0.1 }}
                   className={`group relative flex flex-col md:flex-row md:items-center justify-between py-6 lg:py-8 border-b border-white/5 transition-all duration-500 cursor-default ${anyHovered && !isHovered ? 'opacity-30' : 'opacity-100'}`}
                 >
                   {/* Trace line on hover */}
                   <div className={`hidden md:block absolute left-0 top-1/2 -translate-y-1/2 h-px bg-[var(--decode-green)]/50 transition-all duration-700 ease-out ${isHovered ? 'w-full opacity-100' : 'w-0 opacity-0'} z-0 pointer-events-none`} />

                   <div className="relative z-10 flex items-baseline gap-6 lg:gap-12 pl-2 bg-[#020504] md:pr-4">
                     <span className={`font-mono text-[10px] tracking-[0.2em] transition-colors duration-300 ${isHovered ? 'text-[var(--decode-green)]' : 'text-white/20'}`}>
                       {member.num}
                     </span>
                     <span className={`font-display text-2xl lg:text-4xl tracking-widest uppercase transition-colors duration-300 ${isHovered ? 'text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]' : 'text-white/60'}`}>
                       {member.name}
                     </span>
                   </div>

                   <div className="relative z-10 flex items-center gap-4 bg-[#020504] pl-2 mt-2 md:mt-0 md:pl-4 md:pr-2">
                     {member.role && (
                       <span className={`font-mono text-[9px] font-bold tracking-[0.25em] uppercase transition-all duration-300 ${isLead ? (isHovered ? 'text-[var(--decode-green)]' : 'text-[var(--decode-green)]/60') : (isHovered ? 'text-white/70' : 'text-white/20')}`}>
                         {member.role}
                       </span>
                     )}
                     <div className={`hidden md:block w-1.5 h-1.5 rounded-full transition-all duration-300 ${isHovered ? 'bg-[var(--decode-green)] shadow-[0_0_8px_var(--decode-green)] scale-100 opacity-100' : 'scale-50 opacity-0'}`} />
                   </div>
                 </motion.div>
               );
             })}
           </div>

           {/* 05 - MENTOR SIGNATURE */}
           <motion.div 
             initial={{ opacity: 0, y: 20 }}
             whileInView={{ opacity: 1, y: 0 }}
             viewport={{ once: true }}
             transition={{ delay: 0.6 }}
             className="mt-24 flex flex-col items-center lg:items-start text-center lg:text-left relative pl-0 lg:pl-8"
           >
             <div className="absolute left-0 top-0 bottom-0 w-px bg-white/10 hidden lg:block" />
             <div className="font-mono text-[9px] font-bold tracking-[0.3em] text-white/30 uppercase mb-4">MENTOR</div>
             <h4 className="font-display text-3xl lg:text-4xl tracking-[0.15em] text-white/80 uppercase">DR. RAJEEV GOYAL</h4>
             <div className="mt-3 font-mono text-[10px] tracking-widest text-white/40 uppercase">Associate Professor · Amity University Madhya Pradesh</div>
             
             {/* Signature Underline */}
             <div className="mt-8 w-full max-w-[350px] h-px bg-gradient-to-r from-white/20 to-transparent relative">
               <div className="absolute right-0 -bottom-5 font-mono text-[7px] tracking-[0.4em] text-white/20 uppercase">GUIDANCE · REVIEW · DIRECTION</div>
             </div>
           </motion.div>
        </div>

        {/* 07 & 08 - PROTOCOL SIGNATURE & FINAL STATEMENT */}
        <div className="flex flex-col items-center justify-center my-40">
           <div className="w-24 h-24 rounded-full border border-dashed border-white/20 flex flex-col items-center justify-center relative shadow-[inset_0_0_20px_rgba(255,255,255,0.02)]">
             <div className="absolute inset-2 border border-white/5 rounded-full" />
             <ShieldCheck className="w-5 h-5 text-[var(--decode-green)]/50 mb-1" />
             <div className="font-display text-[10px] tracking-[0.3em] text-white/50">DECODE</div>
             <div className="absolute -bottom-7 font-mono text-[6px] tracking-[0.2em] text-[var(--decode-green)]/40 text-center whitespace-nowrap">
               SCIENTIFIC DATA EXTRACTION PROTOCOL
             </div>
           </div>
           
           <div className="mt-14 font-mono text-[7px] lg:text-[8px] tracking-[0.3em] text-white/20 uppercase flex items-center gap-2 lg:gap-4">
             <span>SOURCE</span> &rarr; <span>EXTRACT</span> &rarr; <span>REBUILD</span> &rarr; <span>VERIFY</span> &rarr; <span>COMPLY</span>
           </div>

           <motion.h1 
             initial={{ opacity: 0, scale: 0.98 }}
             whileInView={{ opacity: 1, scale: 1 }}
             viewport={{ once: true }}
             transition={{ duration: 1 }}
             className="mt-32 font-display text-[clamp(2.5rem,5vw,5rem)] tracking-tight text-white/90 drop-shadow-md text-center max-w-5xl"
           >
             Nothing is guessed. Everything is checked.
           </motion.h1>
        </div>

        {/* 09 - REDESIGNED FOOTER */}
        <footer className="w-full mt-auto border-t border-white/10 pt-8 pb-12">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-8 font-mono text-[9px] text-white/40 tracking-widest uppercase">
            
            {/* Left */}
            <div className="flex flex-col lg:flex-row items-center gap-4">
              <span>© 2026 DECODE</span>
              <span className="hidden lg:block w-1 h-1 rounded-full bg-white/20" />
              <span>SCIENTIFIC DATA EXTRACTION PROTOCOL</span>
            </div>

            {/* Center */}
            <div className="text-white/60">
              Built by Mayank & Vaibhav
            </div>

            {/* Right */}
            <div className="flex flex-col lg:flex-row items-center gap-6 lg:gap-8">
              <div className="flex gap-6">
                <a href="#overview" className="hover:text-white transition-colors cursor-pointer">Overview</a>
                <a href="#protocol" className="hover:text-white transition-colors cursor-pointer">Pipeline</a>
                <a href="#comply" className="hover:text-white transition-colors cursor-pointer">Compliance</a>
              </div>
              
              <div className="flex items-center gap-2 px-2.5 py-1 bg-[#050b08] rounded border border-white/10 shadow-inner">
                <div className="w-1.5 h-1.5 rounded-full bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)] animate-pulse" />
                <span className="text-[var(--decode-green)]">SYSTEM READY</span>
              </div>
            </div>
          </div>
          
          {/* 10 - SIGNATURE FOOTER DETAIL */}
          <div className="mt-16 flex flex-col lg:flex-row justify-between items-center lg:items-end gap-4 border-t border-dashed border-white/5 pt-4">
            <div className="font-mono text-[7px] text-white/20 tracking-[0.4em]">INIT: 0x992B</div>
            <div className="flex items-center gap-3 lg:gap-6 font-mono text-[7px] text-white/20 tracking-[0.4em]">
              <span>PROTOCOL / 2026</span>
              <span>STATUS / READY</span>
              <span className="text-[var(--decode-green)]/40">TRACE / COMPLETE</span>
            </div>
          </div>
        </footer>
      </div>
      
    </section>
  );
}
