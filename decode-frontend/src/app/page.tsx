"use client";
import { useState, useEffect, useRef } from "react";

import { useRouter, usePathname } from "next/navigation";
import { motion, useInView } from "framer-motion";
import { Montserrat } from "next/font/google";
import {
  FileSearch, BarChart3, ShieldCheck, ArrowRight,
  Layers, Download, ScanLine, Cpu,
  Upload, ScanSearch, FileText, Layers3
} from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";

const montserrat = Montserrat({ subsets: ["latin"], weight: ["300", "400", "500", "700"] });

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
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [activeNav, setActiveNav] = useState("Home");

  // Scroll listener for navbar & active section spy
  useEffect(() => {
    const handler = () => {
      setScrolled(window.scrollY > 40);
      
      const scrollPos = window.scrollY + 300; // offset for better UX
      if (window.scrollY < 300) {
        setActiveNav("Home");
        return;
      }
      
      const sections = [
        { id: "platform", label: "Home" },
        { id: "pipeline", label: "How It Works" },
        { id: "capabilities", label: "Capabilities" },
        { id: "compliance", label: "Compliance" }
      ];
      
      for (const section of sections) {
        const el = document.getElementById(section.id);
        if (el && el.offsetTop <= scrollPos && el.offsetTop + el.offsetHeight > scrollPos) {
          setActiveNav(section.label);
        }
      }
    };
    window.addEventListener("scroll", handler, { passive: true });
    handler(); // initial check
    return () => window.removeEventListener("scroll", handler);
  }, []);

  const NAV_ITEMS = [
    { label: "Home", href: "/" },
    { label: "How It Works", href: "#pipeline" },
    { label: "Capabilities", href: "#capabilities" },
    { label: "Compliance", href: "#compliance" },
  ];

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
          PREMIUM GLASS NAVIGATION (DOUBLE SIZE)
          ═══════════════════════════════════════════════════════════════════ */}
      <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pointer-events-none px-4 pt-6 md:pt-10">
        {/* Subtle atmospheric glow behind the navbar */}
        <div className={`absolute top-0 w-full max-w-[1800px] h-64 bg-cyan-500/10 blur-[120px] transition-opacity duration-1000 ${scrolled ? 'opacity-100' : 'opacity-0'}`} />
        
        <nav 
          className={`pointer-events-auto relative w-[98%] max-w-[1800px] rounded-[40px] transition-all duration-500 ease-out flex items-center justify-between ${
            scrolled
              ? "py-8 px-10 md:px-16 bg-navy-950/70 backdrop-blur-xl border border-white/[0.08] shadow-[0_16px_60px_rgb(0,0,0,0.3)]"
              : "py-10 px-10 md:px-16 bg-navy-950/30 backdrop-blur-md border border-white/[0.04]"
          }`}
        >
          {/* Brand */}
          <div className="flex items-center gap-6">
             <div className="text-cyan-400 flex items-center justify-center">
               <Cpu className="w-12 h-12 opacity-90" />
             </div>
             <div className="flex flex-col justify-center">
               <div className={`text-[42px] font-light tracking-[0.3em] text-white leading-none ${montserrat.className}`}>
                 DECODE
               </div>
               <div className="text-[12px] font-semibold tracking-[0.25em] text-slate-400 mt-2.5 uppercase hidden sm:block">
                 Scientific Data Extraction Platform
               </div>
             </div>
          </div>

          {/* Nav Items */}
          <div className="hidden lg:flex items-center gap-8">
            {NAV_ITEMS.map(item => (
              <a 
                key={item.label}
                href={item.href}
                onClick={() => setActiveNav(item.label)}
                className="group relative px-8 py-4 rounded-xl text-xl font-medium transition-colors duration-300 overflow-hidden"
              >
                {/* Hover glass surface */}
                <div className="absolute inset-0 bg-cyan-400/0 group-hover:bg-cyan-400/10 transition-colors duration-300 rounded-xl" />
                
                {/* Scientific signal animation on hover */}
                <div className="absolute bottom-0 left-0 h-[2px] w-full bg-gradient-to-r from-transparent via-cyan-400 to-transparent -translate-x-[150%] group-hover:translate-x-[150%] transition-transform duration-700 ease-in-out" />
                
                {/* Active indicator */}
                {activeNav === item.label && (
                  <motion.div 
                    layoutId="activeNav"
                    className="absolute bottom-0 left-[20%] right-[20%] h-[3px] bg-cyan-400 shadow-[0_0_16px_rgba(34,211,238,0.6)]"
                  />
                )}
                
                <span className={`relative z-10 transition-colors duration-300 ${
                  activeNav === item.label ? "text-white" : "text-slate-400 group-hover:text-slate-200"
                }`}>
                  {item.label}
                </span>
              </a>
            ))}
          </div>

          {/* Right side CTAs */}
          <div className="flex items-center gap-12">
            <button className="hidden md:block text-xl font-medium text-slate-400 hover:text-white transition-colors">
              Sign In
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="group relative px-12 py-5 rounded-2xl overflow-hidden transition-all duration-300 hover:scale-[1.03] shadow-[0_0_30px_rgba(217,119,6,0.25)] hover:shadow-[0_0_50px_rgba(252,211,77,0.45)]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 via-yellow-300 to-yellow-500 bg-[length:200%_auto] group-hover:bg-right transition-all duration-500" />
              <span className="relative z-10 flex items-center gap-4 text-navy-950 font-bold text-lg tracking-wide uppercase">
                Get Started
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
              </span>
            </button>
          </div>
        </nav>
      </div>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 01: THE HERO — Massive scale
          ═══════════════════════════════════════════════════════════════════ */}
      <section 
        id="platform"
        className="relative w-full flex items-center justify-center overflow-hidden pt-[140px] md:pt-[180px]"
      >
        {/* Full Viewport Image adapting perfectly to its own aspect ratio */}
        <img 
          src="/1.png"
          alt="Hero Platform"
          className="w-full h-auto block pointer-events-none"
        />
        
        {/* Subtle Gradient Overlay to ensure the button is always visible */}
        <div className="absolute inset-0 bg-navy-900/10" />

        {/* Premium CTA Button Overlay */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
          className="absolute bottom-16 md:bottom-24 lg:bottom-40 z-10"
        >
          <motion.button
            onClick={() => router.push("/dashboard")}
            animate={{ 
              y: [0, -8, 0],
              boxShadow: [
                "0px 0px 50px rgba(217,119,6,0.4)",
                "0px 0px 90px rgba(252,211,77,0.7)",
                "0px 0px 50px rgba(217,119,6,0.4)"
              ]
            }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="group relative px-24 md:px-32 py-8 md:py-10 rounded-3xl overflow-hidden whitespace-nowrap"
          >
            {/* Premium Gold Gradient Fill */}
            <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 via-yellow-300 to-yellow-500" />
            
            {/* Hover Shine Sweep */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent -translate-x-[150%] group-hover:translate-x-[150%] transition-transform duration-700 ease-in-out" />
            
            {/* Button Content */}
            <span className="relative z-10 flex items-center justify-center gap-6 text-navy-950 font-bold text-3xl md:text-4xl tracking-widest uppercase">
              Start Decoding
              <ArrowRight className="w-10 h-10 md:w-12 md:h-12 text-navy-950 group-hover:translate-x-3 transition-transform duration-300" />
            </span>
          </motion.button>
        </motion.div>
      </section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 02: THE TRANSFORMATION
          ═══════════════════════════════════════════════════════════════════ */}
      <section 
        id="figure-to-intelligence"
        className="relative w-full flex items-center justify-center overflow-hidden bg-navy-950"
      >
        <img 
          src="/2.png"
          alt="Transformation Pipeline"
          className="w-full max-h-[85vh] object-cover object-center block pointer-events-none"
        />
        
        <div className="absolute inset-0 bg-navy-900/10 pointer-events-none" />
      </section>


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

        <div className="relative max-w-[1920px] px-6 lg:px-12 mx-auto mt-12 w-full">
          <GlowingEffectDemoSecond />
        </div>
      </Section>


      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 04: THE PRODUCT
          ═══════════════════════════════════════════════════════════════════ */}
      <section 
        id="capabilities"
        className="relative w-full flex items-center justify-center overflow-hidden"
      >
        <img 
          src="/3.png"
          alt="Precision at Every Stage"
          className="w-full h-auto block pointer-events-none"
        />
        
        <div className="absolute inset-0 bg-navy-900/10 pointer-events-none" />
      </section>

      {/* ═══════════════════════════════════════════════════════════════════
          EXPERIENCE 04-B: EXTENDED CAPABILITIES
          ═══════════════════════════════════════════════════════════════════ */}
      <section 
        className="relative w-full flex items-center justify-center overflow-hidden"
      >
        <img 
          src="/4.png"
          alt="Extended Capabilities"
          className="w-full h-auto block pointer-events-none"
        />
        
        <div className="absolute inset-0 bg-navy-900/10 pointer-events-none" />
      </section>




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

export function GlowingEffectDemoSecond() {
  return (
    <ul className="grid grid-cols-1 grid-rows-none gap-4 md:grid-cols-12 md:grid-rows-3 lg:gap-4 xl:max-h-[34rem] xl:grid-rows-2">

      {/* STEP 01 — INGEST */}
      <GridItem
        area="md:[grid-area:1/1/2/7] xl:[grid-area:1/1/2/5]"
        imageSrc="/card1.png"
      />

      {/* STEP 02 — DETECT */}
      <GridItem
        area="md:[grid-area:1/7/2/13] xl:[grid-area:2/1/3/5]"
        imageSrc="/card2.png"
      />

      {/* STEP 03 — EXTRACT */}
      <GridItem
        area="md:[grid-area:2/1/3/7] xl:[grid-area:1/5/3/8]"
        imageSrc="/card3.png"
      />

      {/* STEP 04 — RECONSTRUCT */}
      <GridItem
        area="md:[grid-area:2/7/3/13] xl:[grid-area:1/8/2/13]"
        imageSrc="/card4.png"
      />

      {/* STEP 05 — COMPLY */}
      <GridItem
        area="md:[grid-area:3/1/4/7] xl:[grid-area:2/8/3/10]"
        imageSrc="/card5.png"
      />

      {/* STEP 06 — EXPORT */}
      <GridItem
        area="md:[grid-area:3/7/4/13] xl:[grid-area:2/10/3/13]"
        imageSrc="/card6.png"
      />

    </ul>
  );
}

const GridItem = ({
  area,
  imageSrc,
}: any) => {
  return (
    <li className={`min-h-[14rem] list-none ${area}`}>
      <div className="relative h-full rounded-2xl border border-white/5 p-2 md:rounded-3xl md:p-3">
        <GlowingEffect
          spread={60}
          glow={true}
          disabled={false}
          proximity={64}
          inactiveZone={0.01}
        />
        <div className="border-0.75 relative flex h-full flex-col justify-center items-center overflow-hidden rounded-xl bg-navy-950/20 dark:shadow-[0px_0px_27px_0px_#2D2D2D]">
          <img 
            src={imageSrc} 
            alt="Pipeline Stage" 
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </li>
  );
};
