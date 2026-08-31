"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { 
  FileBox, BrainCircuit, 
  SplitSquareHorizontal, BadgeCheck, CheckCircle2,
  Scan, Code2, ShieldCheck, Fingerprint, Crosshair
} from "lucide-react";

const STAGES = [
  {
    num: "01",
    id: "RECEIVE",
    status: "SOURCE LOCKED",
    desc: "Document received, paginated, and rendered for analysis.",
    icon: FileBox,
    details: ["PDF INGESTED", "SHA-256: 8f4e...9b1a", "24 PAGES"],
    visual: (
       <div className="relative w-full h-32 bg-[#07110d]/80 rounded border border-white/5 overflow-hidden flex items-center justify-center shadow-inner">
         <motion.div animate={{ top: ["-10%", "110%"] }} transition={{ repeat: Infinity, duration: 2.5, ease: "linear" }} className="absolute left-0 right-0 h-[1px] bg-[var(--decode-green)]/40 shadow-[0_0_15px_var(--decode-green)]" />
         <FileBox className="w-8 h-8 text-white/20 drop-shadow-md" />
         <div className="absolute top-3 right-3 flex gap-1.5"><div className="w-5 h-7 bg-white/5 border border-white/10 rounded-sm" /><div className="w-5 h-7 bg-white/10 border border-white/20 rounded-sm shadow-sm" /></div>
         <div className="absolute bottom-2 left-2 font-mono text-[8px] text-white/30">ID: 0x9812A</div>
       </div>
    )
  },
  {
    num: "02",
    id: "LOCATE",
    status: "REGION FOUND",
    desc: "Every chart, table, and diagram located as its own region.",
    icon: Scan,
    details: ["FIG 01", "TABLE 02", "COORD: 452,189"],
    visual: (
       <div className="relative w-full h-32 bg-[#07110d]/80 rounded border border-white/5 p-4 flex items-center justify-center shadow-inner">
         <div className="relative w-full h-full border border-dashed border-white/20 rounded flex items-center justify-center">
           <div className="absolute inset-2 border border-dashed border-[var(--decode-green)]/20 rounded" />
           <motion.div initial={{ opacity: 0.3, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ repeat: Infinity, duration: 1.5, repeatType: "reverse", ease: "easeInOut" }} className="absolute inset-4 border border-[var(--decode-green)]/50 bg-[var(--decode-green)]/5 shadow-[0_0_20px_rgba(57,217,120,0.1)]">
             <Crosshair className="absolute -top-2.5 -left-2.5 w-5 h-5 text-[var(--decode-green)] drop-shadow-[0_0_5px_var(--decode-green)]" />
             <div className="absolute bottom-1 right-1 font-mono text-[8px] text-[var(--decode-green)]/60">FIG_01</div>
           </motion.div>
         </div>
       </div>
    )
  },
  {
    num: "03",
    id: "EXTRACT",
    status: "DATA RECOVERED",
    desc: "Values, axes, legends, and labels recovered with confidence scoring.",
    icon: BrainCircuit,
    details: ["AXIS DETECTED", "12 VALUES", "CONF: 94%"],
    visual: (
       <div className="relative w-full h-32 bg-[#07110d]/80 rounded border border-white/5 p-4 flex items-end gap-2.5 shadow-inner">
         {/* Animated extraction grid */}
         <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:10px_10px] pointer-events-none" />
         {[35, 75, 45, 95].map((h, i) => (
           <div key={i} className="flex-1 bg-white/10 relative rounded-t-sm overflow-hidden" style={{ height: `${h}%` }}>
             <motion.div initial={{ height: 0 }} animate={{ height: "100%" }} transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.15, ease: "circOut" }} className="absolute bottom-0 w-full bg-gradient-to-t from-[var(--decode-green)]/40 to-[var(--decode-green)]/10 border-t border-[var(--decode-green)]" />
           </div>
         ))}
       </div>
    )
  },
  {
    num: "04",
    id: "REBUILD",
    status: "STRUCTURE BUILT",
    desc: "Rebuilt as an editable, restylable, interactive chart.",
    icon: Code2,
    details: ["VECTOR", "DATA", "STYLE"],
    visual: (
       <div className="relative w-full h-32 bg-[#07110d]/80 rounded border border-white/5 p-4 shadow-inner">
         <div className="w-full h-full flex flex-col justify-between relative z-10">
           <div className="flex justify-between items-center px-2 py-1 bg-white/5 border border-white/10 rounded shadow-sm font-mono text-[8px] text-white/50"><span>Nodes: 24</span><span className="text-[var(--decode-green)]">Handles: Active</span></div>
           <svg viewBox="0 0 100 40" className="w-full h-12 overflow-visible drop-shadow-[0_0_8px_rgba(57,217,120,0.4)]">
             <motion.path d="M0,35 L25,15 L50,25 L75,10 L100,20" fill="none" stroke="var(--decode-green)" strokeWidth="1.5" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }} />
             <circle cx="25" cy="15" r="2.5" fill="var(--decode-bg)" stroke="var(--decode-green)" strokeWidth="1" />
             <circle cx="50" cy="25" r="2.5" fill="var(--decode-bg)" stroke="var(--decode-green)" strokeWidth="1" />
             <circle cx="75" cy="10" r="2.5" fill="var(--decode-bg)" stroke="var(--decode-green)" strokeWidth="1" />
           </svg>
         </div>
       </div>
    )
  },
  {
    num: "05",
    id: "VALIDATE",
    status: "RISK CHECKED",
    desc: "Similarity, color, and layout risk assessed against the source.",
    icon: SplitSquareHorizontal,
    details: ["SSIM: 0.99", "COLOR MATCH", "LAYOUT ALIGNED"],
    visual: (
       <div className="relative w-full h-32 bg-[#07110d]/80 rounded border border-white/5 flex overflow-hidden shadow-inner">
         <div className="flex-1 border-r border-dashed border-white/20 p-2 flex items-center justify-center relative">
           <div className="w-10 h-10 bg-white/10 rounded shadow-inner" />
           <div className="absolute top-1 left-1 font-mono text-[7px] text-white/30">SOURCE</div>
         </div>
         <div className="flex-1 p-2 flex items-center justify-center relative bg-[var(--decode-green)]/5">
           <div className="w-10 h-10 bg-[var(--decode-green)]/20 border border-[var(--decode-green)]/40 rounded shadow-[0_0_15px_rgba(57,217,120,0.1)]" />
           <motion.div animate={{ scale: [0.8, 1.1, 1], opacity: [0, 1, 0] }} transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }} className="absolute inset-0 flex items-center justify-center"><CheckCircle2 className="w-5 h-5 text-[var(--decode-green)]" /></motion.div>
           <div className="absolute top-1 right-1 font-mono text-[7px] text-[var(--decode-green)]/60">RECORD</div>
         </div>
       </div>
    )
  },
  {
    num: "06",
    id: "CERTIFY",
    status: "RECORD CERTIFIED",
    desc: "Certified record released as SVG, PNG, or structured data.",
    icon: BadgeCheck,
    details: ["JSON/SVG", "PROVENANCE", "SEALED"],
    visual: (
       <div className="relative w-full h-32 bg-[url('/noise.png')] bg-[#0b1712] rounded border border-[var(--decode-green)]/30 shadow-[0_0_30px_rgba(57,217,120,0.15)] flex flex-col items-center justify-center gap-3">
         <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#07110d]/80 pointer-events-none" />
         <ShieldCheck className="w-12 h-12 text-[var(--decode-green)] drop-shadow-[0_0_10px_var(--decode-green)] relative z-10" strokeWidth={1.5} />
         <div className="font-mono text-[10px] text-[var(--decode-green)] font-bold tracking-[0.2em] bg-[var(--decode-green)]/10 px-2.5 py-1 rounded border border-[var(--decode-green)]/20 relative z-10 shadow-[0_0_10px_rgba(57,217,120,0.1)]">VERIFIED</div>
       </div>
    )
  }
];

