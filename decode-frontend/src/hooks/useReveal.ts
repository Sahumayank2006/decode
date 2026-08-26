"use client";

import { useEffect } from "react";

/**
 * useReveal
 * 
 * Attaches IntersectionObserver to elements with the '.reveal' class.
 * It adds '.reveal-armed' to hide them initially, and then '.in' when they scroll into view.
 * This ensures content is visible by default (progressive enhancement) and only hidden 
 * if JavaScript and IntersectionObserver are actually supported and running.
 */
export function useReveal() {
  useEffect(() => {
    if (typeof window === "undefined" || !("IntersectionObserver" in window)) {
      return;
    }

    const revealEls = document.querySelectorAll(".reveal");
    
    // Arm them (hide them)
    revealEls.forEach((el) => {
      el.classList.add("reveal-armed");
    });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            observer.unobserve(e.target);
          }
        });
      },
      { threshold: 0.15 }
    );

    revealEls.forEach((el) => observer.observe(el));

    return () => {
      observer.disconnect();
    };
  }, []);
}
