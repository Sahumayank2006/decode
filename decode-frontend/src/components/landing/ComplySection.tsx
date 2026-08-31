"use client";

import { motion } from "framer-motion";
import { CheckCircle2, ArrowRight, ShieldCheck, Unlock, Activity, Search, ShieldAlert } from "lucide-react";

export function ComplySection() {
  return (
    <section id="comply" className="relative border-y border-white/5 min-h-[120svh] py-24 lg:py-32 bg-[#020503] text-white overflow-hidden">
      
      {/* Background Atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(57,217,120,0.03)_0%,transparent_70%)] pointer-events-none z-0" />
      <div className="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none z-0" />

      {/* Typography Header */}
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 mb-20 relative z-10 text-center lg:text-left">
         <div className="font-mono text-[9px] lg:text-[10px] tracking-[0.25em] font-bold uppercase flex flex-col lg:flex-row items-center justify-center lg:justify-start gap-5 text-white/50 mb-8">
            <span className="flex items-center gap-2.5">RESPONSIBLE <CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)] drop-shadow-[0_0_5px_rgba(57,217,120,0.5)]"/></span>
            <span className="hidden lg:block w-1.5 h-1.5 bg-white/10 rounded-full"/>
            <span className="flex items-center gap-2.5">VERIFIED <CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)] drop-shadow-[0_0_5px_rgba(57,217,120,0.5)]"/></span>
            <span className="hidden lg:block w-1.5 h-1.5 bg-white/10 rounded-full"/>
            <span className="flex items-center gap-2.5">TRUSTED <CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)] drop-shadow-[0_0_5px_rgba(57,217,120,0.5)]"/></span>
         </div>
         <h2 className="font-display text-[clamp(4.5rem,8vw,7rem)] font-medium leading-[0.95] tracking-tight text-white drop-shadow-sm">
            Comply.
         </h2>
         <div className="mt-8 font-mono text-[12px] lg:text-[14px] text-[var(--decode-green)] font-bold tracking-[0.15em] uppercase border-l-2 border-[var(--decode-green)]/40 pl-5 text-left mx-auto lg:mx-0 max-w-max">
            Correctness is not enough. Context matters.
         </div>
         <p className="mt-6 font-mono text-[13px] lg:text-[15px] text-white/40 max-w-3xl leading-relaxed mx-auto lg:mx-0">
            Every reconstruction is evaluated for responsible academic reuse before it ever leaves the protocol.
         </p>
      </div>

      {/* Hero Horizontal Pipeline */}
      <div className="relative max-w-[1400px] mx-auto px-6 lg:px-12 flex flex-col lg:flex-row gap-8 lg:gap-12 items-stretch lg:items-center z-10">
         
         {/* LEFT: RECONSTRUCTION */}
         <motion.div 
           initial={{ opacity: 0, x: -20 }}
           whileInView={{ opacity: 1, x: 0 }}
           viewport={{ once: true }}
           className="flex-1 min-w-[280px] border border-white/10 bg-[#070b09]/80 backdrop-blur-xl rounded-2xl p-7 relative flex flex-col justify-between shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
         >
           <div>
             <div className="font-mono text-[9px] font-bold tracking-[0.25em] text-white/40 mb-6 flex items-center gap-2.5">
               <span className="w-1.5 h-1.5 rounded-full bg-[#00f2fe] shadow-[0_0_8px_#00f2fe] animate-pulse"/> RECONSTRUCTED FIGURE
             </div>
             
             <div className="h-44 border border-white/5 bg-[#020403] rounded-lg flex items-end gap-3 p-4 relative overflow-hidden shadow-inner">
               <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:10px_10px]" />
               
               {/* Miniature editable chart */}
               <div className="w-full h-full border-l border-b border-[#00f2fe]/30 flex items-end justify-between px-3 pb-1 relative z-10">
                  {[45, 85, 55, 95, 70].map((h, i) => (
                     <motion.div 
                       key={i}
                       initial={{ height: 0 }}
                       whileInView={{ height: `${h}%` }}
                       viewport={{ once: true }}
                       transition={{ delay: 0.2 + (i * 0.1), duration: 1, ease: "easeOut" }}
                       className="w-[14%] bg-gradient-to-t from-[#00f2fe]/40 to-[#00f2fe]/10 border border-[#00f2fe]/40 rounded-t-[1px] relative shadow-[0_0_10px_rgba(0,242,254,0.1)]"
                     >
                        <div className="absolute -top-1 -left-1 w-2 h-2 bg-white rounded-full shadow-[0_0_5px_white] border border-[#00f2fe]" />
                     </motion.div>
                  ))}
               </div>
               <div className="absolute top-3 right-3 font-mono text-[7px] text-[#00f2fe]/60 border border-[#00f2fe]/20 bg-[#00f2fe]/5 px-1.5 py-0.5 rounded tracking-widest">STRUCTURED</div>
             </div>
           </div>
           
           <div className="mt-8 pt-5 border-t border-white/5 flex items-center justify-between">
             <div className="font-mono text-[10px] text-white/50 tracking-[0.2em]">FIG. 03 · PAGE 07</div>
             <div className="font-mono text-[8px] text-[#00f2fe] tracking-[0.2em] bg-[#00f2fe]/10 px-2 py-1 rounded border border-[#00f2fe]/20 shadow-sm">READY FOR REVIEW</div>
           </div>

           {/* Connection Line to Center */}
           <div className="hidden lg:block absolute top-1/2 -right-12 w-12 h-px bg-white/10 z-0">
             <motion.div animate={{ left: ["0%", "100%"] }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }} className="absolute top-0 w-4 h-px bg-[#00f2fe] shadow-[0_0_5px_#00f2fe]" />
           </div>
         </motion.div>

         {/* CENTER: COMPLIANCE GATE */}
         <motion.div 
           initial={{ opacity: 0, y: 20 }}
           whileInView={{ opacity: 1, y: 0 }}
           viewport={{ once: true }}
           transition={{ delay: 0.3 }}
           className="flex-[1.5] min-w-[340px] border border-white/10 bg-[#070b09]/80 backdrop-blur-xl rounded-2xl p-7 relative flex flex-col shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
         >
           <div className="font-mono text-[9px] font-bold tracking-[0.3em] text-white/40 mb-8 text-center uppercase">COMPLIANCE GATE</div>
           
           <div className="flex flex-col gap-5 flex-1">
             
             {/* 01 SIMILARITY */}
             <div className="flex items-center gap-5 group cursor-default">
                <div className="w-9 h-9 rounded-full border border-white/10 bg-[#020403] flex items-center justify-center font-mono text-[10px] text-white/30 group-hover:border-[var(--decode-green)]/40 group-hover:text-[var(--decode-green)] group-hover:shadow-[0_0_10px_rgba(57,217,120,0.2)] transition-all duration-300">01</div>
                <div className="flex-1 h-16 bg-[#020403] rounded-xl flex items-center justify-between px-5 border border-white/5 shadow-inner">
                   <div className="flex items-center gap-5">
                      <Search className="w-4 h-4 text-white/20" />
                      <div className="flex items-center gap-3">
                         <div className="w-6 h-6 border border-dashed border-white/20 rounded bg-white/5 relative flex items-center justify-center"><span className="text-[5px] font-mono text-white/30 absolute -top-3">SRC</span></div>
                         <ArrowRight className="w-3 h-3 text-white/10" />
                         <div className="w-6 h-6 border border-[var(--decode-green)]/40 rounded bg-[var(--decode-green)]/10 shadow-[0_0_10px_rgba(57,217,120,0.1)] relative flex items-center justify-center"><span className="text-[5px] font-mono text-[var(--decode-green)]/50 absolute -top-3">REC</span></div>
                      </div>
                   </div>
                   <div className="font-mono text-[9px] font-bold text-[var(--decode-green)] tracking-[0.15em] flex items-center gap-2">
                     <CheckCircle2 className="w-3.5 h-3.5" /> STRUCTURAL MATCH · 98%
                   </div>
                </div>
             </div>

             {/* 02 INTEGRITY */}
             <div className="flex items-center gap-5 group cursor-default">
                <div className="w-9 h-9 rounded-full border border-white/10 bg-[#020403] flex items-center justify-center font-mono text-[10px] text-white/30 group-hover:border-[var(--decode-green)]/40 group-hover:text-[var(--decode-green)] group-hover:shadow-[0_0_10px_rgba(57,217,120,0.2)] transition-all duration-300">02</div>
                <div className="flex-1 h-16 bg-[#020403] rounded-xl flex items-center justify-between px-5 border border-white/5 shadow-inner">
                   <div className="flex items-center gap-4">
                      <Activity className="w-4 h-4 text-white/20" />
                      <div className="font-mono text-[8px] text-white/40 flex items-center gap-2 tracking-[0.2em] uppercase">
                        <span>SRC</span><div className="w-3 h-px bg-white/20"/><span>EXT</span><div className="w-3 h-px bg-[var(--decode-green)]/40"/><span>RBD</span>
                      </div>
                   </div>
                   <div className="font-mono text-[9px] font-bold text-[var(--decode-green)] tracking-[0.15em] flex items-center gap-2">
                     <CheckCircle2 className="w-3.5 h-3.5" /> PROVENANCE VERIFIED
                   </div>
                </div>
             </div>

             {/* 03 RISK */}
             <div className="flex items-center gap-5 group cursor-default">
                <div className="w-9 h-9 rounded-full border border-white/10 bg-[#020403] flex items-center justify-center font-mono text-[10px] text-white/30 group-hover:border-[var(--decode-green)]/40 group-hover:text-[var(--decode-green)] group-hover:shadow-[0_0_10px_rgba(57,217,120,0.2)] transition-all duration-300">03</div>
                <div className="flex-1 h-16 bg-[#020403] rounded-xl flex items-center justify-between px-5 border border-white/5 shadow-inner">
                   <div className="flex items-center gap-4">
                      <ShieldAlert className="w-4 h-4 text-white/20" />
                      <div className="flex flex-col gap-1.5">
                         <div className="flex items-center gap-2 font-mono text-[7px] text-white/50 tracking-[0.2em]"><div className="w-1.5 h-1.5 rounded-full bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)]"/> LAYOUT RISK: LOW</div>
                         <div className="flex items-center gap-2 font-mono text-[7px] text-white/50 tracking-[0.2em]"><div className="w-1.5 h-1.5 rounded-full bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)]"/> CHROMATIC RISK: LOW</div>
                      </div>
                   </div>
                   <div className="font-mono text-[9px] font-bold text-[var(--decode-green)] tracking-[0.15em] flex items-center gap-2">
                     <CheckCircle2 className="w-3.5 h-3.5" /> RISK MINIMIZED
                   </div>
                </div>
             </div>

           </div>

           {/* RELEASE APERTURE */}
           <div className="mt-8 pt-7 border-t border-dashed border-white/10 flex flex-col items-center">
             <div className="font-mono text-[8px] text-white/30 tracking-[0.4em] mb-4 uppercase">Release Eligibility</div>
             <motion.div 
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 1, duration: 0.5 }}
                className="flex items-center justify-center gap-3 border border-[var(--decode-green)]/40 bg-[var(--decode-green)]/10 px-10 py-3 rounded-full shadow-[0_0_30px_rgba(57,217,120,0.15)]"
             >
                <Unlock className="w-4 h-4 text-[var(--decode-green)]" />
                <span className="font-mono text-[11px] font-bold tracking-[0.3em] text-[var(--decode-green)] uppercase">CLEARED</span>
             </motion.div>
           </div>

           {/* Connection Line to Right */}
           <div className="hidden lg:block absolute top-1/2 -right-12 w-12 h-px bg-white/10 z-0">
             <motion.div animate={{ left: ["0%", "100%"] }} transition={{ duration: 1.5, delay: 0.75, repeat: Infinity, ease: "linear" }} className="absolute top-0 w-4 h-px bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)]" />
           </div>
         </motion.div>

         {/* RIGHT: CONFIDENCE INSTRUMENT */}
         <motion.div 
           initial={{ opacity: 0, x: 20 }}
           whileInView={{ opacity: 1, x: 0 }}
           viewport={{ once: true }}
           transition={{ delay: 0.6 }}
           className="flex-1 min-w-[320px] border border-[var(--decode-green)]/30 bg-[#061109]/95 backdrop-blur-xl rounded-2xl p-8 relative flex flex-col items-center shadow-[0_20px_50px_rgba(57,217,120,0.1),inset_0_0_40px_rgba(57,217,120,0.03)]"
         >
           
           {/* The Trust Seal (Top Right inside panel) */}
           <div className="absolute top-5 right-5 w-14 h-14 opacity-70">
              <motion.svg animate={{ rotate: 360 }} transition={{ duration: 25, repeat: Infinity, ease: "linear" }} className="w-full h-full text-[var(--decode-green)]/40" viewBox="0 0 100 100">
                 <path id="curve" d="M 50,50 m -35,0 a 35,35 0 1,1 70,0 a 35,35 0 1,1 -70,0" fill="transparent" />
                 <text className="font-mono text-[10.5px] tracking-[0.2em] font-bold uppercase" fill="currentColor">
                    <textPath href="#curve">RESPONSIBLE REUSE · TRACE VERIFIED ·</textPath>
                 </text>
              </motion.svg>
              <div className="absolute inset-0 flex items-center justify-center font-display text-[9px] font-bold text-[var(--decode-green)]/70 tracking-widest uppercase">SEAL</div>
           </div>

           <div className="font-mono text-[10px] font-bold tracking-[0.25em] text-white/40 mb-8 w-full text-center mt-2 uppercase">COMPLIANCE CONFIDENCE</div>
           
           {/* Score Instrument */}
           <div className="relative w-44 h-44 flex items-center justify-center mb-8">
              <svg className="absolute inset-0 w-full h-full -rotate-90 drop-shadow-[0_0_15px_rgba(57,217,120,0.2)]">
                 <circle cx="88" cy="88" r="84" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                 <motion.circle 
                    initial={{ strokeDashoffset: 527 }}
                    whileInView={{ strokeDashoffset: 42.16 }} // 92% of 527 (527 * 0.08)
                    viewport={{ once: true }}
                    transition={{ duration: 2.5, delay: 1.2, ease: "easeOut" }}
                    cx="88" cy="88" r="84" fill="none" stroke="var(--decode-green)" strokeWidth="2.5" strokeDasharray="527" strokeLinecap="round" 
                 />
                 {/* Tiny tick marks */}
                 {[...Array(60)].map((_, i) => (
                    <line key={i} x1="88" y1="4" x2="88" y2="8" stroke="rgba(255,255,255,0.1)" strokeWidth="1" transform={`rotate(${i * 6} 88 88)`} />
                 ))}
              </svg>
              <div className="font-display text-[80px] font-medium tracking-tighter text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]">92</div>
           </div>

           <div className="flex items-center gap-2.5 text-[var(--decode-green)] font-mono text-[12px] tracking-[0.2em] font-bold bg-[var(--decode-green)]/10 px-5 py-2 rounded-full border border-[var(--decode-green)]/20 shadow-[0_0_15px_rgba(57,217,120,0.1)]">
              <ShieldCheck className="w-4 h-4" /> SAFE TO USE
           </div>
           <div className="mt-4 font-mono text-[9px] font-bold text-[var(--decode-green)]/60 tracking-[0.2em] uppercase">3 / 3 CHECKS PASSED</div>
           
           {/* Why Cleared Evidence Panel */}
           <div className="mt-10 w-full text-left bg-[#020403]/90 border border-white/5 p-5 rounded-xl shadow-inner">
              <div className="font-mono text-[9px] font-bold text-white/30 mb-4 tracking-[0.25em] uppercase">Why Cleared</div>
              <div className="flex flex-col gap-3.5 font-mono text-[10px] tracking-wider text-white/70">
                <div className="flex items-center gap-3"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)]"/> Structural similarity confirmed</div>
                <div className="flex items-center gap-3"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)]"/> Source integrity preserved</div>
                <div className="flex items-center gap-3"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--decode-green)]"/> Risk threshold satisfied</div>
              </div>
           </div>
           
           {/* Annotations */}
           <div className="mt-8 font-mono text-[8px] text-white/30 tracking-[0.2em] uppercase text-center border-t border-white/5 pt-4 w-full">Confidence is evidence-backed</div>
           <div className="mt-2 font-mono text-[7px] text-white/20 tracking-[0.2em] uppercase text-center">3 independent checks · 1 release decision</div>
         </motion.div>

      </div>

      {/* RELEASE AUDIT LEDGER */}
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 mt-24 relative z-10">
         <div className="border-y border-white/10 py-5 flex items-center overflow-x-auto hide-scrollbar bg-[#020503]/50">
            <div className="font-mono text-[9px] font-bold text-white/40 tracking-[0.3em] uppercase mr-10 shrink-0">RELEASE AUDIT</div>
            
            <div className="flex items-center gap-5 font-mono text-[8px] tracking-[0.2em] text-white/40 uppercase whitespace-nowrap">
               <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-white/20 rounded-full"/> FIG-03</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-white/20 rounded-full"/> SOURCE-LOCKED</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2 text-[#00f2fe]"><div className="w-1.5 h-1.5 bg-[#00f2fe] rounded-full shadow-[0_0_5px_#00f2fe]"/> RECONSTRUCTED</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2 text-[var(--decode-green)]"><div className="w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full shadow-[0_0_5px_var(--decode-green)]"/> SIMILARITY-98</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2 text-[var(--decode-green)]"><div className="w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full shadow-[0_0_5px_var(--decode-green)]"/> INTEGRITY-PASS</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2 text-[var(--decode-green)]"><div className="w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full shadow-[0_0_5px_var(--decode-green)]"/> RISK-LOW</span>
               <div className="w-6 h-px bg-white/10"/>
               <span className="flex items-center gap-2 text-[var(--decode-green)] font-bold bg-[var(--decode-green)]/10 px-2.5 py-1 rounded border border-[var(--decode-green)]/20"><div className="w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full animate-pulse shadow-[0_0_5px_var(--decode-green)]"/> RELEASE-CLEARED</span>
            </div>
         </div>
      </div>

      {/* FINAL BOTTOM STATEMENT */}
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 mt-32 mb-16 flex flex-col items-center relative z-10 text-center">
         <motion.div 
           initial={{ opacity: 0, y: 20 }}
           whileInView={{ opacity: 1, y: 0 }}
           viewport={{ once: true }}
           transition={{ duration: 1 }}
           className="font-display text-4xl lg:text-6xl tracking-widest text-white/20 font-medium"
         >
           RECONSTRUCTED &ne; RELEASED
         </motion.div>
         <motion.div 
           initial={{ opacity: 0 }}
           whileInView={{ opacity: 1 }}
           viewport={{ once: true }}
           transition={{ delay: 0.5, duration: 1 }}
           className="mt-8 font-mono text-[10px] lg:text-[12px] tracking-[0.4em] text-white/40 uppercase"
         >
           Only evidence-backed records pass the final gate.
         </motion.div>
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
         .hide-scrollbar::-webkit-scrollbar { display: none; }
         .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
       `}} />
    </section>
  );
}
