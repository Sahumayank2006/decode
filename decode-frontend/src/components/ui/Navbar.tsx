"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Montserrat } from "next/font/google";
import { Cpu, ArrowRight } from "lucide-react";
import { Button } from "./Button";

const montserrat = Montserrat({ subsets: ["latin"], weight: ["300", "400", "500", "700"] });

const NAV_ITEMS = [
  { label: "Overview", href: "#overview" },
  { label: "Pipeline", href: "#protocol" },
  { label: "Compliance", href: "#comply" },
  { label: "Access", href: "#access" },
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
      setScrolled(window.scrollY > 40);
      
      const scrollPos = window.scrollY + 300; 
      if (window.scrollY < 300) {
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
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pointer-events-none px-6 pt-6 md:pt-10">
      {/* Subtle atmospheric glow behind the navbar */}
      <div className={`absolute top-0 w-full max-w-[1800px] h-64 bg-cyan-500/10 blur-[120px] transition-opacity duration-1000 ${scrolled ? 'opacity-100' : 'opacity-0'}`} />
      
      <nav 
        className={`pointer-events-auto relative w-[98%] max-w-[1800px] rounded-[50px] transition-all duration-500 ease-out flex items-center justify-between ${
          scrolled
            ? isDark ? "py-6 px-10 md:px-16 bg-[#0B1E33]/80 backdrop-blur-xl border border-[#D8BE8E]/20 shadow-[0_16px_60px_rgb(0,0,0,0.4)]" 
                     : "py-8 px-12 md:px-20 bg-navy-950/70 backdrop-blur-xl border border-white/[0.08] shadow-[0_16px_60px_rgb(0,0,0,0.3)]"
            : "py-7 px-10 md:px-16 bg-[#0B1E33]/30 backdrop-blur-md border border-[#D8BE8E]/10"
        }`}
      >
        {/* Brand */}
        <div className="flex items-center gap-6">
           <div className="text-[#D8BE8E] flex items-center justify-center">
             <Cpu className="w-12 h-12 opacity-90" />
           </div>
           <div className="flex flex-col justify-center">
             <div className={`text-[39px] font-medium tracking-[0.04em] text-[#F7F4EC] leading-none ${montserrat.className}`}>
               DECODE
             </div>
             <div className="text-[14px] font-medium tracking-[0.14em] text-[#D8BE8E] mt-1.5 uppercase hidden sm:block font-mono">
               Data Extraction Protocol
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
              className="group relative px-6 py-2.5 rounded-2xl text-xl font-medium transition-colors duration-300 overflow-hidden"
            >
              {/* Active indicator */}
              {activeNav === item.label && (
                <motion.div 
                  layoutId="activeNav"
                  className="absolute bottom-0 left-[20%] right-[20%] h-[3px] bg-[#D8BE8E] shadow-[0_0_16px_rgba(216,190,142,0.6)]"
                />
              )}
              
              <span className={`relative z-10 transition-colors duration-300 ${
                activeNav === item.label ? "text-[#F7F4EC]" : "text-[#F7F4EC]/75 group-hover:text-[#F7F4EC]"
              }`}>
                {item.label}
              </span>
            </a>
          ))}
        </div>

        {/* Right side CTAs */}
        <div className="flex items-center gap-8">
          <button className="hidden md:block text-xl font-medium text-[#F7F4EC]/80 hover:text-[#F7F4EC] transition-colors">
            Sign In
          </button>
          <Button 
            variant="seal" 
            onClick={() => router.push("/dashboard")}
            className="text-lg px-8 py-4 rounded-xl"
          >
            Begin Verification
          </Button>
        </div>
      </nav>
    </div>
  );
}
