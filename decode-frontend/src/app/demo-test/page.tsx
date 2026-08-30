"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DemoTestRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/demo");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#06100D] text-white">
      <div className="flex items-center gap-3 text-sm text-white/50">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/10 border-t-[#63F5A5]" />
        Opening DECODE workspace...
      </div>
    </div>
  );
}