export function ProtocolLedger() {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Use scroll progress to draw the horizontal rail
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });
  
  // Map scroll progress to horizontal width of the active line
  const railProgress = useTransform(scrollYProgress, [0.2, 0.8], ["0%", "100%"]);

  return (
    <section ref={containerRef} id="protocol" className="relative min-h-[100svh] py-24 lg:py-32 bg-[#050b08] text-white overflow-hidden">
       {/* Background Atmosphere */}
       <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(57,217,120,0.04)_0%,transparent_70%)] pointer-events-none" />
       
       {/* Trace Layer / Hidden Depth */}
       <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
       <div className="absolute top-24 left-6 lg:left-12 font-mono text-[8px] text-white/20 rotate-90 origin-left tracking-[0.3em]">SYS_TRACE_ACTIVE_0x9A4</div>
       <div className="hidden lg:block absolute bottom-24 right-12 font-mono text-[8px] text-[var(--decode-green)]/20 -rotate-90 origin-right tracking-[0.3em]">AUDIT_TRAIL_SECURE</div>

       <div className="relative w-full max-w-[1800px] mx-auto px-6 sm:px-12 z-10">
          
          {/* Header */}
          <div className="reveal mb-24 max-w-4xl">
            <div className="flex items-center gap-3 font-mono text-[10px] font-bold uppercase tracking-[0.2em] text-[var(--decode-green)] before:inline-block before:h-px before:w-6 before:bg-[var(--decode-green)] shadow-sm">
              THE RECORDED PIPELINE
            </div>
            <h2 className="mt-6 font-display text-[clamp(2rem,4vw,3.5rem)] font-medium leading-[1.1] tracking-tight text-white drop-shadow-sm">
              Every document passes through the same recorded sequence — nothing is skipped, nothing is unaccounted for.
            </h2>
            <p className="mt-8 font-mono text-[11px] lg:text-[13px] text-white/40 tracking-widest border-l-2 border-[var(--decode-green)]/30 pl-4">
              A DETERMINISTIC CHAIN FROM SOURCE DOCUMENT TO VERIFIED, TRACEABLE OUTPUT.
            </p>
          </div>

          {/* Verification Rail Container */}
          <div className="reveal relative w-full">
            
            {/* The Horizontal Spine / Rail */}
            <div className="absolute left-8 lg:-left-[50vw] top-0 bottom-0 lg:top-1/2 lg:bottom-auto w-px lg:w-[200vw] lg:h-px bg-gradient-to-b lg:bg-gradient-to-r from-transparent via-white/10 to-[var(--decode-green)]/20 z-0" />
            
            {/* Animated Data Signal on Rail */}
            <div className="absolute left-8 lg:-left-[50vw] top-0 lg:top-1/2 lg:-translate-y-1/2 w-px lg:w-[200vw] h-full lg:h-px z-0 overflow-hidden">
               <motion.div 
                 className="absolute top-0 left-0 lg:top-auto lg:h-px lg:w-[30vw] h-[30vh] w-px bg-gradient-to-b lg:bg-gradient-to-r from-transparent via-[var(--decode-green)] to-transparent opacity-80"
                 style={{ [typeof window !== 'undefined' && window.innerWidth >= 1024 ? 'left' : 'top']: railProgress }}
               />
            </div>

            {/* Micro-label on spine */}
            <div className="hidden lg:block absolute left-1/2 -top-8 font-mono text-[9px] text-[var(--decode-green)]/50 tracking-[0.2em] -translate-x-1/2 bg-[#050b08] px-3 z-10 border border-white/5 rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)]">
              AUDIT TRAIL · COMPLETE
            </div>

            {/* Stages Grid (Vertical Mobile, Horizontal Scrolling Desktop) */}
            <div className="relative z-10 pl-16 lg:pl-0 flex flex-col lg:flex-row gap-12 lg:gap-6 lg:overflow-x-auto lg:snap-x lg:snap-mandatory pb-16 pt-8 lg:px-4 hide-scrollbar">
               {STAGES.map((stage, idx) => (
                 <motion.div 
                   key={idx}
                   whileHover={{ y: -6 }}
                   className="relative flex-shrink-0 w-full lg:w-[340px] lg:snap-center group"
                 >
                    {/* Node Connector */}
                    <div className="absolute -left-[32px] lg:left-1/2 top-8 lg:-top-[34px] w-[32px] h-px lg:w-px lg:h-[34px] bg-white/10 group-hover:bg-[var(--decode-green)]/40 transition-colors duration-500" />
                    
                    {/* Checkpoint Node */}
                    <div className="absolute -left-[37px] lg:left-1/2 top-[27px] lg:-top-[40px] w-[10px] h-[10px] rounded-full border-2 border-[#050b08] bg-white/20 lg:-translate-x-1/2 z-10 group-hover:bg-[var(--decode-green)] group-hover:shadow-[0_0_12px_var(--decode-green)] group-hover:border-[var(--decode-green)]/20 transition-all duration-300" />

                    {/* Stage Card / Glass Panel */}
                    <div className="h-full relative flex flex-col gap-4 rounded-xl border border-white/5 bg-[#0b1712]/40 backdrop-blur-xl p-7 shadow-2xl transition-all duration-500 hover:bg-[#0e1d17]/80 hover:border-[var(--decode-green)]/30 hover:shadow-[0_20px_40px_rgba(0,0,0,0.6),inset_0_0_20px_rgba(57,217,120,0.03)] overflow-hidden">
                       
                       {/* Asymmetric Glass Shine */}
                       <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-white/5 to-transparent rounded-bl-full pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                       {/* Top Metadata */}
                       <div className="flex items-center justify-between font-mono text-[9px] uppercase tracking-widest">
                          <div className="flex items-center gap-2 text-white/40">
                             <Fingerprint className="w-3 h-3 opacity-40" />
                             RECORDED · {stage.num}
                          </div>
                          <div className="text-[var(--decode-green)]/80 font-bold bg-[var(--decode-green)]/5 px-2 py-0.5 rounded border border-[var(--decode-green)]/10 shadow-[0_0_10px_rgba(57,217,120,0.05)]">
                             {stage.status}
                          </div>
                       </div>

                       {/* Visual Container */}
                       <div className="mt-3 group-hover:scale-[1.02] transition-transform duration-700 ease-out">
                         {stage.visual}
                       </div>

                       {/* Title & Desc */}
                       <div className="mt-5 flex-1 relative z-10">
                          <h3 className="font-mono text-[16px] font-bold tracking-[0.15em] text-white/90 flex items-center gap-4">
                             {stage.id}
                             <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                          </h3>
                          <p className="mt-3 text-[13px] text-white/40 leading-relaxed font-sans font-light">
                             {stage.desc}
                          </p>
                       </div>

                       {/* Hidden Technical Evidence (Reveals on Hover) */}
                       <div className="mt-0 pt-0 border-t border-white/0 grid grid-cols-1 gap-2.5 h-0 opacity-0 overflow-hidden group-hover:h-auto group-hover:opacity-100 group-hover:mt-4 group-hover:pt-4 group-hover:border-white/5 transition-all duration-500 ease-in-out">
                         {stage.details.map((det, i) => (
                           <div key={i} className="flex items-center gap-3 font-mono text-[9px] text-[var(--decode-green)]/70 tracking-widest uppercase">
                             <CheckCircle2 className="w-3 h-3" /> {det}
                           </div>
                         ))}
                       </div>
                    </div>
                 </motion.div>
               ))}
               
               {/* Final Terminal Node (Wow Detail) */}
               <div className="relative flex-shrink-0 w-full lg:w-[240px] flex flex-col justify-center items-center lg:items-start pl-4 opacity-80 group">
                 <div className="absolute -left-8 lg:-left-6 top-1/2 w-8 h-px bg-gradient-to-r from-[var(--decode-green)]/20 to-[var(--decode-green)]/60" />
                 
                 <div className="w-16 h-16 rounded-full border border-[var(--decode-green)]/40 bg-[#0e1d17] flex flex-col items-center justify-center gap-1 shadow-[0_0_40px_rgba(57,217,120,0.15)] relative z-10 group-hover:shadow-[0_0_60px_rgba(57,217,120,0.25)] transition-shadow duration-500">
                   <ShieldCheck className="w-6 h-6 text-[var(--decode-green)] drop-shadow-[0_0_8px_var(--decode-green)]" />
                 </div>
                 
                 <div className="mt-8 text-center lg:text-left bg-[#07110d]/50 p-4 rounded-xl border border-white/5 backdrop-blur-sm">
                   <div className="font-mono text-[11px] font-bold tracking-[0.2em] text-[var(--decode-green)] flex items-center justify-center lg:justify-start gap-2">
                     <CheckCircle2 className="w-3.5 h-3.5" /> VERIFIED
                   </div>
                   <div className="font-mono text-[9px] text-white/30 tracking-widest mt-2 mb-4">TRACE COMPLETE</div>
                   
                   {/* Provenance Chain */}
                   <div className="flex flex-col gap-2 font-mono text-[8px] text-white/40 uppercase tracking-widest border-l border-[var(--decode-green)]/20 pl-3">
                     <span className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> SOURCE</span>
                     <span className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-white/20" /> EXTRACTION</span>
                     <span className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-[var(--decode-green)]/50" /> VALIDATION</span>
                     <span className="flex items-center gap-2 text-[var(--decode-green)]"><div className="w-1 h-1 rounded-full bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)]" /> RECORD</span>
                   </div>
                 </div>
               </div>

            </div>
            
            {/* Tiny Progress Indicator */}
            <div className="absolute right-6 top-0 font-mono text-[9px] text-white/30 tracking-[0.2em] flex items-center gap-2 bg-[#050b08] px-3 border border-white/5 rounded-full shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--decode-green)] shadow-[0_0_5px_var(--decode-green)] animate-pulse" /> 6 / 6 VERIFIED
            </div>

          </div>
       </div>
       
       <style dangerouslySetInnerHTML={{__html: `
         .hide-scrollbar::-webkit-scrollbar { display: none; }
         .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
       `}} />
    </section>
  );
}
