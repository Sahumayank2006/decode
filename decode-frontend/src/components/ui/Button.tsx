import React from "react";
import { ArrowRight } from "lucide-react";
import { twMerge } from "tailwind-merge";
import { clsx, type ClassValue } from "clsx";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "seal" | "ghost";
  withArrow?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", withArrow = false, children, ...props }, ref) => {
    
    if (variant === "seal") {
      return (
        <button
          ref={ref}
          className={cn(
            "relative isolate inline-flex items-center justify-center gap-2.5 rounded-sm border border-transparent font-mono text-[13px] font-medium tracking-[0.06em] uppercase text-[#0B1E33] px-[26px] py-[15px] cursor-pointer no-underline transition-all duration-300 ease-[cubic-bezier(0.2,1.4,0.4,1)]",
            "bg-gradient-to-b from-[#C9A86A] via-[#B08D57] via-[55%] to-[#9A7842]",
            "shadow-[inset_0_1px_0_rgba(255,255,255,0.4),0_8px_20px_-8px_rgba(176,141,87,0.65)]",
            "hover:-translate-y-0.5 hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.5),0_14px_26px_-10px_rgba(176,141,87,0.8)]",
            "active:translate-y-0",
            "after:absolute after:inset-0 after:rounded-sm after:border after:border-white/35 after:pointer-events-none",
            className
          )}
          {...props}
        >
          {children}
          {withArrow && <span>→</span>}
        </button>
      );
    }
    
    if (variant === "ghost") {
      return (
        <button
          ref={ref}
          className={cn(
            "inline-flex items-center justify-center gap-2.5 rounded-sm border border-[#D9D2BC] bg-transparent font-mono text-[13px] font-medium tracking-[0.06em] uppercase text-[#0B1E33] px-[26px] py-[15px] cursor-pointer transition-colors duration-200",
            "hover:border-[#1D4E89] hover:text-[#1D4E89]",
            "dark:text-[#F7F4EC] dark:border-[rgba(247,244,236,0.28)] dark:hover:border-[#D8BE8E] dark:hover:text-[#D8BE8E]",
            className
          )}
          {...props}
        >
          {children}
          {withArrow && <span>→</span>}
        </button>
      );
    }

    // Default: 'primary' (the old Get Started gradient button)
    return (
      <button
        ref={ref}
        className={cn(
          "group relative overflow-hidden rounded-2xl px-12 py-5 transition-all duration-300 hover:scale-[1.03] shadow-[0_0_30px_rgba(217,119,6,0.25)] hover:shadow-[0_0_50px_rgba(252,211,77,0.45)]",
          className
        )}
        {...props}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 via-yellow-300 to-yellow-500 bg-[length:200%_auto] transition-all duration-500 group-hover:bg-right" />
        <span className="relative z-10 flex items-center justify-center gap-4 text-lg font-bold uppercase tracking-wide text-navy-950">
          {children}
          {withArrow && (
            <ArrowRight className="h-6 w-6 transition-transform duration-300 group-hover:translate-x-1" />
          )}
        </span>
      </button>
    );
  }
);
Button.displayName = "Button";
