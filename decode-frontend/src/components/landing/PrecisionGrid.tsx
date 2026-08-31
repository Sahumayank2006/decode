"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { Crosshair, ShieldCheck, CheckCircle2 } from "lucide-react";

const STAGES = [
  {
    id: "01",
    name: "DETECT",
    subtitle: "SMART VISION",
    metric: "REGIONS FOUND: 6 / 6",
    visual: (
      <div className="relative h-44 bg-black/40 border border-white/5 rounded-lg flex items-center justify-center p-4 shadow-inner">
         <div className="w-24 h-32 bg-white/5 border border-white/10 rounded relative p-2 flex flex-col gap-2 shadow-[0_0_10px_rgba(0,0,0,0.5)]">
            {/* Regions */}
            <div className="h-8 border border-[var(--decode-green)]/40 bg-[var(--decode-green)]/10 rounded-sm relative">
               <div className="absolute -top-1 -right-1 w-2 h-2 bg-[var(--decode-green)] rounded-full animate-pulse shadow-[0_0_5px_var(--decode-green)]" />
               <div className="absolute bottom-0 right-1 text-[5px] font-mono text-[var(--decode-green)] tracking-widest">FIG. 03</div>
            </div>
            <div className="h-6 border border-white/20 border-dashed rounded-sm relative flex items-center justify-center overflow-hidden">
               <motion.div animate={{ left: ["-10%", "110%", "-10%"] }} transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }} className="absolute w-px h-full bg-white/50 shadow-[0_0_5px_white]" />
            </div>
            <div className="h-6 border border-[var(--decode-green)]/40 bg-[var(--decode-green)]/10 rounded-sm relative">
               <div className="absolute bottom-0 right-1 text-[5px] font-mono text-[var(--decode-green)] tracking-widest">TBL. 01</div>
            </div>
         </div>
         <div className="absolute top-3 left-3 flex flex-col gap-1.5">
           <div className="font-mono text-[6px] text-white/30 tracking-widest bg-white/5 px-1 py-0.5 rounded border border-white/10">OCR-VALID</div>
           <div className="font-mono text-[6px] text-white/30 tracking-widest bg-white/5 px-1 py-0.5 rounded border border-white/10">PAGE-07</div>
         </div>
      </div>
    )
  },
  {
    id: "02",
    name: "EXTRACT",
    subtitle: "INTELLIGENT OCR",
    metric: "FIELD VARIANCE: 1.2%",
    visual: (
      <div className="relative h-44 bg-black/40 border border-white/5 rounded-lg p-4 flex gap-4 items-center shadow-inner overflow-hidden">
         <div className="w-16 h-28 border border-white/10 relative overflow-hidden flex items-end p-1.5 gap-1.5 shadow-md bg-white/5 rounded-sm">
            <motion.div animate={{ top: ["0%", "100%", "0%"] }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }} className="absolute left-0 right-0 h-[2px] bg-[#00f2fe]/60 shadow-[0_0_15px_#00f2fe] z-10" />
            <div className="flex-1 bg-white/30 h-[40%] rounded-t-sm" />
            <div className="flex-1 bg-white/30 h-[80%] rounded-t-sm" />
            <div className="flex-1 bg-white/30 h-[60%] rounded-t-sm" />
         </div>
         <div className="flex-1 flex flex-col justify-center gap-3 relative z-10">
            <div className="flex items-center gap-2">
               <div className="h-px w-6 bg-[#00f2fe]/40" />
               <div className="text-[8px] font-mono border border-white/10 px-1.5 py-0.5 bg-black/50 backdrop-blur-md rounded text-[#00f2fe] flex gap-2 w-full justify-between shadow-sm">
                 <span>AXIS &rarr; X</span> <span className="text-white/40">98.7%</span>
               </div>
            </div>
            <div className="flex items-center gap-2">
               <div className="h-px w-4 bg-[var(--decode-green)]/40" />
               <div className="text-[8px] font-mono border border-white/10 px-1.5 py-0.5 bg-black/50 backdrop-blur-md rounded text-[var(--decode-green)] flex gap-2 w-full justify-between shadow-sm">
                 <span>VALUE &rarr; 82</span> <span className="text-white/40">96.2%</span>
               </div>
            </div>
            <div className="flex items-center gap-2">
               <div className="h-px w-8 bg-purple-400/40" />
               <div className="text-[8px] font-mono border border-white/10 px-1.5 py-0.5 bg-black/50 backdrop-blur-md rounded text-purple-400 flex gap-2 w-full justify-between shadow-sm">
                 <span>LBL &rarr; CAT</span> <span className="text-white/40">99.1%</span>
               </div>
            </div>
         </div>
      </div>
    )
  },
  {
    id: "03",
    name: "STRUCTURE",
    subtitle: "ORGANIZED DATA",
    metric: "SCHEMA MATCH: 98%",
    visual: (
      <div className="relative h-44 bg-black/40 border border-white/5 rounded-lg p-4 flex flex-col items-center justify-center shadow-inner overflow-hidden">
         <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:10px_10px] pointer-events-none" />
         
         <div className="relative z-10 w-full max-w-[120px] h-20 border-l border-b border-[#00f2fe]/40 flex items-end gap-3 pl-3 pb-1">
            {[40, 80, 60].map((h, i) => (
               <motion.div 
                 key={i} 
                 initial={{ height: 0 }}
                 animate={{ height: `${h}%` }}
                 transition={{ duration: 0.8, delay: i * 0.15, repeat: Infinity, repeatType: "reverse", repeatDelay: 3 }}
                 className="flex-1 bg-gradient-to-t from-[#00f2fe]/50 to-[#00f2fe]/10 rounded-t-sm relative border border-[#00f2fe]/50 shadow-[0_0_15px_rgba(0,242,254,0.1)]"
               >
                 <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white rounded-full shadow-[0_0_8px_white] border-2 border-[#00f2fe]" />
                 <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white rounded-full shadow-[0_0_8px_white] border-2 border-[#00f2fe]" />
               </motion.div>
            ))}
         </div>
         
         <div className="relative z-10 flex gap-2 mt-5">
           <span className="font-mono text-[7px] font-bold tracking-widest border border-[#00f2fe]/30 text-[#00f2fe] bg-[#00f2fe]/10 px-1.5 py-0.5 rounded shadow-sm">VECTOR</span>
           <span className="font-mono text-[7px] font-bold tracking-widest border border-white/20 text-white/60 bg-white/5 px-1.5 py-0.5 rounded shadow-sm">VALUE</span>
           <span className="font-mono text-[7px] font-bold tracking-widest border border-white/20 text-white/60 bg-white/5 px-1.5 py-0.5 rounded shadow-sm">LABEL</span>
         </div>
      </div>
    )
  },
  {
    id: "04",
    name: "VERIFY",
    subtitle: "TRUSTED ACCURACY",
    metric: "FINAL RISK: LOW",
    visual: (
      <div className="relative h-44 bg-black/40 border border-white/5 rounded-lg flex overflow-hidden shadow-inner">
        <div className="flex-1 border-r border-dashed border-white/20 p-3 relative flex items-center justify-center bg-black/30">
          <div className="absolute top-2 left-2 text-[7px] font-mono text-white/40 tracking-widest bg-black/50 px-1 py-0.5 rounded">SOURCE</div>
          <div className="w-14 h-14 bg-white/10 rounded flex flex-col gap-1.5 p-2.5 shadow-inner">
            <div className="flex-1 bg-white/20 rounded-sm" />
            <div className="h-2 bg-white/20 rounded-sm" />
          </div>
        </div>
        
        {/* Verification Checkpoint Core */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-[#050b08] border border-white/10 flex items-center justify-center z-20 shadow-[0_0_15px_rgba(0,0,0,0.6)]">
           <motion.div animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: "linear" }} className="absolute inset-0 border border-dashed border-[#00f2fe]/60 rounded-full" />
           <div className="w-2 h-2 bg-[#00f2fe] rounded-full shadow-[0_0_8px_#00f2fe] animate-pulse" />
        </div>

        <div className="flex-1 p-3 relative flex items-center justify-center bg-[#00f2fe]/5">
          <div className="absolute top-2 right-2 text-[7px] font-mono text-[#00f2fe]/80 tracking-widest bg-[#00f2fe]/10 px-1 py-0.5 rounded border border-[#00f2fe]/20">RECONSTRUCTED</div>
          
          <div className="absolute bottom-2 right-2 flex flex-col gap-1">
             <div className="text-[6px] font-mono text-[#00f2fe] flex items-center gap-1"><CheckCircle2 className="w-2.5 h-2.5" /> GEOMETRY</div>
             <div className="text-[6px] font-mono text-[#00f2fe] flex items-center gap-1"><CheckCircle2 className="w-2.5 h-2.5" /> COLOR</div>
             <div className="text-[6px] font-mono text-[#00f2fe] flex items-center gap-1"><CheckCircle2 className="w-2.5 h-2.5" /> DATA</div>
          </div>

          <div className="w-14 h-14 border border-[#00f2fe]/50 bg-[#00f2fe]/20 rounded-lg shadow-[0_0_20px_rgba(0,242,254,0.2)] flex items-center justify-center">
            <ShieldCheck className="w-7 h-7 text-[#00f2fe] drop-shadow-[0_0_8px_#00f2fe]" strokeWidth={1.5} />
          </div>
        </div>
      </div>
    )
  }
];

