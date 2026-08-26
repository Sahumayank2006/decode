"use client";

import { useRouter } from "next/navigation";
import Image from "next/image";

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
          className="object-cover object-center w-full h-full opacity-90"
        />
        {/* Optional overlay to make the button stand out more if the image is bright */}
        <div className="absolute inset-0 bg-black/10" />
      </div>
      
      {/* Premium Large Golden CTA Button (Slightly Reduced, Positioned Higher) */}
      <div className="relative z-10 w-full flex justify-center px-4">
        <button
          onClick={() => router.push("/dashboard")}
          className="
            relative isolate inline-flex items-center justify-center gap-5
            rounded-xl border border-transparent 
            font-mono text-2xl md:text-[40px] font-bold tracking-[0.1em] uppercase text-[#0B1E33] 
            px-12 py-6 md:px-24 md:py-10
            cursor-pointer no-underline 
            transition-all duration-500 ease-[cubic-bezier(0.2,1.4,0.4,1)]
            bg-gradient-to-b from-[#E5C989] via-[#C9A86A] to-[#9A7842]
            shadow-[inset_0_4px_0_rgba(255,255,255,0.6),0_24px_80px_-20px_rgba(201,168,106,1)]
            hover:-translate-y-2 hover:scale-[1.02] hover:shadow-[inset_0_4px_0_rgba(255,255,255,0.8),0_30px_100px_-20px_rgba(201,168,106,1)]
            active:translate-y-0 active:scale-95
            after:absolute after:inset-0 after:rounded-xl after:border-[3px] after:border-white/40 after:pointer-events-none
          "
        >
          Begin Verification →
        </button>
      </div>
    </section>
  );
}
