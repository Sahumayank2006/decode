"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Montserrat } from "next/font/google";
import { Cpu, ArrowRight } from "lucide-react";

const montserrat = Montserrat({ subsets: ["latin"], weight: ["300", "400", "500", "700"] });

const NAV_ITEMS = [
  { label: "Overview", href: "#overview" },
  { label: "Pipeline", href: "#protocol" },
  { label: "Compliance", href: "#comply" },
  { label: "Access", href: "#access" },
  { label: "Live Demo", href: "/demo" },
];

interface NavbarProps {
  variant?: "default" | "dark";
}

export function Navbar({ variant = "default" }: NavbarProps) {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);
  const [activeNav, setActiveNav] = useState("Overview");

  // Scroll listener for navbar & active section spy
  useEffect(() => {
    const handler = () => {
      setScrolled(window.scrollY > 30);
      
      const scrollPos = window.scrollY + 250; 
      if (window.scrollY < 250) {
        setActiveNav("Overview");
        return;
      }
      
      const sections = [
        { id: "overview", label: "Overview" },
        { id: "protocol", label: "Pipeline" },
        { id: "comply", label: "Compliance" },
        { id: "access", label: "Access" }
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

  // Use variant="dark" for the landing page where the background is very dark.
  const isDark = variant === "dark";

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pointer-events-none px-4 pt-3 md:pt-4">
      {/* Subtle atmospheric glow behind the navbar */}
      <div className={`absolute top-0 w-full max-w-[1240px] h-28 bg-cyan-500/10 blur-[80px] transition-opacity duration-700 ${scrolled ? 'opacity-100' : 'opacity-0'}`} />
      
      <nav 
        className={`pointer-events-auto relative w-full max-w-[1240px] rounded-full transition-all duration-400 ease-out flex items-center justify-between ${
          scrolled
            ? isDark ? "py-2 px-5 md:px-7 bg-[#0B1E33]/90 backdrop-blur-xl border border-[#D8BE8E]/25 shadow-[0_12px_40px_rgba(0,0,0,0.5)]" 
                     : "py-2 px-5 md:px-7 bg-navy-950/85 backdrop-blur-xl border border-white/[0.12] shadow-[0_12px_40px_rgba(0,0,0,0.4)]"
            : "py-2.5 px-5 md:px-7 bg-[#0B1E33]/45 backdrop-blur-md border border-[#D8BE8E]/15"
        }`}
      >
        {/* Brand */}
        <a href="#overview" className="flex items-center gap-3 group cursor-pointer no-underline">
          <div className="text-[#D8BE8E] flex items-center justify-center p-1 rounded-lg bg-[#D8BE8E]/10 border border-[#D8BE8E]/20 transition-transform duration-300 group-hover:scale-105">
            <Cpu className="w-5 h-5 md:w-5.5 md:h-5.5 opacity-95" />
          </div>
          <div className="flex flex-col justify-center">
            <div className={`text-lg md:text-xl font-bold tracking-[0.06em] text-[#F7F4EC] leading-none ${montserrat.className}`}>
              DECODE
            </div>
            <div className="text-[9px] md:text-[10px] font-medium tracking-[0.16em] text-[#D8BE8E] mt-0.5 uppercase hidden sm:block font-mono leading-none">
              Data Extraction Protocol
            </div>
          </div>
        </a>

        {/* Nav Items */}
        <div className="hidden lg:flex items-center gap-1.5 md:gap-2 bg-white/[0.03] px-2 py-1 rounded-full border border-white/[0.06]">
          {NAV_ITEMS.map(item => (
            <a 
              key={item.label}
              href={item.href}
              onClick={() => setActiveNav(item.label)}
              className={`group relative px-3.5 py-1.5 rounded-full text-xs md:text-sm font-medium transition-all duration-200 ${
                activeNav === item.label ? "text-[#F7F4EC]" : "text-[#F7F4EC]/70 hover:text-[#F7F4EC]"
              }`}
            >
              {/* Active indicator */}
              {activeNav === item.label && (
                <motion.div 
                  layoutId="activeNav"
                  className="absolute inset-0 rounded-full bg-white/[0.08] border border-[#D8BE8E]/30"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              
              <span className="relative z-10">
                {item.label}
              </span>
            </a>
          ))}
        </div>

        {/* Right side CTAs */}
        <div className="flex items-center gap-4 md:gap-5">
          <button 
            onClick={() => router.push("/demo")}
            className="hidden sm:block text-xs md:text-sm font-medium text-[#F7F4EC]/75 hover:text-[#F7F4EC] transition-colors"
          >
            Sign In
          </button>
          
          <a
            href="/demo"
            className="group relative overflow-hidden rounded-full bg-gradient-to-r from-[#DFB76C] via-[#FCEABB] via-50% to-[#C39738] px-4 py-1.5 md:px-5 md:py-2 text-xs md:text-sm font-bold uppercase tracking-wide text-[#0B1E33] shadow-[0_0_16px_rgba(223,183,108,0.35)] transition-all duration-300 hover:scale-105 hover:shadow-[0_0_24px_rgba(252,234,187,0.6)] active:scale-95 flex items-center gap-1.5"
          >
            <span className="relative z-10 flex items-center gap-1.5">
              Try DECODE
              <ArrowRight size={13} className="transition-transform duration-200 group-hover:translate-x-0.5" />
            </span>
            <div className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/50 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
          </a>
        </div>
      </nav>
    </div>
  );
}