export function PrecisionGrid() {
  const [activeStage, setActiveStage] = useState(0);
  const [isDesktop, setIsDesktop] = useState(true);

  useEffect(() => {
    const handleResize = () => setIsDesktop(window.innerWidth >= 1024);
    handleResize(); // Init
    window.addEventListener('resize', handleResize);
    
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev + 1) % 4);
    }, 4000);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const conf = [92.0, 95.0, 97.0, 98.4][activeStage];

  return (
    <section id="precision" className="relative min-h-[120svh] flex flex-col justify-center py-32 overflow-hidden bg-[#040806] text-white">
      
      {/* Background Grid & Measurements */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(57,217,120,0.02)_0%,transparent_60%)] pointer-events-none" />
      
      <div className="absolute top-0 w-full h-8 border-b border-white/5 flex items-end justify-between px-10 pb-1 pointer-events-none">
        {[...Array(24)].map((_, i) => <div key={i} className="h-2 w-px bg-white/10" />)}
      </div>

      <div className="relative max-w-[1600px] w-full mx-auto px-6 sm:px-12 z-10 flex flex-col justify-center h-full">
        
        {/* Header & Confidence Metric */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end mb-20 gap-8">
          <div className="max-w-2xl">
            <div className="font-mono text-[10px] tracking-[0.2em] font-bold text-[#00f2fe] uppercase flex items-center gap-3 before:w-6 before:h-px before:bg-[#00f2fe] shadow-sm">
              INSPECTION STANDARD
            </div>
            <h2 className="mt-6 font-display text-[clamp(2.5rem,5vw,4rem)] font-medium leading-[1.1] tracking-tight text-white drop-shadow-sm">
              Precision at Every Stage.
            </h2>
            <p className="mt-6 font-mono text-[12px] lg:text-[14px] text-white/50 leading-relaxed tracking-wider border-l-2 border-[#00f2fe]/30 pl-4">
              Intelligent detection. Accurate extraction. Trusted results — verified at each checkpoint, not assumed at the end.
            </p>
          </div>

          <div className="bg-[#0a140f]/80 backdrop-blur-md border border-white/10 rounded-xl p-5 min-w-[220px] shadow-[0_20px_40px_rgba(0,0,0,0.6)]">
            <div className="font-mono text-[9px] font-bold text-white/40 tracking-[0.2em] uppercase mb-2">Inspection Confidence</div>
            <div className="flex items-baseline gap-2 text-[#00f2fe]">
              <span className="text-5xl font-bold font-mono tracking-tighter drop-shadow-[0_0_10px_rgba(0,242,254,0.3)]">{conf.toFixed(1)}</span>
              <span className="text-xl font-mono opacity-60">%</span>
            </div>
          </div>
        </div>

        {/* The Inspection Rail Container */}
        <div className="relative w-full">
          
          {/* Precision Rail Line */}
          <div className="absolute left-8 lg:left-0 top-0 bottom-0 lg:top-1/2 lg:bottom-auto w-px lg:w-full lg:h-px bg-white/5 z-0" />
          
          {/* Travelling Data Signal */}
          <motion.div 
            animate={{ 
              top: isDesktop ? "50%" : `calc(${12.5 + activeStage * 25}%)`,
              left: isDesktop ? `calc(${12.5 + activeStage * 25}%)` : 32,
              translateX: "-50%",
              translateY: "-50%"
            }}
            transition={{ type: "spring", stiffness: 60, damping: 25 }}
            className="absolute w-2 h-2 lg:w-3 lg:h-3 rounded-full bg-[#00f2fe] shadow-[0_0_20px_#00f2fe] z-20"
          />

          {/* Precision Lens (Desktop only) */}
          <motion.div 
            animate={{ left: `calc(${12.5 + activeStage * 25}% - 56px)` }}
            transition={{ type: "spring", stiffness: 60, damping: 25 }}
            className="hidden lg:flex absolute top-1/2 -translate-y-1/2 w-28 h-28 rounded-full border border-[#00f2fe]/40 bg-[#00f2fe]/5 backdrop-blur-[2px] shadow-[0_0_40px_rgba(0,242,254,0.15),inset_0_0_20px_rgba(0,242,254,0.1)] z-30 pointer-events-none items-center justify-center"
          >
            <Crosshair className="w-10 h-10 text-[#00f2fe]/30" strokeWidth={1} />
            <div className="absolute -bottom-6 font-mono text-[9px] text-[#00f2fe] font-bold tracking-[0.2em] whitespace-nowrap drop-shadow-sm">LENS_ACTIVE</div>
          </motion.div>

          {/* Grid of 4 Stages */}
          <div className="relative z-10 pl-16 lg:pl-0 grid grid-cols-1 lg:grid-cols-4 gap-12 lg:gap-6 py-8">
            {STAGES.map((stage, idx) => {
              const isActive = activeStage === idx;
              const isPassed = activeStage > idx;
              const isVerify = idx === 3;

              return (
                <div key={idx} className="relative flex flex-col group cursor-default">
                  
                  {/* Connector Node */}
                  <div className={`absolute -left-[42px] lg:left-1/2 top-10 lg:-top-11 w-5 h-5 rounded-full border-2 bg-[#040806] lg:-translate-x-1/2 z-10 transition-all duration-500 flex items-center justify-center ${isActive || isPassed ? 'border-[#00f2fe] shadow-[0_0_10px_rgba(0,242,254,0.3)]' : 'border-white/10'}`}>
                    {(isActive || isPassed) && <div className="w-2 h-2 bg-[#00f2fe] rounded-full" />}
                  </div>

                  {/* Glass Panel */}
                  <div className={`flex-1 rounded-xl border p-7 bg-[#0a140f]/60 backdrop-blur-xl transition-all duration-700 ease-out relative overflow-hidden ${
                    isActive 
                      ? isVerify 
                        ? 'border-[#00f2fe]/60 shadow-[0_20px_50px_rgba(0,0,0,0.6),inset_0_0_30px_rgba(0,242,254,0.15)] scale-[1.03]' 
                        : 'border-[#00f2fe]/40 shadow-[0_20px_40px_rgba(0,0,0,0.5),inset_0_0_20px_rgba(0,242,254,0.05)] scale-[1.02]' 
                      : isPassed 
                        ? 'border-white/15 opacity-80' 
                        : 'border-white/5 opacity-40 grayscale-[40%]'
                  }`}>
                    
                    {/* Active Corner Glow */}
                    {isActive && <div className={`absolute top-0 right-0 w-32 h-32 rounded-bl-full pointer-events-none bg-gradient-to-bl ${isVerify ? 'from-[#00f2fe]/20' : 'from-[#00f2fe]/10'} to-transparent`} />}
                    
                    {/* Header: Number & Name */}
                    <div className="flex items-baseline justify-between mb-3 relative z-10">
                      <div className={`font-display text-4xl font-bold tracking-tighter transition-colors duration-500 ${isActive ? 'text-[#00f2fe] drop-shadow-[0_0_10px_rgba(0,242,254,0.3)]' : 'text-white/20'}`}>
                        {stage.id}
                      </div>
                      <div className="font-mono text-[9px] font-bold tracking-[0.2em] text-white/30 uppercase bg-black/40 px-2 py-1 rounded border border-white/5">
                        TRACE-{stage.id}8A
                      </div>
                    </div>
                    <h3 className="font-mono text-[15px] tracking-[0.15em] font-bold text-white mb-1.5 uppercase">{stage.name}</h3>
                    <div className="font-mono text-[9px] text-white/40 tracking-[0.2em] uppercase mb-8">{stage.subtitle}</div>

                    {/* Stage Visual */}
                    <div className={`mb-8 relative z-10 transition-transform duration-500 ${isActive ? 'scale-100' : 'scale-[0.98]'}`}>
                      {stage.visual}
                    </div>

                    {/* Metric Strip */}
                    <div className={`mt-auto border-t pt-4 font-mono text-[10px] tracking-widest flex items-center justify-between transition-colors duration-500 ${isActive ? 'border-[#00f2fe]/30 text-[#00f2fe]' : 'border-white/10 text-white/30'}`}>
                      <span className={isVerify && isActive ? 'font-bold' : ''}>{stage.metric}</span>
                      {isActive && <div className="w-1.5 h-1.5 rounded-full bg-[#00f2fe] shadow-[0_0_5px_#00f2fe] animate-pulse" />}
                    </div>
                  </div>
                  
                </div>
              )
            })}
          </div>
        </div>
        
        {/* Bottom Signature */}
        <div className="mt-24 flex flex-col items-center">
          <div className="font-mono text-[9px] font-bold text-white/20 tracking-[0.3em] uppercase flex items-center gap-5">
            <span>ONE FIGURE</span>
            <span className="w-1 h-1 bg-white/10 rounded-full" />
            <span>FOUR CHECKPOINTS</span>
            <span className="w-1 h-1 bg-white/10 rounded-full" />
            <span>ZERO ASSUMPTIONS</span>
          </div>
          <div className="mt-5 flex items-center gap-5 font-mono text-[10px] font-bold text-[var(--decode-green)]/60 tracking-widest bg-white/5 px-6 py-2.5 rounded-full border border-white/5">
            <span className="flex items-center gap-1.5">DETECTED <CheckCircle2 className="w-3 h-3" /></span>
            <span className="text-white/10">/</span>
            <span className="flex items-center gap-1.5">EXTRACTED <CheckCircle2 className="w-3 h-3" /></span>
            <span className="text-white/10">/</span>
            <span className="flex items-center gap-1.5">STRUCTURED <CheckCircle2 className="w-3 h-3" /></span>
            <span className="text-white/10">/</span>
            <span className="flex items-center gap-1.5 text-[#00f2fe] drop-shadow-[0_0_5px_#00f2fe]">VERIFIED <CheckCircle2 className="w-3 h-3" /></span>
          </div>
        </div>
      </div>
    </section>
  );
}
