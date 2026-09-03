"use client";

import { motion } from "framer-motion";
import { Lock, FileText, CheckCircle, Database, ShieldCheck, ChevronRight } from "lucide-react";

export function HowItWorks() {
  return (
    <section id="how-it-works" className="relative min-h-[100svh] flex flex-col justify-center py-24 lg:py-32 overflow-hidden bg-[var(--decode-bg)]">
      {/* Background Cinematic Glows */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(57,217,120,0.06)_0%,transparent_60%)] pointer-events-none" />
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="relative mx-auto w-full max-w-[1400px] px-6 sm:px-8 md:px-16 z-10">
        
        {/* Header */}
        <div className="reveal mx-auto mb-20 lg:mb-28 max-w-[800px] text-center">
          <div className="flex items-center justify-center gap-3 font-mono text-[12px] lg:text-[13px] font-medium uppercase tracking-[0.16em] text-[var(--decode-green)] before:inline-block before:h-px before:w-[22px] before:bg-[var(--decode-green)]">
            HOW VERIFICATION WORKS
          </div>
          <h2 className="mt-6 font-[family-name:var(--font-display)] text-[clamp(2.5rem,5vw,4rem)] font-medium leading-[1.1] tracking-[-0.01em] text-white">
            From Locked Figure to<br />Certified Record.
          </h2>
          <p className="mt-6 text-[clamp(1.1rem,1.5vw,1.35rem)] text-[var(--decode-muted)] max-w-[60ch] mx-auto leading-relaxed">
            Every chart is read, understood, and re-issued as structured data — nothing is guessed, everything is checked.
          </p>
        </div>

        {/* Pipeline Container */}
        <div className="reveal relative flex flex-col lg:flex-row items-center justify-center gap-12 lg:gap-4 w-full">
          
          {/* Data Pipeline Background Line (Desktop only) */}
          <div className="hidden lg:block absolute top-1/2 left-[15%] right-[15%] h-px bg-gradient-to-r from-white/10 via-[var(--decode-green)]/40 to-[var(--decode-green)]/80 -translate-y-1/2 z-0" />
          
          {/* Animated Particles on Pipeline */}
          <div className="hidden lg:block absolute top-1/2 left-[15%] right-[15%] h-px -translate-y-1/2 z-0 overflow-hidden">
             <motion.div
                className="w-24 h-full bg-gradient-to-r from-transparent via-[var(--decode-green)] to-transparent opacity-80"
                animate={{ x: ["-100%", "800%"] }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
             />
          </div>

          {/* LEFT: LOCKED FIGURE */}
          <div className="relative z-10 flex-1 w-full max-w-[450px] perspective-[1200px]">
            <motion.div 
              whileHover={{ rotateY: 5, rotateX: 2, scale: 1.02 }}
              className="rounded-2xl border border-white/10 bg-[#0e1d17]/80 backdrop-blur-xl p-8 shadow-[0_20px_40px_rgba(0,0,0,0.5)] relative overflow-hidden group transition-all duration-500"
            >
              {/* Scanline Animation */}
              <motion.div 
                animate={{ top: ["0%", "100%", "0%"] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[var(--decode-green)]/40 to-transparent z-20 pointer-events-none"
              />
              <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />

              <div className="relative z-10 mb-8 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="bg-black/40 p-3 rounded-lg border border-white/5 shadow-inner">
                    <FileText className="h-6 w-6 text-white/70" />
                  </div>
                  <div>
                    <div className="text-[17px] font-semibold text-white">Research Figure</div>
                    <div className="font-mono text-[10px] text-white/50 uppercase tracking-wider mt-1">SCANNED FROM SOURCE PDF</div>
                  </div>
                </div>
                <div className="bg-black/50 p-2.5 rounded-full border border-white/10 shadow-inner">
                  <Lock className="h-4 w-4 text-white/40" />
                </div>
              </div>

              {/* Locked Chart Visual */}
              <div className="relative h-[180px] border border-white/10 rounded-lg bg-black/40 p-4 flex items-end gap-3 overflow-hidden shadow-inner">
                {/* Bounding Box overlay */}
                <div className="absolute inset-3 border border-[var(--decode-green)]/20 border-dashed rounded flex items-center justify-center pointer-events-none z-10">
                  <div className="font-mono text-[9px] text-[var(--decode-green)]/50 absolute top-2 right-2 tracking-widest bg-[#0e1d17] px-1">OCR_DETECTED</div>
                </div>
                
                {/* Extraction Points */}
                <div className="absolute top-1/4 left-1/3 w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full shadow-[0_0_10px_var(--decode-green)] animate-pulse z-10" />
                <div className="absolute top-1/2 right-1/4 w-1.5 h-1.5 bg-[var(--decode-green)] rounded-full shadow-[0_0_10px_var(--decode-green)] animate-pulse z-10 delay-75" />
                
                {[35, 65, 45, 85, 60].map((h, i) => (
                  <div key={i} className="flex-1 bg-white/10 rounded-t-sm relative group-hover:bg-white/15 transition-colors duration-300" style={{ height: `${h}%` }}>
                    <div className="absolute -top-1 -left-1 w-2 h-2 border border-[var(--decode-green)]/0 group-hover:border-[var(--decode-green)]/50 rounded-full transition-colors duration-300" />
                  </div>
                ))}
              </div>

              {/* Badges */}
              <div className="mt-6 flex items-center justify-between gap-2 font-mono text-[9px] font-medium tracking-wider text-white/40 uppercase">
                <span className="bg-white/5 px-2.5 py-1.5 rounded border border-white/5">FIG. 03</span>
                <span className="bg-white/5 px-2.5 py-1.5 rounded border border-white/5">PDF • PAGE 07</span>
                <span className="bg-[#12251d] px-2.5 py-1.5 rounded border border-white/5 flex items-center gap-1.5 text-white/60">
                  <div className="w-1.5 h-1.5 rounded-full bg-orange-400/60 animate-pulse" />
                  SOURCE LOCKED
                </span>
              </div>
            </motion.div>
          </div>

          {/* CENTER: VERIFICATION ENGINE */}
          <div className="relative z-20 flex shrink-0 flex-col items-center justify-center my-4 lg:my-0 lg:mx-4">
            <div className="relative flex items-center justify-center w-40 h-40 rounded-full bg-[#0a140f]/80 backdrop-blur-2xl border border-[var(--decode-green)]/20 shadow-[0_0_60px_rgba(57,217,120,0.15),inset_0_0_20px_rgba(57,217,120,0.05)]">
              {/* Orbital Rings */}
              <motion.div 
                animate={{ rotate: 360 }} 
                transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
                className="absolute inset-[-15px] rounded-full border border-dashed border-[var(--decode-green)]/30"
              />
              <motion.div 
                animate={{ rotate: -360 }} 
                transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
                className="absolute inset-[-30px] rounded-full border border-[var(--decode-green)]/10"
              />
              
              {/* Inner Glowing Core */}
              <div className="absolute inset-6 rounded-full bg-[radial-gradient(circle_at_center,rgba(57,217,120,0.25),transparent_70%)] animate-pulse" />
              <ShieldCheck className="w-14 h-14 text-[var(--decode-green)] relative z-10 drop-shadow-[0_0_15px_rgba(57,217,120,0.5)]" strokeWidth={1.5} />
              
              {/* Data Particles */}
              {[...Array(8)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-[var(--decode-green)] rounded-full shadow-[0_0_5px_var(--decode-green)]"
                  style={{ top: "50%", left: "50%" }}
                  animate={{
                    x: [((i * 17) % 120) - 60, ((i * 31) % 250) - 125],
                    y: [((i * 23) % 120) - 60, ((i * 47) % 250) - 125],
                    opacity: [0, 1, 0]
                  }}
                  transition={{
                    duration: 2 + ((i * 7) % 3),
                    repeat: Infinity,
                    delay: ((i * 11) % 2)
                  }}
                />
              ))}
            </div>
            
            <div className="mt-12 flex flex-col items-center">
              <div className="font-mono text-[12px] font-bold tracking-[0.25em] text-white">VERIFICATION ENGINE</div>
              <div className="mt-4 flex items-center gap-1.5 font-mono text-[9px] text-[var(--decode-green)]/60 uppercase tracking-widest">
                <span>OCR</span> <ChevronRight className="w-3 h-3 opacity-50" /> 
                <span>STRUCTURE</span> <ChevronRight className="w-3 h-3 opacity-50" /> 
                <span>CERTIFY</span>
              </div>
              <div className="mt-4 bg-[var(--decode-green)]/10 text-[var(--decode-green)] border border-[var(--decode-green)]/20 px-4 py-1.5 rounded-full font-mono text-[10px] font-semibold flex items-center gap-2 shadow-[0_0_15px_rgba(57,217,120,0.1)]">
                <CheckCircle className="w-3.5 h-3.5" /> 92% VERIFIED
              </div>
            </div>
          </div>

          {/* RIGHT: CERTIFIED RECORD */}
          <div className="relative z-10 flex-1 w-full max-w-[450px]">
            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="rounded-2xl border border-[var(--decode-green)]/30 bg-[#0e1d17]/95 backdrop-blur-xl p-8 shadow-[0_0_50px_rgba(57,217,120,0.08),0_20px_40px_rgba(0,0,0,0.5)] relative overflow-hidden transition-transform duration-500"
            >
              {/* Cyan / Green subtle top glow */}
              <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-[var(--decode-green)]/0 via-[#00f2fe]/60 to-[var(--decode-green)]/0" />

              <div className="mb-8 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="bg-[var(--decode-green)]/10 p-3 rounded-lg border border-[var(--decode-green)]/20 shadow-inner">
                    <Database className="h-6 w-6 text-[var(--decode-green)]" />
                  </div>
                  <div>
                    <div className="text-[17px] font-semibold text-white">
                      Certified Record
                    </div>
                    <div className="font-mono text-[10px] text-[#00f2fe]/80 uppercase tracking-widest mt-1">STRUCTURED & EDITABLE</div>
                  </div>
                </div>
                <div className="bg-[#00f2fe]/10 text-[#00f2fe] px-3 py-1.5 rounded-md border border-[#00f2fe]/20 flex items-center gap-1.5 font-mono text-[9px] font-bold tracking-wider shadow-[0_0_10px_rgba(0,242,254,0.1)]">
                  <ShieldCheck className="w-3.5 h-3.5" /> VERIFIED
                </div>
              </div>

              {/* Clean Reconstructed Chart */}
              <div className="relative h-[180px] border-b border-l border-white/10 pl-6 pb-2 flex items-end gap-5">
                {/* Y-axis labels */}
                <div className="absolute -left-7 top-0 bottom-2 flex flex-col justify-between py-1 font-mono text-[9px] text-white/30 text-right w-5">
                  <span>100</span>
                  <span>50</span>
                  <span>0</span>
                </div>
                
                {/* Horizontal grid lines */}
                <div className="absolute left-0 right-0 top-1/2 h-px bg-white/5 pointer-events-none" />
                <div className="absolute left-0 right-0 top-0 h-px bg-white/5 pointer-events-none" />

                {[35, 65, 45, 85, 60].map((h, i) => (
                  <div key={i} className="flex-1 bg-gradient-to-t from-[var(--decode-green)]/80 to-[#00f2fe]/80 rounded-t-sm relative group shadow-[0_0_15px_rgba(57,217,120,0.2)]" style={{ height: `${h}%` }}>
                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-mono text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 drop-shadow-md">
                      {h}
                    </div>
                  </div>
                ))}
              </div>

              {/* X-axis labels */}
              <div className="flex items-center gap-5 pl-6 mt-3 font-mono text-[9px] text-white/30 text-center uppercase tracking-wider">
                {['JAN', 'FEB', 'MAR', 'APR', 'MAY'].map((lbl, i) => (
                  <div key={i} className="flex-1">{lbl}</div>
                ))}
              </div>

              {/* Data Table Strip */}
              <div className="mt-7 pt-5 border-t border-white/5">
                <div className="grid grid-cols-4 gap-2 font-mono text-[8px] text-white/30 uppercase tracking-widest mb-2">
                  <div>Source</div>
                  <div>Extracted</div>
                  <div>Unit</div>
                  <div className="text-right">Conf</div>
                </div>
                <div className="grid grid-cols-4 gap-2 font-mono text-[11px] font-medium text-white/90">
                  <div className="text-white/60">FIG. 03</div>
                  <div className="text-white/90">5 Points</div>
                  <div className="text-white/60">Px / %</div>
                  <div className="text-right text-[var(--decode-green)] flex items-center justify-end gap-1">
                    92.4% <CheckCircle className="w-3 h-3" />
                  </div>
                </div>
              </div>
              
            </motion.div>
          </div>
          
        </div>
      </div>
    </section>
  );
}
