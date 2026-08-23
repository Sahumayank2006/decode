"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, useInView } from "framer-motion";
import {
  FileSearch, BarChart3, ShieldCheck, ArrowRight,
  Layers, Download, ScanLine
} from "lucide-react";

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATION VARIANTS
   ═══════════════════════════════════════════════════════════════════════════ */

const fadeUp = {
  hidden: { opacity: 0, y: 60 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.15, duration: 1.2, ease: "easeOut" as const },
  }),
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 1.5, ease: "easeOut" as const } },
};

/* ═══════════════════════════════════════════════════════════════════════════
   DATA
   ═══════════════════════════════════════════════════════════════════════════ */

const PIPELINE = [
  { num: "01", title: "INGEST",      icon: FileSearch },
  { num: "02", title: "DETECT",      icon: ScanLine },
  { num: "03", title: "EXTRACT",     icon: Layers },
  { num: "04", title: "RECONSTRUCT", icon: BarChart3 },
  { num: "05", title: "COMPLY",      icon: ShieldCheck },
  { num: "06", title: "EXPORT",      icon: Download },
];

/* ═══════════════════════════════════════════════════════════════════════════
   REUSABLE SECTION WRAPPER (MASSIVE WHITESPACE)
   ═══════════════════════════════════════════════════════════════════════════ */

function Section({
  children, className = "", id, dark = true
}: {
  children: React.ReactNode; className?: string; id?: string; dark?: boolean;
}) {
  return (
    <section
      id={id}
      className={`relative px-6 md:px-12 lg:px-24 py-32 md:py-48 lg:py-[200px] ${
        dark
          ? "bg-navy-900 text-white"
          : "bg-white text-navy-950"
      } ${className}`}
    >
      <div className="max-w-[1400px] mx-auto w-full">
        {children}
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════════════════════════════ */

export default function LandingPage() {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);

  // Scroll listener for navbar
  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  // Pipeline scroll activation
  const pipelineRef = useRef<HTMLDivElement>(null);
  const pipelineInView = useInView(pipelineRef, { once: false, amount: 0.3 });
  const [activePipe, setActivePipe] = useState(-1);

  useEffect(() => {
    if (!pipelineInView) { setActivePipe(-1); return; }
    let i = 0;
    const iv = setInterval(() => {
      setActivePipe(i);
      i++;
      if (i >= PIPELINE.length) clearInterval(iv);
    }, 600);
    return () => clearInterval(iv);
  }, [pipelineInView]);

  return (
    <div className="bg-navy-900 min-h-screen">

      {/* ═══════════════════════════════════════════════════════════════════
          NAVIGATION
          ═══════════════════════════════════════════════════════════════════ */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-700 ${
        scrolled
          ? "bg-navy-900/90 backdrop-blur-2xl shadow-[0_1px_0_rgba(255,255,255,0.05)]"
          : "bg-transparent py-4"
      }`}>
        <div className="max-w-[1440px] mx-auto px-8 md:px-16 lg:px-24 py-6 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <div className="w-10 h-10 bg-brand flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="text-xl font-bold tracking-tight text-white leading-none">DECODE</div>
              <div className="text-[10px] font-semibold tracking-[0.2em] uppercase text-slate-400 mt-1.5 hidden sm:block">
                Scientific Data Extraction Platform
              </div>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-12 text-[15px] font-medium text-slate-400 tracking-wide">
            <a href="#platform" className="hover:text-white transition-colors duration-300">Platform</a>
            <a href="#pipeline" className="hover:text-white transition-colors duration-300">How It Works</a>
            <a href="#capabilities" className="hover:text-white transition-colors duration-300">Capabilities</a>
            <a href="#compliance" className="hover:text-white transition-colors duration-300">Compliance</a>
          </div>

          <div className="flex items-center gap-8">
            <button className="hidden md:block text-[15px] font-medium text-slate-400 hover:text-white transition-colors">
              Sign In
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="px-8 py-3 bg-white text-navy-950 font-semibold text-[15px] hover:bg-slate-100 transition-all duration-300"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 01: THE HERO — Massive scale
          ═══════════════════════════════════════════════════════════════════ */}
      <Section className="min-h-[100vh] flex items-center pt-40 bg-grid-dark" id="platform">
        <div className="grid xl:grid-cols-[1fr_1.2fr] gap-20 items-center w-full">
          {/* ── Left: Simplified Content ───────────────────────────────── */}
          <motion.div
            initial="hidden" animate="visible"
            variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          >
            <motion.div variants={fadeUp} custom={0}
              className="text-[12px] font-bold tracking-[0.2em] uppercase text-accent-cyan mb-8"
            >
              AI-Powered Scientific Chart Intelligence
            </motion.div>

            <motion.h1 variants={fadeUp} custom={1}
              className="text-6xl sm:text-7xl md:text-8xl lg:text-[6.5rem] font-bold leading-[1.05] tracking-tight mb-10"
            >
              Extract.<br />
              Reconstruct.<br />
              Comply.
            </motion.h1>

            <motion.p variants={fadeUp} custom={2}
              className="text-xl md:text-2xl text-slate-400 leading-relaxed max-w-xl mb-16 font-light"
            >
              Transform charts and graphs embedded in research papers into
              editable, structured datasets and interactive visualizations —
              with built-in compliance analysis for responsible academic reuse.
            </motion.p>

            <motion.div variants={fadeUp} custom={3} className="flex flex-col sm:flex-row gap-6">
              <button
                onClick={() => router.push("/dashboard")}
                className="px-10 py-5 bg-brand text-white font-semibold text-lg hover:bg-brand-light transition-all duration-300 flex items-center justify-center gap-4"
              >
                Start Decoding
                <ArrowRight className="w-6 h-6" />
              </button>
              <button
                onClick={() => document.getElementById("figure-to-intelligence")?.scrollIntoView({ behavior: "smooth" })}
                className="px-10 py-5 border border-navy-600 text-slate-300 font-semibold text-lg hover:text-white transition-all duration-300 flex items-center justify-center"
              >
                Explore the Platform
              </button>
            </motion.div>
          </motion.div>

          {/* ── Right: ONE Massive Visualization ───────────────────────── */}
          <motion.div initial="hidden" animate="visible" variants={scaleIn} className="relative w-full h-[600px] xl:h-[750px] bg-navy-950 rounded-2xl border border-navy-700 shadow-2xl overflow-hidden flex items-center justify-center">
            <div className="absolute inset-0 bg-grid-dark opacity-30" />
            
            {/* The unified product story inside the hero */}
            <div className="relative z-10 w-[80%] h-[70%] flex gap-8">
                {/* PDF Enter */}
                <motion.div 
                    className="flex-1 bg-white border border-slate-200 p-6 flex flex-col justify-end grayscale opacity-90 shadow-lg"
                    initial={{ x: -100, opacity: 0 }}
                    animate={{ x: 0, opacity: 0.9 }}
                    transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
                >
                    <div className="h-6 w-32 bg-slate-200 mb-8" />
                    <div className="flex items-end gap-2 h-40">
                        <div className="flex-1 bg-slate-300 h-[40%]" />
                        <div className="flex-1 bg-slate-300 h-[70%]" />
                        <div className="flex-1 bg-slate-300 h-[50%]" />
                        <div className="flex-1 bg-slate-300 h-[90%]" />
                    </div>
                    <div className="h-px bg-slate-300 mt-2 w-full" />
                </motion.div>

                {/* Scan Overlay (Center) */}
                <motion.div 
                    className="absolute inset-0 z-20 flex items-center justify-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 2.5, duration: 1 }}
                >
                    <div className="w-[110%] h-[120%] border-4 border-accent-cyan bg-accent-cyan/10 relative flex items-center justify-center">
                        <div className="scan-line" />
                        <div className="px-6 py-3 bg-navy-900 text-accent-cyan font-mono text-xl tracking-widest border border-accent-cyan shadow-[0_0_40px_rgba(6,182,212,0.4)]">
                            DETECTING CHART REGION
                        </div>
                    </div>
                </motion.div>

                {/* Reconstructed Output */}
                <motion.div 
                    className="flex-1 bg-navy-900 border border-brand p-6 flex flex-col justify-end shadow-lg"
                    initial={{ x: 100, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 1.5, ease: "easeOut", delay: 4 }}
                >
                    <div className="h-6 w-32 bg-brand/20 mb-8" />
                    <div className="flex items-end gap-2 h-40">
                        <motion.div className="flex-1 bg-brand h-[40%]" initial={{ height: 0 }} animate={{ height: "40%" }} transition={{ delay: 5 }} />
                        <motion.div className="flex-1 bg-brand h-[70%]" initial={{ height: 0 }} animate={{ height: "70%" }} transition={{ delay: 5.1 }} />
                        <motion.div className="flex-1 bg-brand h-[50%]" initial={{ height: 0 }} animate={{ height: "50%" }} transition={{ delay: 5.2 }} />
                        <motion.div className="flex-1 bg-brand h-[90%]" initial={{ height: 0 }} animate={{ height: "90%" }} transition={{ delay: 5.3 }} />
                    </div>
                    <div className="h-px bg-slate-600 mt-2 w-full" />
                </motion.div>
            </div>
          </motion.div>
        </div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 02: THE TRANSFORMATION
          ═══════════════════════════════════════════════════════════════════ */}
      <Section id="figure-to-intelligence" dark={false} className="border-t border-slate-200">
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.3 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="text-center mb-32"
        >
          <motion.h2 variants={fadeUp} custom={0}
            className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] text-navy-950 mb-8"
          >
            From Research Figure<br />
            <span className="text-brand">to Editable Intelligence.</span>
          </motion.h2>
        </motion.div>

        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.3 }}
          variants={scaleIn}
          className="w-full aspect-[21/9] bg-slate-50 border border-slate-200 flex items-center justify-between p-12 lg:p-24 shadow-2xl relative"
        >
            <div className="w-[30%] h-full bg-white border border-slate-200 shadow-md p-10 grayscale flex flex-col items-center justify-end">
                <div className="text-slate-400 font-mono text-sm tracking-widest mb-10">ORIGINAL FIGURE</div>
                <div className="w-full h-px bg-slate-300 mb-2" />
                <div className="flex items-end gap-4 w-full h-[60%]">
                    <div className="flex-1 bg-slate-400 h-[80%]" />
                    <div className="flex-1 bg-slate-400 h-[60%]" />
                    <div className="flex-1 bg-slate-400 h-[100%]" />
                </div>
                <div className="w-full h-px bg-slate-300 mt-2" />
            </div>

            <div className="flex-1 flex justify-center">
                <ArrowRight className="w-20 h-20 text-brand opacity-20" />
            </div>

            <div className="w-[45%] h-full bg-navy-900 border border-navy-800 shadow-2xl p-12 flex flex-col items-center justify-end relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-dark opacity-10" />
                <div className="text-brand font-mono text-sm tracking-widest mb-10 z-10">RECONSTRUCTED SVG</div>
                <div className="flex items-end gap-4 w-full h-[70%] z-10">
                    <div className="flex-1 bg-brand h-[80%] shadow-[0_0_30px_rgba(37,99,235,0.4)]" />
                    <div className="flex-1 bg-brand-light h-[60%] shadow-[0_0_30px_rgba(59,130,246,0.4)]" />
                    <div className="flex-1 bg-accent-cyan h-[100%] shadow-[0_0_30px_rgba(6,182,212,0.4)]" />
                </div>
                <div className="w-full h-px bg-slate-700 mt-4 z-10" />
            </div>
        </motion.div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 03: THE PIPELINE
          ═══════════════════════════════════════════════════════════════════ */}
      <Section id="pipeline" className="border-t border-navy-800">
        <div className="text-center mb-40">
          <motion.h2
            initial="hidden" whileInView="visible" viewport={{ once: true }}
            variants={fadeUp} custom={0}
            className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-8"
          >
            Six Stages.<br />
            <span className="text-slate-500">One Intelligent Workflow.</span>
          </motion.h2>
        </div>

        <div ref={pipelineRef} className="relative max-w-full">
          <div className="hidden lg:block absolute top-[40px] left-0 right-0 h-px bg-navy-800" />
          <div
            className="hidden lg:block absolute top-[40px] left-0 h-[2px] bg-brand transition-all duration-1000 ease-out"
            style={{ width: `${Math.max(0, (activePipe / (PIPELINE.length - 1)) * 100)}%` }}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-16 lg:gap-8">
            {PIPELINE.map((step, i) => (
              <motion.div
                key={step.num}
                initial="hidden" whileInView="visible" viewport={{ once: true }}
                variants={fadeUp} custom={i}
                className="relative text-center lg:text-left flex flex-col items-center lg:items-start"
              >
                <div className={`w-20 h-20 mb-8 flex items-center justify-center transition-all duration-700 shrink-0 ${
                  i <= activePipe
                    ? "bg-brand text-white"
                    : "bg-navy-950 text-slate-600 border border-navy-800"
                }`}>
                  <step.icon className="w-8 h-8" />
                </div>
                <div className="text-sm font-mono text-slate-500 mb-3">{step.num}</div>
                <h3 className={`text-2xl font-bold tracking-widest transition-colors duration-700 ${
                  i <= activePipe ? "text-white" : "text-slate-600"
                }`}>{step.title}</h3>
              </motion.div>
            ))}
          </div>
        </div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 04: THE PRODUCT (3 Massive Experiences)
          ═══════════════════════════════════════════════════════════════════ */}
      <Section id="capabilities" dark={false} className="border-t border-slate-200">
        <div className="text-center mb-48">
          <motion.h2 initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp} custom={0}
            className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight text-navy-950"
          >Precision at Every Stage.</motion.h2>
        </div>

        {/* 1. DETECT & EXTRACT */}
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="grid lg:grid-cols-[1fr_1.5fr] gap-24 items-center mb-[250px]"
        >
          <motion.div variants={fadeUp} custom={0}>
            <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-navy-950 mb-8">Detect & Extract.</h3>
            <p className="text-2xl text-slate-500 leading-relaxed font-light">
              Advanced computer vision identifies chart regions, while morphological analysis and OCR reverse-engineer numerical values and metadata directly from pixel data.
            </p>
          </motion.div>
          <motion.div variants={scaleIn} className="w-full aspect-video bg-slate-100 border border-slate-200 p-8 flex gap-8">
             <div className="flex-1 bg-white shadow flex items-center justify-center relative">
                 <div className="absolute inset-4 border-2 border-brand" />
                 <span className="text-brand font-mono font-bold tracking-widest bg-white px-2">CHART DETECTED</span>
             </div>
             <div className="w-[40%] bg-white shadow p-8 font-mono text-lg text-slate-600">
                 <div className="mb-4 text-slate-400">RAW DATA</div>
                 <div className="flex justify-between border-b pb-2 mb-2"><span>Var A</span><span className="text-navy-950 font-bold">14.2</span></div>
                 <div className="flex justify-between border-b pb-2 mb-2"><span>Var B</span><span className="text-navy-950 font-bold">8.7</span></div>
                 <div className="flex justify-between border-b pb-2 mb-2"><span>Var C</span><span className="text-navy-950 font-bold">22.4</span></div>
             </div>
          </motion.div>
        </motion.div>

        {/* 2. RECONSTRUCT */}
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="grid lg:grid-cols-[1.5fr_1fr] gap-24 items-center mb-[250px]"
        >
          <motion.div variants={scaleIn} className="order-2 lg:order-1 w-full aspect-video bg-navy-900 p-12 flex flex-col justify-end relative shadow-2xl">
             <div className="absolute top-12 left-12 flex gap-4">
                 {["BAR", "LINE", "SCATTER", "PIE"].map(t => (
                     <div key={t} className={`px-6 py-2 border ${t === "BAR" ? "border-brand text-brand" : "border-slate-700 text-slate-500"} font-mono tracking-widest`}>
                         {t}
                     </div>
                 ))}
             </div>
             <div className="flex items-end gap-6 w-full h-[60%]">
                 <div className="flex-1 bg-brand h-[45%]" />
                 <div className="flex-1 bg-brand h-[80%]" />
                 <div className="flex-1 bg-brand h-[60%]" />
                 <div className="flex-1 bg-brand h-[95%]" />
                 <div className="flex-1 bg-brand h-[30%]" />
             </div>
             <div className="w-full h-px bg-slate-700 mt-6" />
          </motion.div>
          <motion.div variants={fadeUp} custom={0} className="order-1 lg:order-2">
            <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-navy-950 mb-8">Reconstruct.</h3>
            <p className="text-2xl text-slate-500 leading-relaxed font-light">
              Switch seamlessly between visualization types. The extracted data immediately populates an interactive, editable environment ready for export.
            </p>
          </motion.div>
        </motion.div>

        {/* 3. COMPLY */}
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="grid lg:grid-cols-[1fr_1.5fr] gap-24 items-center"
        >
          <motion.div variants={fadeUp} custom={0}>
            <h3 className="text-4xl md:text-5xl font-bold tracking-tight text-navy-950 mb-8">Comply.</h3>
            <p className="text-2xl text-slate-500 leading-relaxed font-light">
              Automatically calculate Structural Similarity (SSIM), chromatic overlap, and layout risk to ensure responsible academic reuse before you export.
            </p>
          </motion.div>
          <motion.div variants={scaleIn} className="w-full aspect-video bg-slate-50 border border-slate-200 p-12 flex items-center justify-center">
             <div className="relative w-64 h-64">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e2e8f0" strokeWidth="1.5" />
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#10b981" strokeWidth="1.5"
                      strokeDasharray="92 100" />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-6xl font-bold text-navy-950">92</span>
                    <span className="text-sm font-mono text-slate-400 mt-2 tracking-widest">SAFE TO USE</span>
                  </div>
              </div>
          </motion.div>
        </motion.div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 05: RESPONSIBLE REUSE (Elevated to its own section)
          ═══════════════════════════════════════════════════════════════════ */}
      <Section id="compliance" className="border-t border-navy-800 bg-navy-950">
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.3 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="text-center max-w-4xl mx-auto mb-24"
        >
          <motion.h2 variants={fadeUp} custom={0}
            className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-10"
          >
            Designed for Responsible Scientific Reuse.
          </motion.h2>
          <motion.p variants={fadeUp} custom={1}
            className="text-2xl text-slate-400 leading-relaxed font-light"
          >
            DECODE provides technical similarity metrics and workflow guidance;
            it does not constitute legal advice or guarantee copyright clearance.
          </motion.p>
        </motion.div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 06: FINAL CTA
          ═══════════════════════════════════════════════════════════════════ */}
      <Section className="bg-grid-dark relative flex items-center justify-center text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-navy-900/50 to-navy-900 pointer-events-none" />
        <motion.div
          initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.5 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
          className="relative z-10 max-w-5xl mx-auto"
        >
          <motion.h2 variants={fadeUp} custom={0}
            className="text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.1] mb-12"
          >
            Turn Research Figures<br />
            Into Usable Intelligence.
          </motion.h2>
          <motion.div variants={fadeUp} custom={1} className="flex flex-col sm:flex-row justify-center gap-8">
            <button
              onClick={() => router.push("/dashboard")}
              className="px-12 py-6 bg-white text-navy-950 font-bold text-xl hover:bg-slate-100 transition-all duration-300"
            >
              Launch DECODE
            </button>
          </motion.div>
        </motion.div>
      </Section>

      <footer className="bg-navy-950 border-t border-navy-800 py-16 px-6 md:px-12 lg:px-24 text-center">
        <div className="text-sm font-mono tracking-widest text-slate-500 mb-6">
            &copy; {new Date().getFullYear()} DECODE SCIENTIFIC PLATFORM
        </div>
        <div className="text-sm font-mono tracking-widest text-slate-600">
            BUILT BY MAYANK & VAIBHAV
        </div>
      </footer>

    </div>
  );
}
